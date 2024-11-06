"""YouTube Channel Persona Pipeline

This module orchestrates the end-to-end pipeline for generating YouTube channel personas
by integrating screenshot capture, image processing, and persona generation utilities.

Example Usage:
    # Basic pipeline execution
    python persona_pipeline.py
    
    # Process single YouTube channel
    python persona_pipeline.py --url="https://www.youtube.com/@veritasium"
    python persona_pipeline.py --url="https://www.youtube.com/@AIJasonZ"
    
    # Custom configuration with file input
    python persona_pipeline.py --urls-file="custom_urls.txt" --max-retries=5
    
    # Programmatic usage
    pipeline = PersonaPipeline(
        urls_file='custom_urls.txt',
        max_retries=5,
        single_url='https://www.youtube.com/@veritasium'
    )
    pipeline.run_pipeline()

Command Line Arguments:
    --url: Single YouTube URL to process
    --urls-file: Path to file containing YouTube URLs (default: data/youtube_url.txt)
    --max-retries: Maximum number of retry attempts (default: 3)

Features:
    - End-to-end automation of persona generation
    - Support for both single URL and batch processing
    - Multi-stage processing:
        1. Screenshot capture of YouTube channels
        2. Intelligent image segmentation
        3. Persona analysis and generation
    - Robust error handling with retry mechanism
    - Comprehensive logging system
    - Independent stage processing
    - Configurable retry attempts

Output Structure:
    data/
    ├── web_snapshots/                 # Raw screenshots
    │   └── {channel}_{timestamp}.png
    ├── crop_{channel}_{timestamp}/    # Cropped segments
    │   ├── segment_001.png
    │   └── metadata.txt
    ├── logs/                          # Pipeline logs
    │   └── pipeline_{timestamp}.log
    └── personas/                      # Generated personas
        └── {channel}_persona.md

Technical Details:
    - Implements exponential backoff for retries
    - Modular architecture for easy maintenance
    - Comprehensive error tracking
    - Progress logging at each stage
    - Independent channel processing
    - Command-line interface for flexible usage

Requirements:
    - Python 3.8+
    - Custom utilities:
        - screenshotapi.py
        - picture_crop.py
        - persona.py
    - Environment setup:
        - API tokens in .env
        - URLs list in data/youtube_url.txt (if not using --url)

Configuration:
    - URLs file location: data/youtube_url.txt (configurable)
    - Log directory: data/logs/
    - Default retry attempts: 3 (configurable)
    - Configurable through class initialization or command line arguments
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import time

# Import the utility modules to use their main functions
import screenshotapi
import picture_crop
from persona import PersonaAnalyzer  # Import the correct class

class PersonaPipeline:
    """
    Orchestrates the end-to-end pipeline for generating YouTube channel personas.
    """
    
    def __init__(self, urls_file: str = 'data/youtube_url.txt', max_retries: int = 3, single_url: str = None):
        """Initialize the pipeline with configuration."""
        self.urls_file = urls_file
        self.max_retries = max_retries
        self.single_url = single_url
        self.setup_logging()
        
        # Configure cropping parameters
        self.crop_height = 1024
        self.crop_overlap = 100
        
        # Initialize persona analyzer
        self.persona_analyzer = PersonaAnalyzer()

    def setup_logging(self) -> None:
        """Configure logging for the pipeline."""
        log_dir = Path('data/logs')
        log_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'pipeline_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('PersonaPipeline')

    def read_urls(self) -> List[str]:
        """Read YouTube URLs from the specified file or return single URL if provided."""
        if self.single_url:
            return [self.single_url]
            
        try:
            with open(self.urls_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            return urls
        except FileNotFoundError:
            self.logger.error(f"URLs file not found: {self.urls_file}")
            raise

    def execute_with_retry(self, operation: callable, *args, **kwargs) -> Optional[any]:
        """
        Execute an operation with retry mechanism.
        
        Args:
            operation: Function to execute
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation
        """
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Operation failed after {self.max_retries} attempts")
                    raise

    def process_channel(self, url: str) -> None:
        """Process a single YouTube channel through the pipeline."""
        self.logger.info(f"Processing channel: {url}")
        
        try:
            # Stage 1: Capture screenshots using screenshot function
            screenshot_path = self.execute_with_retry(
                screenshotapi.screenshot,
                url
            )
            
            # Stage 2: Crop images using main crop_picture function
            self.logger.info(f"Cropping screenshot: {screenshot_path}")
            self.execute_with_retry(
                picture_crop.crop_picture,
                screenshot_path,
                None,  # Use default output directory
                self.crop_height,
                self.crop_overlap
            )
            
            # Get the output directory path
            input_path = Path(screenshot_path)
            image_name = input_path.stem
            output_dir = f'crop_{image_name}'
            cropped_dir_path = str(input_path.parent.parent / output_dir)
            
            # Stage 3: Generate persona using PersonaAnalyzer's analyze_channel method
            self.logger.info(f"Analyzing channel from: {cropped_dir_path}")
            analysis_result = self.execute_with_retry(
                self.persona_analyzer.analyze_channel,
                cropped_dir_path
            )
            
            # Save the analysis result
            analysis_path = Path(cropped_dir_path + '_analysis.md')
            analysis_path.write_text(analysis_result)
            self.logger.info(f"Analysis saved to: {analysis_path}")
            
            self.logger.info(f"Completed processing channel: {url}")
            
        except Exception as e:
            self.logger.error(f"Error processing channel {url}: {str(e)}")
            raise

    def run_pipeline(self) -> None:
        """Execute the complete pipeline for all URLs."""
        self.logger.info("Starting persona pipeline execution")
        
        try:
            urls = self.read_urls()
            self.logger.info(f"Found {len(urls)} URLs to process")
            
            for url in urls:
                try:
                    self.process_channel(url)
                except Exception as e:
                    self.logger.error(f"Failed to process channel {url}: {str(e)}")
                    continue
                    
            self.logger.info("Pipeline execution completed successfully")
            
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {str(e)}")
            raise

def main():
    """Main entry point for the pipeline."""
    try:
        # Add argument parsing
        import argparse
        parser = argparse.ArgumentParser(description='Generate YouTube channel personas')
        parser.add_argument('--url', type=str, help='Single YouTube URL to process')
        parser.add_argument('--urls-file', type=str, default='data/youtube_url.txt',
                          help='Path to file containing YouTube URLs')
        parser.add_argument('--max-retries', type=int, default=3,
                          help='Maximum number of retry attempts')
        
        args = parser.parse_args()
        
        pipeline = PersonaPipeline(
            urls_file=args.urls_file,
            max_retries=args.max_retries,
            single_url=args.url
        )
        pipeline.run_pipeline()
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
