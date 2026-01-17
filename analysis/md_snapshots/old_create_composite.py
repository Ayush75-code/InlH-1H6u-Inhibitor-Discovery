#!/usr/bin/env python3
"""
Create a composite image grid from molecular dynamics trajectory snapshots.
Maintains original 1500 DPI resolution for publication-quality output.
Compatible with Python 2.7+ and Python 3.x
"""

from __future__ import print_function
from PIL import Image, ImageDraw, ImageFont
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

# Molecule names (will be used to construct filenames)
MOLECULES = ['Control', 'Hedragenin', 'Lupeol', 'Maslinic_Acid']

# Time points for column labels
TIME_POINTS = ['00ns', '25ns', '50ns', '75ns', '100ns', '125ns']
TIME_LABELS = ['0 ns', '25 ns', '50 ns', '75 ns', '100 ns', '125 ns']

# Row labels (full names for left side)
ROW_LABELS = [
    '(A). Protein-Control',
    '(B). Protein-Hedragenin Analogue',
    '(C). Protein-Lupeol Analogue',
    '(D). Protein-Maslinic_Acid Analogue'
]

# Input directory (modify as needed)
# Use './' for current directory or specify full path
INPUT_DIR = './'

# Output file
OUTPUT_FILE = 'final_composite_figure.png'

# DPI setting (must match input images)
DPI = 1500

# Spacing and padding (in pixels)
PADDING = 100  # Outer padding around entire grid
IMAGE_SPACING = 80  # Space between images
LABEL_SPACING = 60  # Space for labels
FONT_SIZE_TIME = 180  # Font size for time labels
FONT_SIZE_ROW = 200  # Font size for row labels

# ============================================================================
# MAIN SCRIPT
# ============================================================================

def load_images():
    """Load all images and return as a 2D list (rows x cols)."""
    images = []
    
    for molecule in MOLECULES:
        row_images = []
        for time_point in TIME_POINTS:
            filename = "{}_frame_{}.png".format(molecule, time_point)
            filepath = os.path.join(INPUT_DIR, filename)
            
            if not os.path.exists(filepath):
                raise IOError("Image not found: {}".format(filepath))
            
            img = Image.open(filepath)
            print("Loaded: {} - Size: {}".format(filename, img.size))
            row_images.append(img)
        
        images.append(row_images)
    
    return images


def get_font(size):
    """Try to load a clear sans-serif font, fallback to default."""
    font_options = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        'C:\\Windows\\Fonts\\arial.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
    ]
    
    for font_path in font_options:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
    
    # Fallback to default font
    print("Warning: Using default font. For better results, install DejaVu fonts.")
    return ImageFont.load_default()


def get_text_size(draw, text, font):
    """Get text size in a way compatible with both old and new Pillow versions."""
    try:
        # New Pillow API (9.2.0+)
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        # Old Pillow API
        return draw.textsize(text, font=font)


def create_composite_grid(images):
    """Create the final composite image with labels."""
    
    # Get dimensions of a single image (assuming all are the same size)
    img_width, img_height = images[0][0].size
    
    # Calculate canvas dimensions
    rows = len(images)
    cols = len(images[0])
    
    # Width: left padding + images + spacing + right padding
    canvas_width = (PADDING + (cols * img_width) + ((cols - 1) * IMAGE_SPACING) + PADDING)
    
    # Height: top padding + (images + row labels + time labels + spacing for each row) + bottom padding
    row_label_height = 250  # Space for row labels above each row
    time_label_height = 250  # Space for time labels below each row
    canvas_height = (PADDING + 
                     (rows * (row_label_height + img_height + time_label_height + IMAGE_SPACING)) + 
                     PADDING)
    
    # Create white canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    draw = ImageDraw.Draw(canvas)
    
    # Load fonts
    font_time = get_font(FONT_SIZE_TIME)
    font_row = get_font(FONT_SIZE_ROW)
    
    # Starting positions
    start_x = PADDING
    start_y = PADDING
    
    # Place images and labels
    for row_idx, row_images in enumerate(images):
        # Calculate Y position for this row
        current_y_row_label = start_y + row_idx * (row_label_height + img_height + time_label_height + IMAGE_SPACING)
        current_y_images = current_y_row_label + row_label_height
        
        # Draw row label (centered above the row of images)
        row_label = ROW_LABELS[row_idx]
        text_width, text_height = get_text_size(draw, row_label, font_row)
        
        # Center the row label horizontally across all images
        total_row_width = (cols * img_width) + ((cols - 1) * IMAGE_SPACING)
        row_label_x = start_x + (total_row_width - text_width) // 2
        row_label_y = current_y_row_label + (row_label_height - text_height) // 2
        
        draw.text((row_label_x, row_label_y), row_label, fill='black', font=font_row)
        
        # Place images in this row
        for col_idx, img in enumerate(row_images):
            current_x = start_x + col_idx * (img_width + IMAGE_SPACING)
            
            # Paste image
            canvas.paste(img, (current_x, current_y_images))
            
            # Draw time label below image (centered)
            time_label = TIME_LABELS[col_idx]
            text_width, text_height = get_text_size(draw, time_label, font_time)
            
            label_x = current_x + (img_width - text_width) // 2
            label_y = current_y_images + img_height + 50
            
            draw.text((label_x, label_y), time_label, fill='black', font=font_time)
    
    return canvas


def main():
    """Main execution function."""
    print("=" * 70)
    print("MD Trajectory Grid Compositor")
    print("=" * 70)
    print("\nInput directory: {}".format(INPUT_DIR))
    print("Output file: {}".format(OUTPUT_FILE))
    print("Target DPI: {}".format(DPI))
    print("\nGrid layout: {} rows × {} columns".format(len(MOLECULES), len(TIME_POINTS)))
    print("\nLoading images...")
    
    # Load all images
    images = load_images()
    
    print("\nSuccessfully loaded {} images.".format(len(images) * len(images[0])))
    print("\nCreating composite grid...")
    
    # Create composite
    composite = create_composite_grid(images)
    
    print("\nComposite dimensions: {} × {} pixels".format(composite.size[0], composite.size[1]))
    
    # Save with high DPI
    print("\nSaving composite image to: {}".format(OUTPUT_FILE))
    composite.save(OUTPUT_FILE, dpi=(DPI, DPI), quality=100)
    
    print("\n✓ Composite image created successfully!")
    print("  File: {}".format(OUTPUT_FILE))
    print("  Size: {} × {} pixels".format(composite.size[0], composite.size[1]))
    print("  DPI: {}".format(DPI))
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n✗ Error: {}".format(e))
        import traceback
        traceback.print_exc()
