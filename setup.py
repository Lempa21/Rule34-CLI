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
    author="Ton Nom",
    description="Un CLI pour rechercher des éléments sur Rule34",
    long_description="long_description",
    long_description_content_type="text/markdown",
)
