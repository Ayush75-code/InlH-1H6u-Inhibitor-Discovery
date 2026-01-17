from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
input_dir = "./"  # Current directory
output_filename = "protein_ligand_interactions_grid_composite.png"

# Input image filenames in grid order (top-left, top-right, bottom-left, bottom-right)
image_files = [
    "control_interactiondpi900_white_bg.png",
    "hedragenin_interactiondpi900_white_bg.png",
    "lup_interactiondpi900_white_bg.png",
    "mas_interactiondpi900_white_bg.png"
]

# Labels for each image
labels = [
    "A) Control Complex",
    "B) Hedragenin Analogue Complex",
    "C) Lupeol Analogue Complex",
    "D) Maslinic Acid Analogue Complex"
]

# Settings
DPI = 900
PADDING = 200  # Padding between images and edges (in pixels at 900 DPI)
LABEL_SPACING = 150  # Space between image and label
FONT_SIZE = 120  # Font size for labels
BORDER_WIDTH = 8  # Width of border frames around each image
BORDER_COLOR = (100, 100, 100)  # Dark gray color for borders

try:
    # Load all images
    print("Loading images...")
    images = []
    for filename in image_files:
        filepath = os.path.join(input_dir, filename)
        img = Image.open(filepath)
        images.append(img)
        print(f"Loaded: {filename} - Size: {img.size}")
    
    # Get dimensions (assuming all images are same size)
    img_width, img_height = images[0].size
    
    # Try to load a good font
    try:
        # Try Arial first
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", FONT_SIZE)
    except:
        try:
            # Try DejaVu Sans
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONT_SIZE)
        except:
            # Fallback to default font
            print("Warning: Using default font. Install DejaVu fonts for better results.")
            font = ImageFont.load_default()
    
    # Calculate canvas dimensions
    # Width: 2 images + 3 padding spaces (left, middle, right)
    canvas_width = (2 * img_width) + (3 * PADDING)
    # Height: 2 images + label spaces + 3 padding spaces (top, middle, bottom)
    canvas_height = (2 * img_height) + (2 * LABEL_SPACING) + (3 * PADDING)
    
    print(f"\nCreating canvas: {canvas_width} x {canvas_height} pixels at {DPI} DPI")
    
    # Create white canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    draw = ImageDraw.Draw(canvas)
    
    # Position and paste images in 2x2 grid
    positions = [
        (PADDING, PADDING),  # Top-left
        (PADDING * 2 + img_width, PADDING),  # Top-right
        (PADDING, PADDING * 2 + img_height + LABEL_SPACING),  # Bottom-left
        (PADDING * 2 + img_width, PADDING * 2 + img_height + LABEL_SPACING)  # Bottom-right
    ]
    
    print("\nComposing grid...")
    for i, (img, pos, label) in enumerate(zip(images, positions, labels)):
        # Draw border frame around image
        border_box = [
            pos[0] - BORDER_WIDTH,
            pos[1] - BORDER_WIDTH,
            pos[0] + img_width + BORDER_WIDTH,
            pos[1] + img_height + BORDER_WIDTH
        ]
        draw.rectangle(border_box, outline=BORDER_COLOR, width=BORDER_WIDTH)
        
        # Paste image
        canvas.paste(img, pos)
        
        # Calculate label position (centered below image)
        label_y = pos[1] + img_height + (LABEL_SPACING // 4)
        
        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        
        # Center text below image
        label_x = pos[0] + (img_width - text_width) // 2
        
        # Draw label
        draw.text((label_x, label_y), label, fill='black', font=font)
        print(f"Added: {label}")
    
    # Save with DPI information
    print(f"\nSaving composite image to: {output_filename}")
    canvas.save(output_filename, dpi=(DPI, DPI), quality=100)
    
    print(f"✓ Success! Composite image saved.")
    print(f"  Final dimensions: {canvas_width} x {canvas_height} pixels")
    print(f"  Resolution: {DPI} DPI")
    print(f"  File size: {os.path.getsize(output_filename) / (1024*1024):.2f} MB")

except FileNotFoundError as e:
    print(f"Error: Could not find file - {e}")
    print(f"Please ensure all PNG files are in: {input_dir}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
