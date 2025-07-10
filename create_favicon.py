#!/usr/bin/env python3
"""
Create a PNG favicon from the SVG logo.
This script requires the cairosvg library to convert SVG to PNG.
"""

import os
import sys

try:
    import cairosvg
except ImportError:
    print("cairosvg library not found. Installing...")
    os.system("pip install cairosvg")
    import cairosvg

def create_favicon():
    """Create a PNG favicon from the SVG logo."""
    svg_path = "static/images/logo_4.svg"
    png_path = "static/images/favicon.png"
    
    if not os.path.exists(svg_path):
        print(f"Error: SVG file not found at {svg_path}")
        return False
    
    try:
        # Convert SVG to PNG favicon (32x32 pixels)
        cairosvg.svg2png(
            url=svg_path,
            write_to=png_path,
            output_width=32,
            output_height=32
        )
        print(f"Favicon created successfully: {png_path}")
        return True
    except Exception as e:
        print(f"Error creating favicon: {e}")
        return False

if __name__ == "__main__":
    create_favicon() 