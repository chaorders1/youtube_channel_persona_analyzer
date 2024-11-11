"""YouTube Channel Persona Analyzer

This module provides functionality to analyze YouTube channel content and generate
comprehensive persona reports using the Claude API. It processes channel screenshots
and content to extract key insights about the channel's brand, audience, and content strategy.

Example Usage:
    # Basic usage with directory of channel screenshots
    analyzer = PersonaAnalyzer()
    analysis = analyzer.analyze_channel('data/crop_veritasium_20241106_124941')
    
    # Command line usage:
    python persona.py /path/to/cropped/screenshots
    
    # Pipeline integration:
    pipeline = PersonaPipeline()
    pipeline.process_channel('https://youtube.com/@veritasium')

Features:
    - Comprehensive channel analysis including:
        - Basic channel metrics and classification
        - Brand essence and presentation style
        - Content strategy and themes
        - Audience analysis and engagement patterns
    - Support for multiple image formats
    - Intelligent text extraction and processing
    - Integration with Claude API for analysis
    - Structured markdown report generation
    - Robust error handling and logging

Output Structure:
    data/
    └── crop_{channel}_{timestamp}_analysis.md
    Example: crop_veritasium_20241106_124941_analysis.md

Technical Details:
    - Uses Claude API for intelligent content analysis
    - Supports multiple file formats:
        - Images: jpg, jpeg, png
        - Text: txt, csv, json, html, pdf, docx, etc.
    - Implements base64 encoding for API communication
    - Provides structured analysis framework
    - Generates markdown-formatted reports

Requirements:
    - Python 3.8+
    - anthropic (Claude API client)
    - python-dotenv (environment management)
    - Various text processing libraries:
        - PyPDF2
        - python-docx
        - html2text
        - ebooklib
    
Configuration:
    - Claude API key should be set in .env as ANTHROPIC_API_KEY
    - Configurable through class initialization
    - Supports custom prompt templates
    - Logging configuration available
"""

"""
Module for analyzing YouTube channel personas using Claude API.
python persona.py /Users/yuanlu/Code/youtube_copilot/data/crop_anthropic_youtube_chanel
python persona.py /Users/yuanlu/Code/youtube_copilot/data/crop_openai_youtube_chanel
python persona.py /Users/yuanlu/Code/youtube_copilot/data/crop_veritasium_20241106_124941
"""
import os
import base64
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import logging
from anthropic import Anthropic
import PyPDF2
import docx
import csv
import json
import html2text
import ebooklib
from ebooklib import epub
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PersonaAnalyzer:
    """
    A class to analyze YouTube channel personas using Claude API.
    """
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png'}
    SUPPORTED_TEXT_FORMATS = {
        '.txt', '.csv', '.json', '.html', '.htm',
        '.pdf', '.docx', '.odt', '.rtf', '.epub'
    }

    # Define prompt template directly in code
    PROMPT_TEMPLATE = """
    You will be analyzing screenshots of a YouTube channel to provide insights and recommendations for a content creator. The screenshots contain information about the channel's videos, metrics, and other relevant data. Here are the screenshots:

    <screenshots>
    {{SCREENSHOTS}}
    </screenshots>

    Your task is to generate an artifact in markdown format following a specific framework. The framework is divided into three parts: Classification & Metrics, Creator Analysis, and Content Analysis. You should analyze the information in the screenshots and provide detailed insights for each section.

    For PART 1: CLASSIFICATION & METRICS, follow these steps:

    1. Extract and list the basic channel data, including:
        - Channel name and subscriber count
        - Top 10 performing videos ranked by view count
        - Themes of the top 5 performing videos and the deeper audience desires they reveal
    2. Classify the channel by:
        - Identifying the primary category in one of the following (Personality/Entertainment Driven, Professional/Educational/Corporate, or Curated/Aggregate)
        - Determining the area of interest (e.g., Food, Travel, Technology)
        - Identifying the subculture or niche
        - Noting whether the creator shows their face

    For PART 2: CREATOR ANALYSIS, choose the relevant framework based on the channel classification:

    - For Personality/Entertainment channels, analyze the Creator Essence with particular attention to cultural resonance, audience connection, and authentic storytelling elements
        - Linguistic style (e.g., humorous, serious, warm, thoughtful) + use of regional or subculture slang / emojis / catchphrases if any
        - Quote examples from video titles (DOUBLE CHECK FOR ACCURACY)
        - Distinguishing demographic or cultural characteristics if any shown
        - Personal Values (50 words) including core beliefs demonstrated, what they stand for, life philosophy
        - Key Life Events & Journey ONLY IF SHOWN: Origin story + Major transitions + Career changes + Location moves + Significant milestones + Current situation
        - Aesthetics: Briefly describe color schemes, composition methods, and style preferences.
    - For Professional/Educational channels, analyze the Brand Essence, with particular attention to brand positioning, authority, subcultural or local resonance, audience connection
        - Brand mission / corporate identity
        - Expertise demonstration / credibility markers
        - Presentation style, SPECIAL NOTE if this professional channels shows humor or emotion to connect audience with brand
        - Target audience location, demographic, or culture or subculture / niche characteristics
        - Value proposition clarity
    - For Curated channels, analyze the Curation Effectiveness with particular attention to theme and flow, subcultural or local resonance, audience connection
        - Content selection criteria
        - Value addition methods
        - Source management
        - Theme consistency
        - Community building

    For PART 3: CONTENT ANALYSIS, complete the following for ALL channels:

    1. Analyze the Content Strategy, including:
        - Overall impression of brand personality or image or theme
        - Most successful formats and themes
        - Title/thumbnail patterns
        - Upload frequency
        - List of 5 key phrases to find similar accounts
    2. Provide a Brief Summary (300 words) covering:
        - Key success factors and audience pain points/aspirations
        - Primary strengths
        - Growth opportunities
        - Unique value proposition

    When writing your analysis:

    - Use vivid, descriptive, and easy-to-understand language
    - Strictly follow the framework structure and maintain consistent formatting
    - Include examples and quotes from the screenshots where relevant
    - Pay attention to cultural resonance, audience connection, and authentic storytelling elements
    - Double-check number counts and ensure accuracy when quoting video titles

    Format your output in markdown, using appropriate headers, bullet points, and emphasis where needed. Begin your response with "## PART 1: CLASSIFICATION & METRICS" and continue with the subsequent parts as outlined in the framework.

    Do not include any additional output or explanations outside of the requested artifact.

    """

    def __init__(self):
        """Initialize the analyzer with API client."""
        # 确保环境变量已加载
        load_dotenv()
        
        # 获取 API 密钥并验证
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            
        # 打印部分密钥用于调试（只显示前几个字符）
        logger.info(f"API key loaded: {api_key[:8]}...")
        
        try:
            # 初始化 Anthropic 客户端
            self.client = Anthropic(
                api_key=api_key
            )
        except Exception as e:
            logger.error(f"Error initializing Anthropic client: {e}")
            raise
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True

    def _encode_image(self, image_path: Path) -> Dict:
        """Encode an image file to base64."""
        try:
            with open(image_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                logger.info(f"Successfully encoded image: {image_path.name}")
                return {
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': f'image/{image_path.suffix[1:]}',
                        'data': base64_image
                    }
                }
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {str(e)}")
            raise

    def _extract_text_content(self, file_path: Path) -> str:
        """
        Extract text content from various file formats.

        Args:
            file_path (Path): Path to the file

        Returns:
            str: Extracted text content
        """
        suffix = file_path.suffix.lower()
        try:
            if suffix == '.txt' or suffix == '.rtf':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()

            elif suffix == '.pdf':
                text = []
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text.append(page.extract_text())
                return '\n'.join(text)

            elif suffix == '.docx':
                doc = docx.Document(file_path)
                return '\n'.join(paragraph.text for paragraph in doc.paragraphs)

            elif suffix == '.csv':
                text = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    csv_reader = csv.reader(f)
                    for row in csv_reader:
                        text.append(','.join(row))
                return '\n'.join(text)

            elif suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.dumps(json.load(f), indent=2)

            elif suffix in {'.html', '.htm'}:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return self.html_converter.handle(f.read())

            elif suffix == '.epub':
                book = epub.read_epub(file_path)
                text = []
                for item in book.get_items():
                    if item.get_type() == ebooklib.ITEM_DOCUMENT:
                        text.append(self.html_converter.handle(item.get_content().decode('utf-8')))
                return '\n'.join(text)

            elif suffix == '.odt':
                # For ODT files, you might need to implement specific handling
                # or use a library like odfpy
                logger.warning(f"ODT support is limited: {file_path}")
                return f"[Content from ODT file: {file_path.name}]"

            else:
                logger.warning(f"Unsupported file format: {suffix}")
                return f"[Unsupported file format: {file_path.name}]"

        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return f"[Error extracting content from: {file_path.name}]"

    def _process_files(self, folder_path: Path) -> Tuple[List[Dict], str]:
        """
        Process all supported files in the folder.

        Args:
            folder_path (Path): Path to the folder containing files

        Returns:
            Tuple[List[Dict], str]: Tuple of (image contents, text contents)
        """
        image_contents = []
        text_contents = []

        for file_path in folder_path.iterdir():
            suffix = file_path.suffix.lower()
            
            if suffix in self.SUPPORTED_IMAGE_FORMATS:
                logger.info(f"Processing image: {file_path.name}")
                image_contents.append(self._encode_image(file_path))
            
            elif suffix in self.SUPPORTED_TEXT_FORMATS:
                logger.info(f"Processing text file: {file_path.name}")
                content = self._extract_text_content(file_path)
                text_contents.append(f"\n=== Content from {file_path.name} ===\n{content}\n")

        return image_contents, '\n'.join(text_contents)

    def analyze_channel(self, images_folder: str | Path) -> str:
        """
        Analyze YouTube channel using files from specified folder.

        Args:
            images_folder (str | Path): Path to folder containing channel data

        Returns:
            str: Analysis results from Claude
        """
        folder_path = Path(images_folder).resolve()
        logger.info(f"Analyzing channel from folder: {folder_path}")
        
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        # Process all files
        image_contents, text_contents = self._process_files(folder_path)

        if not image_contents and not text_contents:
            raise ValueError(f"No supported files found in {folder_path}")

        # Prepare message content
        message_content = image_contents + [{
            'type': 'text',
            'text': f"Please analyze this YouTube channel based on the following content:\n\n{text_contents}\n\n{self.PROMPT_TEMPLATE}"
        }]

        try:
            # Create message using Claude API
            logger.info("Sending request to Claude API...")
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=5000,
                temperature=0.5,
                messages=[
                    {'role': 'user', 'content': message_content},
                    {'role': 'assistant', 'content': '# YouTube Channel Analysis Report'}
                ]
            )
            logger.info("Received response from Claude API")
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Analyze YouTube channel content from screenshots.'
    )
    parser.add_argument(
        'images_folder',
        type=str,
        help='Path to folder containing channel screenshots'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Path to save analysis results (default: <images_folder>_analysis.md)',
        default=None
    )
    return parser.parse_args()

def main():
    """Main function to demonstrate usage."""
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Initialize analyzer (API key from environment variable)
        analyzer = PersonaAnalyzer()
        
        # Analyze channel from specified folder
        result = analyzer.analyze_channel(args.images_folder)
        
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            # Create output next to input folder with timestamp
            input_path = Path(args.images_folder)
            output_path = input_path.parent / f"{input_path.name}_analysis.md"
        
        # Save results to markdown file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result, encoding='utf-8')
        logger.info(f'Analysis results saved to {output_path}')
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == '__main__':
    main()