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
    You are an expert in YouTube content creation and an advisor to the content creator shown in the following screenshots. Your task is to analyze these screenshots and generate a comprehensive report in markdown format. Here are the screenshots:

    <screenshots>
    {{SCREENSHOTS}}
    </screenshots>

    Carefully examine these screenshots and use the information they contain to complete the following framework. Your language should be vivid, descriptive, and easy to understand. Please strictly follow the framework structure and maintain consistent formatting throughout your report.

    Your report should be divided into three main parts:

    PART 1: CLASSIFICATION & METRICS
    In this section, complete the following steps:

    1. Basic Channel Data
       - Identify the channel name and subscriber count
       - List the top 10 performing videos shown, ranked by exact views
       - Calculate the average views across these videos
       - Note the themes of the top 5 performing videos and analyze what deeper audience desires these reveal

    2. Channel Classification
       - Identify the primary category of the channel:
         a) Personality/Entertainment Driven
         b) Professional/Educational
         c) Curated/Aggregate
       - Identify the main area of interest (e.g., Food, Travel, Technology, Fashion, Education, Relationships, Gaming)
       - Identify the specific subculture or niche (e.g., Practical Italian recipes)
       - Note whether the creator shows their own face in the content

    PART 2: CATEGORY-SPECIFIC ANALYSIS
    Based on your classification in Part 1, follow the relevant framework:

    FOR PERSONALITY/ENTERTAINMENT CHANNELS ONLY:
    Analyze the Creator Essence, paying particular attention to cultural resonance, audience connection, and authentic storytelling elements. Include:
    - Linguistic style (e.g., humorous, serious, warm, thoughtful)
    - Use of regional or subculture slang / emojis / catchphrases if any
    - Quote examples from video titles (double check for accuracy)
    - Distinguishing demographic or cultural characteristics if shown
    - Personal Values (in about 50 words) including core beliefs demonstrated, what they stand for, life philosophy
    - Key Life Events & Journey ONLY IF SHOWN: Origin story, major transitions, career changes, location moves, significant milestones, current situation
    - Aesthetics: Briefly describe color schemes, composition methods, and style preferences

    FOR PROFESSIONAL/EDUCATIONAL CHANNELS ONLY:
    Analyze the Brand Essence, paying particular attention to brand positioning, authority, subcultural or local resonance, and audience connection. Include:
    - Expertise demonstration
    - Presentation style
    - Brand mission / corporate identity
    - Target location, demographic or culture characteristics
    - Value proposition clarity
    - Credibility markers

    FOR CURATED CHANNELS ONLY:
    Analyze the Curation Effectiveness, paying particular attention to theme and flow, subcultural or local resonance, and audience connection. Include:
    - Content selection criteria
    - Value addition methods
    - Source management
    - Theme consistency
    - Community building

    PART 3: UNIVERSAL ANALYSIS
    Complete this section for all channels:

    1. Content Strategy
       - Overall impression of brand personality (about 100 words, can include examples and quotes)
       - Most successful formats and themes
       - Title/thumbnail patterns
       - Upload frequency
       - List of 5 key phrases to find similar accounts

    2. Brief Summary (300 words, can include examples and quotes)
       - Key success factors
       - Audience pain points
       - What the audience aspires to be
       - Primary strengths
       - Growth opportunities
       - Unique value proposition

    Format your entire report in markdown, using appropriate headers, bullet points, and emphasis where needed. Ensure that your analysis is thorough, insightful, and based solely on the information provided in the screenshots. Do not make assumptions or include information not evident from the given data.

    Begin your analysis now.

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
                max_tokens=500,
                temperature=0.1,
                messages=[{
                    'role': 'user',
                    'content': message_content
                }]
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