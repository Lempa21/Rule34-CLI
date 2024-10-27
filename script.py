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
    header_text.append("Random34 ", style="bold cyan")
    console.print(Panel(header_text, style="cyan"))

def search_rule34_api(keyword, num_images):
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
            console.print(f"[red]Search error: {e}")
            return []
        
        progress.update(task, completed=50)
        
        root = ET.fromstring(response.content)
        image_urls = []
        
        for post in root.findall('post'):
            if len(image_urls) >= num_images:
                break
            image_url = post.get('file_url')
            if image_url:
                image_urls.append(image_url)
                
        progress.update(task, completed=100)
        
    return image_urls

def get_keyword_from_file(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"[red]File '{filename}' does not exist.")
    
    with console.status(f"[cyan]Reading file {filename}...", spinner="dots"):
        with open(filename, 'r') as file:
            keyword = file.readline().strip()
    
    return keyword

def save_urls_to_file(urls, keyword):
    output_file = f"urls_{keyword}.txt"
    
    if os.path.exists(output_file):
        if not Confirm.ask(f"File [bold]{output_file}[/bold] already exists. Do you want to overwrite it?"):
            while True:
                output_file = Prompt.ask("Enter a new filename")
                if not os.path.exists(output_file):
                    break
                if Confirm.ask(f"File [bold]{output_file}[/bold] already exists. Do you want to overwrite it?"):
                    break
    
    with open(output_file, 'w') as f:
        f.write("\n".join(urls))
    
    console.print(f"[green]URLs have been saved to file: [bold]{output_file}[/bold]")

def display_results(keyword, urls):
    if not urls:
        console.print(Panel(
            f"[yellow]No images found for '[bold]{keyword}[/bold]' 😕",
            title="Results",
            border_style="yellow"
        ))
        return

    console.print(f"\n[cyan]Images found for '[bold]{keyword}[/bold]':")
    
    for idx, url in enumerate(urls, 1):
        console.print(f"[bold cyan]{idx}.[/bold cyan] {url}")
    
    if Confirm.ask("\nDo you want to save the URLs to a file?"):
        save_urls_to_file(urls, keyword)

def main():
    create_fancy_header()
    
    parser = argparse.ArgumentParser(description="Search for images on Rule 34.")
    parser.add_argument('-k', '--keyword', type=str, help="Keyword to search for.")
    parser.add_argument('-f', '--file', type=str, help="File containing the keyword.")
    parser.add_argument('-n', '--num_images', type=int, help="Number of images to retrieve.")

    args = parser.parse_args()

    keyword = args.keyword
    num_images = args.num_images

    try:
        if not keyword and not args.file:
            if Confirm.ask("Do you want to use a file for the keyword?"):
                filename = Prompt.ask("Enter the filename", default="keywords.txt")
                try:
                    keyword = get_keyword_from_file(filename)
                    console.print(f"[green]Keyword loaded: [bold]{keyword}[/bold]")
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}")
                    return
            else:
                keyword = Prompt.ask("Enter the keyword you want to search for")
        elif args.file:
            try:
                keyword = get_keyword_from_file(args.file)
                console.print(f"[green]Keyword loaded: [bold]{keyword}[/bold]")
            except Exception as e:
                console.print(f"[red]Error: {str(e)}")
                return

        if num_images is None:
            num_images = int(Prompt.ask("How many images do you want?", default="5"))

        urls = search_rule34_api(keyword, num_images)
        display_results(keyword, urls)

    except KeyboardInterrupt:
        console.print("\n[yellow]Search cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]An unexpected error occurred: {str(e)}[/red]")

if __name__ == "__main__":
    main()