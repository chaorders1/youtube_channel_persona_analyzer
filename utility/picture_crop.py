"""Image Cropping Utility

This module provides functionality to crop large images into smaller parts vertically.
It maintains the original image quality and width while dividing it into specified heights.

Example Usage:
    # Process single image
    python picture_crop.py --image "/path/to/image.png"
    python picture_crop.py --image "/Users/yuanlu/Code/youtube_copilot/data/web_snapshots/veritasium_20241106_111925.png"
    
    # Process entire directory
    python picture_crop.py --dir "/path/to/directory"
    
    # Process directory with custom settings
    python picture_crop.py --dir "//Users/yuanlu/Code/youtube_copilot/data/web_snapshots" --output "custom_output" --height 1024 --overlap 100
    python picture_crop.py --dir "//Users/yuanlu/Code/youtube_copilot/data/web_snapshots"  --height 1024 --overlap 100

Features:
    - Supports both single image and directory processing
    - Processes PNG, JPEG, JPG, GIF, BMP, TIFF files
    - Maintains original image quality and structure
    - Configurable crop settings
"""

from PIL import Image
import os
from pathlib import Path
from datetime import datetime
import argparse
from typing import Set, List

SUPPORTED_FORMATS: Set[str] = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}

def get_output_format(input_file: str) -> str:
    """Get the appropriate output format based on input file extension."""
    ext = Path(input_file).suffix.lower()
    
    format_map = {
        '.jpg': 'JPEG',
        '.jpeg': 'JPEG',
        '.png': 'PNG',
        '.gif': 'GIF',
        '.bmp': 'BMP',
        '.tiff': 'TIFF'
    }
    
    return format_map.get(ext, 'JPEG')

def process_directory(
    input_dir: str, 
    output_dir: str = None, 
    part_height: int = 1200, 
    overlap: int = 200
) -> None:
    """Process all supported image files in a directory."""
    input_path = Path(input_dir)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Directory not found: {input_dir}")
    
    # Get all image files in directory
    image_files = []
    for ext in SUPPORTED_FORMATS:
        image_files.extend(input_path.glob(f"*{ext}"))
    
    if not image_files:
        print(f"No supported image files found in {input_dir}")
        return
    
    print(f"Found {len(image_files)} image(s) to process")
    
    # Process each image
    for idx, image_file in enumerate(image_files, 1):
        print(f"\nProcessing image {idx}/{len(image_files)}: {image_file.name}")
        try:
            crop_picture(str(image_file), output_dir, part_height, overlap)
        except Exception as e:
            print(f"Error processing {image_file.name}: {e}")

def crop_picture(input_file: str, output_dir: str = None, part_height: int = 1200, overlap: int = 200) -> None:
    """Crop an image into multiple parts vertically with overlap."""
    # Setup paths
    input_path = Path(input_file)
    image_name = input_path.stem
    
    # Determine output directory
    if output_dir:
        prefix = '' if output_dir.startswith('crop_') else 'crop_'
        output_dir = f'{prefix}{output_dir}_{image_name}'
    else:
        output_dir = f'crop_{image_name}'
    
    # Setup output path
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / 'data' / output_dir
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process the image
    with Image.open(input_path) as img:
        width, height = img.size
        num_parts = (height + part_height - 1) // part_height
        output_format = get_output_format(str(input_path))
        extension = '.jpg' if output_format == 'JPEG' else f'.{output_format.lower()}'
        
        # Create metadata
        create_metadata(output_path, input_path, img, output_format, 
                       width, height, part_height, overlap, num_parts, extension)
        
        # Crop and save parts
        for i in range(num_parts):
            top = max(0, i * (part_height - overlap))
            bottom = min(height, top + part_height)
            
            part = img.crop((0, top, width, bottom))
            output_file = output_path / f"{image_name}_part_{i+1}_h{part_height}_overlap{overlap}{extension}"
            part.save(output_file, output_format)
            print(f"  Saved part {i+1}/{num_parts}: {output_file.name}")

def create_metadata(output_path: Path, input_path: Path, img: Image, 
                   output_format: str, width: int, height: int, 
                   part_height: int, overlap: int, num_parts: int, 
                   extension: str) -> None:
    """Create metadata file for the cropping operation."""
    metadata_path = output_path / 'metadata.txt'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write(f"Image Crop Metadata:\n")
        f.write(f"==================\n\n")
        f.write(f"Source Information:\n")
        f.write(f"- Image File: {input_path.name}\n")
        f.write(f"- Original Path: {input_path}\n")
        f.write(f"- Format: {output_format}\n")
        f.write(f"\nImage Properties:\n")
        f.write(f"- Dimensions: {width}x{height}\n")
        f.write(f"- Mode: {img.mode}\n")
        f.write(f"\nCrop Settings:\n")
        f.write(f"- Part Height: {part_height} pixels\n")
        f.write(f"- Overlap: {overlap} pixels\n")
        f.write(f"- Number of Parts: {num_parts}\n")
        f.write(f"- Output Directory: {output_path}\n")
        f.write(f"\nProcessing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crop images into vertical parts with overlap')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--image', help='Path to single image file')
    group.add_argument('--dir', help='Path to directory containing images')
    parser.add_argument('--output', help='Output directory name')
    parser.add_argument('--height', type=int, default=1200, help='Height of each part (default: 1200)')
    parser.add_argument('--overlap', type=int, default=200, help='Overlap between parts (default: 200)')
    
    args = parser.parse_args()
    
    try:
        if args.image:
            crop_picture(args.image, args.output, args.height, args.overlap)
        else:
            process_directory(args.dir, args.output, args.height, args.overlap)
    except Exception as e:
        print(f'Error: {e}')
        exit(1)