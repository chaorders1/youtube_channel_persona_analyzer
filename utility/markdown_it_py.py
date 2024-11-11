#!/usr/bin/env python3
"""
Markdown to HTML converter using markdown-it-py.

This script converts markdown files to HTML format using the markdown-it-py library.
It takes input and output file paths as command line arguments.

Usage:
    python markdown_it_py.py <input_markdown_file> <output_html_file>

Example:
    python markdown_it_py.py input.md output.html
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from markdown_it import MarkdownIt
from rich.logging import RichHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)


def setup_argparse() -> argparse.Namespace:
    """
    Set up command line argument parsing.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Convert markdown to HTML using markdown-it-py'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to input markdown file'
    )
    parser.add_argument(
        'output_file',
        type=str,
        help='Path to output HTML file'
    )
    return parser.parse_args()


def read_markdown_file(file_path: str) -> Optional[str]:
    """
    Read content from a markdown file.

    Args:
        file_path (str): Path to the markdown file

    Returns:
        Optional[str]: Content of the markdown file or None if file doesn't exist
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f'Input file not found: {file_path}')
        return None
    except Exception as e:
        logger.error(f'Error reading file: {e}')
        return None


def convert_markdown_to_html(markdown_content: str) -> str:
    """
    Convert markdown content to HTML with enhanced features.

    Args:
        markdown_content (str): Markdown content to convert

    Returns:
        str: Converted HTML content with enhanced formatting
    """
    md = MarkdownIt('commonmark', {
        'html': True,           # Enable HTML tags in source
        'linkify': True,        # Autoconvert URL-like text to links
        'typographer': True,    # Enable smartquotes and other typographic replacements
        'breaks': True,         # Convert \n in paragraphs into <br>
        'langPrefix': 'language-'  # CSS language prefix for fenced blocks
    })

    # You could add syntax highlighting here if needed:
    # md.options['highlight'] = your_highlight_function

    return md.render(markdown_content)


def write_html_file(content: str, file_path: str) -> bool:
    """
    Write HTML content to a file.

    Args:
        content (str): HTML content to write
        file_path (str): Path to output file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f'Error writing output file: {e}')
        return False


def main() -> None:
    """
    Main function to handle markdown to HTML conversion.
    """
    args = setup_argparse()
    
    markdown_content = read_markdown_file(args.input_file)
    if markdown_content is None:
        return

    html_content = convert_markdown_to_html(markdown_content)
    
    if write_html_file(html_content, args.output_file):
        logger.info(f'Successfully converted {args.input_file} to {args.output_file}')
    else:
        logger.error('Failed to write output file')


if __name__ == '__main__':
    main()