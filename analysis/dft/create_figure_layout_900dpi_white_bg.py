#!/usr/bin/env python3
"""
Create publication-quality figure layouts from molecular visualization images
Matches the reference layout style with ESP surfaces and HOMO-LUMO orbitals
High-resolution 900 DPI output with white backgrounds for publishing
"""

from PIL import Image, ImageDraw, ImageFont
import os
import sys

def create_esp_figure(molecules, output_file='Figure_ESP_Surfaces_900dpi.tiff'):
    """
    Create ESP surface comparison figure (similar to Fig. 11 reference)
    Layout: Side-by-side ESP surfaces with labels
    """
    print(f"Creating ESP surface comparison figure...")
    
    # Load images
    images = []
    labels = []
    
    for mol_name, label in molecules:
        esp_file = f"{mol_name}_ESP_Surface_dpi900.png"
        
        if os.path.exists(esp_file):
            img = Image.open(esp_file)
            # Convert to RGB for white background
            if img.mode != 'RGB':
                # Create white background and paste the image
                rgb_img = Image.new('RGB', img.size, 'white')
                if img.mode == 'RGBA':
                    # Use alpha channel as mask
                    rgb_img.paste(img, (0, 0), img)
                else:
                    rgb_img.paste(img, (0, 0))
                img = rgb_img
            images.append(img)
            labels.append(label)
            print(f"  ✓ Loaded {esp_file}")
        else:
            print(f"  ✗ Missing {esp_file}")
    
    if not images:
        print("No ESP images found!")
        return
    
    # Calculate dimensions (scaled for 900 DPI)
    n_images = len(images)
    
    # Resize all images to same height (larger for 900 DPI)
    target_height = 2400  # 3x larger for 900 DPI
    resized_images = []
    for img in images:
        aspect = img.width / img.height
        new_width = int(target_height * aspect)
        resized = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
        resized_images.append(resized)
    
    # Calculate canvas size (scaled margins)
    total_width = sum(img.width for img in resized_images)
    margin = 150  # 3x larger
    label_height = 240  # 3x larger
    colorbar_height = 300  # 3x larger
    
    canvas_width = total_width + margin * (n_images + 1)
    canvas_height = target_height + label_height + colorbar_height + margin * 3
    
    # Create white canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    draw = ImageDraw.Draw(canvas)
    
    # Try to load fonts (larger sizes for 900 DPI)
    try:
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 108)  # 3x larger
        font_caption = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 84)  # Larger and bold for caption
    except:
        font_label = ImageFont.load_default()
        font_caption = ImageFont.load_default()
    
    # Place images with labels
    x_offset = margin
    for i, (img, label) in enumerate(zip(resized_images, labels)):
        # Draw label (A., B., C., etc.)
        label_text = f"{chr(65+i)}. {label}"
        bbox = draw.textbbox((0, 0), label_text, font=font_label)
        text_width = bbox[2] - bbox[0]
        text_x = x_offset + (img.width - text_width) // 2
        draw.text((text_x, margin), label_text, fill='black', font=font_label)
        
        # Paste image
        canvas.paste(img, (x_offset, margin + label_height))
        
        x_offset += img.width + margin
    
    # Add caption with larger font
    caption = "Molecular electrostatic potential (MEP) surface analysis"
    bbox = draw.textbbox((0, 0), caption, font=font_caption)
    caption_width = bbox[2] - bbox[0]
    caption_x = (canvas_width - caption_width) // 2
    caption_y = canvas_height - colorbar_height - margin
    draw.text((caption_x, caption_y), caption, fill='black', font=font_caption)
    
    # Add color scale legend (scaled)
    colorbar_y = canvas_height - colorbar_height + 60
    colorbar_width = 1800  # 3x larger
    colorbar_x = (canvas_width - colorbar_width) // 2
    
    # Draw gradient colorbar (red to white to blue)
    for i in range(colorbar_width):
        ratio = i / colorbar_width
        if ratio < 0.5:
            # Red to white
            r = 255
            g = int(255 * (ratio * 2))
            b = int(255 * (ratio * 2))
        else:
            # White to blue
            r = int(255 * (2 - ratio * 2))
            g = int(255 * (2 - ratio * 2))
            b = 255
        
        draw.line([(colorbar_x + i, colorbar_y), 
                   (colorbar_x + i, colorbar_y + 90)], 
                  fill=(r, g, b))
    
    # Draw colorbar border
    draw.rectangle([colorbar_x, colorbar_y, 
                    colorbar_x + colorbar_width, colorbar_y + 90], 
                   outline='black', width=6)
    
    # Add colorbar labels (larger font)
    try:
        font_colorbar = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 72)
    except:
        font_colorbar = font_caption
    
    draw.text((colorbar_x - 240, colorbar_y + 15), "-0.030", fill='black', font=font_colorbar)
    draw.text((colorbar_x + colorbar_width + 30, colorbar_y + 15), "0.030", fill='black', font=font_colorbar)
    
    # Save as TIFF with 900 DPI
    canvas.save(output_file, 'TIFF', dpi=(900, 900))
    print(f"\n✓ Saved: {output_file} (900 DPI, white background)")
    
    # Also save as PNG with white background
    png_file = output_file.replace('.tiff', '.png')
    canvas.save(png_file, 'PNG', dpi=(900, 900))
    print(f"✓ Saved: {png_file}")
    
    # Save as EPS (vector format for publishing)
    eps_file = output_file.replace('.tiff', '.eps')
    canvas.save(eps_file, 'EPS')
    print(f"✓ Saved: {eps_file}")


def create_homo_lumo_figure(molecules, output_file='Figure_HOMO_LUMO_900dpi.tiff'):
    """
    Create HOMO-LUMO comparison figure (similar to Fig. 10 reference)
    Layout: Grid with LUMO on top, energy gap in middle, HOMO on bottom
    """
    print(f"\nCreating HOMO-LUMO comparison figure...")
    
    # Load images
    data = []
    
    for mol_name, label in molecules:
        homo_file = f"{mol_name}_HOMO_Orbital_dpi900.png"
        lumo_file = f"{mol_name}_LUMO_Orbital_dpi900.png"
        
        homo_img = None
        lumo_img = None
        
        if os.path.exists(homo_file):
            homo_img = Image.open(homo_file)
            # Convert to RGB for white background
            if homo_img.mode != 'RGB':
                rgb_img = Image.new('RGB', homo_img.size, 'white')
                if homo_img.mode == 'RGBA':
                    rgb_img.paste(homo_img, (0, 0), homo_img)
                else:
                    rgb_img.paste(homo_img, (0, 0))
                homo_img = rgb_img
            print(f"  ✓ Loaded {homo_file}")
        else:
            print(f"  ✗ Missing {homo_file}")
            
        if os.path.exists(lumo_file):
            lumo_img = Image.open(lumo_file)
            # Convert to RGB for white background
            if lumo_img.mode != 'RGB':
                rgb_img = Image.new('RGB', lumo_img.size, 'white')
                if lumo_img.mode == 'RGBA':
                    rgb_img.paste(lumo_img, (0, 0), lumo_img)
                else:
                    rgb_img.paste(lumo_img, (0, 0))
                lumo_img = rgb_img
            print(f"  ✓ Loaded {lumo_file}")
        else:
            print(f"  ✗ Missing {lumo_file}")
        
        if homo_img and lumo_img:
            data.append({
                'name': mol_name,
                'label': label,
                'homo': homo_img,
                'lumo': lumo_img
            })
    
    if not data:
        print("No HOMO-LUMO image pairs found!")
        return
    
    n_molecules = len(data)
    
    # Resize images (scaled for 900 DPI)
    target_size = 1800  # 3x larger
    for item in data:
        item['homo'] = item['homo'].resize((target_size, target_size), Image.Resampling.LANCZOS)
        item['lumo'] = item['lumo'].resize((target_size, target_size), Image.Resampling.LANCZOS)
    
    # Calculate canvas dimensions (scaled)
    margin = 120  # 3x larger
    label_width = 360  # 3x larger
    header_height = 240  # 3x larger
    gap_box_height = 300  # 3x larger
    
    canvas_width = label_width + (target_size + margin) * n_molecules + margin
    canvas_height = header_height + target_size + gap_box_height + target_size + margin * 3
    
    # Create white canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    draw = ImageDraw.Draw(canvas)
    
    # Fonts (scaled for 900 DPI)
    try:
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 96)  # 3x larger
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 84)  # 3x larger
        font_value = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 72)  # 3x larger
        font_caption = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 78)  # Larger and bold
    except:
        font_header = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_value = ImageFont.load_default()
        font_caption = ImageFont.load_default()
    
    # Draw row labels
    lumo_y = header_height + margin
    gap_y = lumo_y + target_size + margin
    homo_y = gap_y + gap_box_height + margin
    
    draw.text((60, lumo_y + target_size//2 - 60), "LUMO", fill='black', font=font_label)
    draw.text((60, gap_y + gap_box_height//2 - 60), "ΔE", fill='black', font=font_label)
    draw.text((60, homo_y + target_size//2 - 60), "HOMO", fill='black', font=font_label)
    
    # Place images and labels for each molecule
    x_offset = label_width + margin
    
    for i, item in enumerate(data):
        # Column header
        header_text = f"{chr(65+i)}. {item['label']}"
        bbox = draw.textbbox((0, 0), header_text, font=font_header)
        text_width = bbox[2] - bbox[0]
        text_x = x_offset + (target_size - text_width) // 2
        draw.text((text_x, 60), header_text, fill='black', font=font_header)
        
        # LUMO image
        canvas.paste(item['lumo'], (x_offset, lumo_y))
        
        # Energy gap box (scaled)
        gap_box_x = x_offset + target_size//2 - 300
        gap_box_y = gap_y + gap_box_height//2 - 90
        
        draw.rectangle([gap_box_x - 30, gap_box_y - 30,
                       gap_box_x + 660, gap_box_y + 150],
                      outline='black', width=6)
        
        # Energy gap values (calculated from DFT data)
        gap_values = {
            'control': '5.61 eV',
            'lupeol': '7.26 eV',
            'hedragenin': '4.92 eV',
            'maslinic_acid': '4.95 eV'
        }
        
        gap_value = gap_values.get(item['name'], '0.XXXX')
        gap_text = f"ΔE = {gap_value}" 
        draw.text((gap_box_x, gap_box_y), gap_text, fill='black', font=font_value)
        
        # Arrow (scaled)
        arrow_x = x_offset + target_size//2
        arrow_top = gap_box_y - 60
        arrow_bottom = gap_box_y + 180
        
        draw.line([(arrow_x, lumo_y + target_size + 30),
                   (arrow_x, arrow_top)], fill='black', width=9)
        draw.line([(arrow_x, arrow_bottom),
                   (arrow_x, homo_y - 30)], fill='black', width=9)
        
        # Arrow heads (scaled)
        draw.polygon([(arrow_x, arrow_top - 45),
                     (arrow_x - 24, arrow_top),
                     (arrow_x + 24, arrow_top)], fill='black')
        draw.polygon([(arrow_x, arrow_bottom + 45),
                     (arrow_x - 24, arrow_bottom),
                     (arrow_x + 24, arrow_bottom)], fill='black')
        
        # HOMO image
        canvas.paste(item['homo'], (x_offset, homo_y))
        
        x_offset += target_size + margin
    
    # Add caption with larger font
    caption = "HOMO-LUMO orbitals and energy gaps. Red and green denote orbital phases; ΔE reflects chemical reactivity."
    
    # Word wrap caption
    words = caption.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font_caption)
        if bbox[2] - bbox[0] > canvas_width - 300:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw caption lines
    caption_y = canvas_height - 180
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_caption)
        text_width = bbox[2] - bbox[0]
        text_x = (canvas_width - text_width) // 2
        draw.text((text_x, caption_y), line, fill='black', font=font_caption)
        caption_y += 90
    
    # Save as TIFF with 900 DPI
    canvas.save(output_file, 'TIFF', dpi=(900, 900))
    print(f"\n✓ Saved: {output_file} (900 DPI, white background)")
    
    # Also save as PNG with white background
    png_file = output_file.replace('.tiff', '.png')
    canvas.save(png_file, 'PNG', dpi=(900, 900))
    print(f"✓ Saved: {png_file}")
    
    # Save as EPS (vector format for publishing)
    eps_file = output_file.replace('.tiff', '.eps')
    canvas.save(eps_file, 'EPS')
    print(f"✓ Saved: {eps_file}")


def main():
    """Main execution"""
    print("=" * 60)
    print("Molecular Visualization Figure Compositor (900 DPI)")
    print("White background version for publishing")
    print("=" * 60)
    
    # Define your molecules matching your actual filenames
    molecules = [
    ('control', 'Oleanolic Acid (Control)'),      # Added full name
    ('hedragenin', 'Hederagenin Analogue'),       # Fixed spelling
    ('lupeol', 'Lupeol Analogue'),
    ('maslinic_acid', 'Maslinic Acid Analogue')
]
    
    # Create ESP surface comparison
    create_esp_figure(molecules, 'Figure_ESP_Surfaces_900dpi.tiff')
    
    # Create HOMO-LUMO comparison
    create_homo_lumo_figure(molecules, 'Figure_HOMO_LUMO_900dpi.tiff')
    
    print("\n" + "=" * 60)
    print("Done! Publication-ready figures created at 900 DPI")
    print("All figures have solid white backgrounds for publishing")
    print("Files saved as TIFF, PNG, and EPS formats")
    print("=" * 60)


if __name__ == "__main__":
    main()
