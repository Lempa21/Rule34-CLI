import requests
import xml.etree.ElementTree as ET
import argparse
import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text

console = Console()

def create_fancy_header():
    header_text = Text()
    header_text.append("Rule34-CLI ", style="bold cyan")
    console.print(Panel(header_text, style="cyan"))

def process_keyword(keyword):
    """Converts the keyword to lowercase and replaces spaces with underscores"""
    return keyword.lower().replace(" ", "_")

def search_rule34_api(keyword, num_images):
    keyword = process_keyword(keyword)
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&tags={keyword}"
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Searching for '{keyword}'...", total=None)
        
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Search error for '{keyword}': {e}")
            return []
        
        progress.update(task, completed=50)
        
        root = ET.fromstring(response.content)
        image_urls = []
        
        for post in root.findall('post'):
            if len(image_urls) >= num_images:
                break
            image_url = post.get('file_url')
            if image_url:
                image_urls.append((keyword, image_url))
                
        progress.update(task, completed=100)
        
    return image_urls

def get_keywords_from_file(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"[red]File '{filename}' does not exist.")
    
    with console.status(f"[cyan]Reading file {filename}...", spinner="dots"):
        with open(filename, 'r') as file:
            keywords = [process_keyword(line.strip()) for line in file if line.strip()]
    
    if not keywords:
        raise ValueError("Le fichier est vide")
        
    console.print(f"[green]Loaded {len(keywords)} keywords from file")
    return keywords

def save_urls_to_file(urls, filename_prefix="urls"):
    output_file = f"{filename_prefix}_combined.txt"
    
    if os.path.exists(output_file):
        if not Confirm.ask(f"File [bold]{output_file}[/bold] already exists. Do you want to overwrite it?"):
            while True:
                output_file = Prompt.ask("Enter a new filename")
                if not os.path.exists(output_file):
                    break
                if Confirm.ask(f"File [bold]{output_file}[/bold] already exists. Do you want to overwrite it?"):
                    break
    
    with open(output_file, 'w') as f:
        for keyword, url in urls:
            f.write(f"{keyword}: {url}\n")
    
    console.print(f"[green]URLs have been saved to file: [bold]{output_file}[/bold]")

def distribute_image_count(num_keywords, total_images):
    """Distributes the number of images per keyword evenly"""
    base_count = total_images // num_keywords
    remainder = total_images % num_keywords
    
    distribution = [base_count] * num_keywords
    for i in range(remainder):
        distribution[i] += 1
    
    return distribution

def search_multiple_keywords(keywords, total_images):
    distributions = distribute_image_count(len(keywords), total_images)
    all_urls = []
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Searching all keywords...", total=len(keywords))
        
        for keyword, num_images in zip(keywords, distributions):
            urls = search_rule34_api(keyword, num_images)
            all_urls.extend(urls)
            progress.advance(task)
    
    return all_urls

def display_results(urls):
    if not urls:
        console.print(Panel(
            "[yellow]No images found 😕",
            title="Results",
            border_style="yellow"
        ))
        return

    console.print("\n[cyan]Images found:")
    
    current_keyword = None
    for idx, (keyword, url) in enumerate(urls, 1):
        if keyword != current_keyword:
            console.print(f"\n[bold magenta]Keyword: {keyword}[/bold magenta]")
            current_keyword = keyword
        console.print(f"[bold cyan]{idx}.[/bold cyan] {url}")
    
    if Confirm.ask("\nDo you want to save the URLs to a file?"):
        save_urls_to_file(urls)

def main():
    create_fancy_header()
    
    parser = argparse.ArgumentParser(description="Search for images on Rule 34.")
    parser.add_argument('-k', '--keyword', type=str, help="Keyword to search for.")
    parser.add_argument('-f', '--file', type=str, help="File containing the keywords.")
    parser.add_argument('-n', '--num_images', type=int, help="Total number of images to retrieve.")

    args = parser.parse_args()

    num_images = args.num_images

    try:
        if not args.keyword and not args.file:
            if Confirm.ask("Do you want to use a file for keywords?"):
                filename = Prompt.ask("Enter the filename", default="keywords.txt")
                try:
                    keywords = get_keywords_from_file(filename)
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}")
                    return
            else:
                keywords = [process_keyword(Prompt.ask("Enter the keyword you want to search for"))]
        elif args.file:
            try:
                keywords = get_keywords_from_file(args.file)
            except Exception as e:
                console.print(f"[red]Error: {str(e)}")
                return
        else:
            keywords = [process_keyword(args.keyword)]

        if num_images is None:
            num_images = int(Prompt.ask("How many images do you want in total?", default="5"))

        urls = search_multiple_keywords(keywords, num_images)
        display_results(urls)

    except KeyboardInterrupt:
        console.print("\n[yellow]Search cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]An unexpected error occurred: {str(e)}[/red]")

if __name__ == "__main__":
    main()
