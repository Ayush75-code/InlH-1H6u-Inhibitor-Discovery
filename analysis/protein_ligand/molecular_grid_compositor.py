from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
input_dir = "./"  # Current directory
output_filename = "protein_ligand_interactions_composite.png"

# Input filenames in grid order (top-left, top-right, bottom-left, bottom-right)
image_filenames = [
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

# Layout parameters
padding = 200  # Padding around edges and between images (in pixels at 900 DPI)
label_space = 300  # Space for labels below images
dpi = 900
border_width = 8  # Width of grid lines/borders
border_color = 'black'  # Color of grid lines

# Load all images
print("Loading images...")
images = []
for filename in image_filenames:
    filepath = os.path.join(input_dir, filename)
    img = Image.open(filepath)
    images.append(img)
    print(f"Loaded: {filename} - Size: {img.size}")

# Get dimensions (assuming all images are same size)
img_width, img_height = images[0].size
print(f"\nIndividual image size: {img_width}x{img_height} pixels")

# Calculate composite dimensions
# 2 columns: padding + img + padding + img + padding
composite_width = padding + img_width + padding + img_width + padding
# 2 rows: padding + (img + label_space) + padding + (img + label_space) + padding
composite_height = padding + (img_height + label_space) + padding + (img_height + label_space) + padding

print(f"Composite canvas size: {composite_width}x{composite_height} pixels at {dpi} DPI")

# Create white canvas
composite = Image.new('RGB', (composite_width, composite_height), 'white')
draw = ImageDraw.Draw(composite)

# Try to load a high-quality font
font_size = 120  # Font size for 900 DPI
try:
    # Try common font paths
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "/System/Library/Fonts/Helvetica.ttc"
    ]
    font = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
            print(f"Using font: {font_path}")
            break
    if font is None:
        print("Using default font (truetype fonts not found)")
        font = ImageFont.load_default()
except Exception as e:
    print(f"Font loading error: {e}. Using default font.")
    font = ImageFont.load_default()

# Position images in 2x2 grid
positions = [
    (padding, padding),  # Top-left
    (padding + img_width + padding, padding),  # Top-right
    (padding, padding + img_height + label_space + padding),  # Bottom-left
    (padding + img_width + padding, padding + img_height + label_space + padding)  # Bottom-right
]

print("\nCompositing images and adding labels...")
for i, (img, pos, label) in enumerate(zip(images, positions, labels)):
    # Paste image
    composite.paste(img, pos)
    
    # Calculate label position (centered below image)
    label_x = pos[0] + img_width // 2
    label_y = pos[1] + img_height + 80  # 80 pixels below image
    
    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Draw label centered
    text_position = (label_x - text_width // 2, label_y)
    draw.text(text_position, label, fill='black', font=font)
    
    print(f"Added: {label}")

# Draw grid borders around each cell
print("\nDrawing grid borders...")
cell_width = img_width
cell_height = img_height + label_space

# Draw borders for each cell
for i, pos in enumerate(positions):
    x, y = pos
    # Draw rectangle around each cell (image + label area)
    draw.rectangle(
        [x - border_width//2, y - border_width//2, 
         x + cell_width + border_width//2, y + cell_height + border_width//2],
        outline=border_color,
        width=border_width
    )

print(f"✓ Grid borders added")

# Save with DPI information
print(f"\nSaving composite image: {output_filename}")
composite.save(output_filename, dpi=(dpi, dpi), quality=100)

print(f"✓ Successfully created composite image!")
print(f"  Output: {output_filename}")
print(f"  Resolution: {composite_width}x{composite_height} pixels")
print(f"  DPI: {dpi}")
print(f"  File size: {os.path.getsize(output_filename) / (1024*1024):.2f} MB")
