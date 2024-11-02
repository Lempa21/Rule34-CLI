from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rule34-cli",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "click",
        "requests",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "rule34=rule34_cli.__main__:main",
        ],
    },
   author="Lempa",
    author_email="mempa1peu@gmail.com",
    description="A command-line tool for searching images from rule34.xxx",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lempa21/Rule34-CLI",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Licence appropriée
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
