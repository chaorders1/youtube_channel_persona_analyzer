"""Screenshot Utility

This module provides functionality to capture website screenshots using the ScreenshotAPI service.
It specializes in capturing YouTube channel pages with optimized settings.

Example Usage:
    # Basic usage - capture YouTube channel
    screenshot('https://www.youtube.com/@veritasium')
    
    # Capture with custom options
    screenshot('https://www.youtube.com/@veritasium',
              width=1920,
              height=3240,  # 1080 * 3 for better content capture
              format='png',
              output_dir='screenshots')
    
    # Command line usage:
    # Single channel capture:
    python screenshotapi.py --url='https://www.youtube.com/@veritasium'
    
    # Batch capture from file:
    python screenshotapi.py --file='/Users/yuanlu/Code/youtube_copilot/data/youtube_url.txt'

Features:
    - Optimized for YouTube channel pages
    - Smart file naming using channel handles
    - Lazy loading support for dynamic content
    - High-resolution capture (1920x3240)
    - Ad and cookie banner blocking
    - Custom CSS injection for YouTube-specific elements
    - Automatic retries with exponential backoff
    - Comprehensive error handling and logging
    - URL validation and sanitization

Output Structure:
    data/web_snapshots/
    └── {channel_name}_{timestamp}.png
    Example: veritasium_20241106_102308.png

Technical Details:
    - Uses ScreenshotAPI's advanced features:
        - Lazy loading detection
        - Network idle waiting
        - Custom viewport settings
        - CSS injection for YouTube elements
    - Implements robust error handling with 3 retries
    - Validates URLs before processing
    - Generates meaningful filenames from YouTube URLs

Requirements:
    - Python 3.6+
    - urllib (standard library)
    - os (standard library)
    - datetime (standard library)
    - logging (standard library)
    - python-dotenv (for API token management)

Configuration:
    - API token should be set in .env file as SCREENSHOT_API_TOKEN
    - Default output directory: data/web_snapshots/
    - Default image format: PNG
    - Default viewport: 1920x3240 (optimized for YouTube)
"""

#!/usr/bin/python3
import urllib.request
import urllib.parse
import os
import argparse
import logging
from pathlib import Path
from typing import Dict, Optional, List
from dotenv import load_dotenv
from urllib.parse import urlparse
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScreenshotAPI:
    """Handles screenshot capture using ScreenshotAPI service."""
    
    BASE_URL = "https://shot.screenshotapi.net/screenshot"
    
    def __init__(self, api_token: str):
        """Initialize with API token."""
        self.api_token = api_token
        
    def generate_api_url(self, url: str, options: Dict) -> str:
        """Generate API URL with parameters optimized for YouTube content capture."""
        params = {
            # Required parameters
            'token': self.api_token,
            'url': url,
            
            # Output settings
            'output': 'image',
            'file_type': options.get('file_type', 'png'),
            
            # Viewport settings - Optimized for YouTube
            'width': options.get('width', '1920'),
            'height': options.get('height', '3240'),  # 1080 * 3 for better content capture
            'full_page': 'false',  # Disabled as per requirement
            
            # Loading optimizations
            'delay': options.get('delay', '12000'),  # Increased to 12 seconds
            'wait_for_event': 'networkidle0',  # Wait for all network requests to finish
            'lazy_load': 'true',  # Enable lazy loading detection
            'fresh': 'true',  # Always get fresh screenshot
            
            # Scrolling configuration
            'scrolling_screenshot': 'true',
            'scroll_speed': 'slow',  # Slow scroll for better content loading
            'duration': '30',  # 30 seconds scroll duration
            'scroll_back': 'false',  # No need to scroll back for YouTube
            
            # Content blocking
            'block_ads': 'true',
            'no_cookie_banners': 'true',
            
            # Quality settings
            'retina': 'true'
        }
        
        # YouTube-specific CSS injection
        params['css'] = '''
            /* Force show thumbnails and content */
            ytd-rich-grid-renderer, ytd-rich-item-renderer {
                visibility: visible !important;
                opacity: 1 !important;
            }
            
            /* Hide unnecessary elements */
            ytd-popup-container,
            tp-yt-paper-dialog,
            .ytd-consent-bump-v2-lightbox { 
                display: none !important; 
            }
        '''

        query_string = urllib.parse.urlencode(params)
        return f"{self.BASE_URL}?{query_string}"

def is_valid_url(url: str) -> bool:
    """Validate if the string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def read_urls_from_file(file_path: str) -> List[str]:
    """Read URLs from a file, skipping invalid URLs."""
    valid_urls = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                url = line.strip()
                if url and is_valid_url(url):
                    valid_urls.append(url)
                elif url:
                    logger.warning(f"Skipping invalid URL: {url}")
    except Exception as e:
        logger.error(f"Error reading URLs file: {e}")
        raise
    return valid_urls

def save_screenshot(api_url: str, output_path: str, retries: int = 3) -> bool:
    """Save a screenshot with improved error handling."""
    for attempt in range(retries):
        try:
            # Create request with headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/*'
            }
            request = urllib.request.Request(api_url, headers=headers)
            
            # Make request with timeout
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status != 200:
                    raise urllib.error.HTTPError(
                        api_url, response.status, 
                        "Failed to fetch screenshot", 
                        response.headers, None
                    )
                
                # Read and save the image data
                with open(output_path, 'wb') as f:
                    f.write(response.read())
                
                # Verify file was created and has content
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    logger.info(f"Screenshot saved successfully to: {output_path}")
                    return True
                else:
                    raise Exception("Screenshot file is empty or not created")
                    
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP Error on attempt {attempt + 1}: {e.code} - {e.reason}")
            if attempt < retries - 1:
                time.sleep(min((attempt + 1) * 2, 10))
                
        except urllib.error.URLError as e:
            logger.error(f"URL Error on attempt {attempt + 1}: {str(e)}")
            if attempt < retries - 1:
                time.sleep(min((attempt + 1) * 2, 10))
                
        except Exception as e:
            logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
            if attempt < retries - 1:
                time.sleep(min((attempt + 1) * 2, 10))
                
    return False

def capture_screenshot(url: str, output_dir: str, options: Optional[Dict] = None) -> Optional[str]:
    """Capture a screenshot with improved error handling and naming."""
    if not options:
        options = {}
        
    try:
        # Initialize API client
        api_token = os.getenv('SCREENSHOT_API_TOKEN')
        if not api_token:
            raise ValueError("SCREENSHOT_API_TOKEN not found in environment variables")
            
        api_client = ScreenshotAPI(api_token)
        
        # Generate API URL
        api_url = api_client.generate_api_url(url, options)
        logger.debug(f"Generated API URL: {api_url}")
        
        # Create output filename using URL components
        parsed_url = urlparse(url)
        channel_name = parsed_url.path.split('@')[-1].split('/')[0] if '@' in parsed_url.path else 'screenshot'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{channel_name}_{timestamp}.{options.get('file_type', 'png')}"
        output_path = os.path.join(output_dir, filename)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save screenshot
        if save_screenshot(api_url, output_path):
            return output_path
            
    except Exception as e:
        logger.error(f"Error capturing screenshot for {url}: {e}")
        
    return None

def screenshot(url: str) -> Optional[str]:
    """
    Capture a screenshot of a URL using default settings optimized for YouTube.
    
    This is the main interface function for the module.
    
    Args:
        url: URL to capture screenshot of
        
    Returns:
        Optional[str]: Path to saved screenshot file, or None if capture failed
    """
    # Set up default output directory
    data_folder = Path(__file__).parent.parent / 'data'
    output_dir = str(data_folder / 'web_snapshots')
    
    # Use default options optimized for YouTube
    options = {
        'width': '1920',
        'height': '3240',
        'file_type': 'png',
        'full_page': 'false',
        'block_ads': 'true',
        'no_cookie_banners': 'true'
    }
    
    return capture_screenshot(url, output_dir, options)

def main():
    """Main function to handle command line arguments and capture screenshots."""
    # Load environment variables
    load_dotenv()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Capture website screenshots using ScreenshotAPI')
    parser.add_argument('--url', help='Single URL to capture')
    parser.add_argument('--file', help='File containing URLs to capture')
    parser.add_argument('--width', help='Viewport width', default='1680')
    parser.add_argument('--height', help='Viewport height', default='867')
    parser.add_argument('--format', help='Output format (png/jpg/pdf)', default='png')
    parser.add_argument('--full-page', help='Capture full page', action='store_true')
    args = parser.parse_args()

    # Set up screenshot options
    options = {
        'width': args.width,
        'height': args.height,
        'file_type': args.format,
        'full_page': str(args.full_page).lower(),
        'block_ads': 'true',
        'no_cookie_banners': 'true'
    }

    # Set up output directory
    data_folder = Path(__file__).parent.parent / 'data'
    output_dir = data_folder / 'web_snapshots'
    
    if args.url:
        # Handle single URL
        if output_path := screenshot(args.url):
            logger.info(f"Screenshot saved to: {output_path}")
    elif args.file:
        # Handle URLs from file
        urls_file = data_folder / args.file
        urls = read_urls_from_file(str(urls_file))
        
        for url in urls:
            if output_path := screenshot(url):
                logger.info(f"Screenshot saved for {url} to: {output_path}")
            else:
                logger.error(f"Failed to capture screenshot for: {url}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()