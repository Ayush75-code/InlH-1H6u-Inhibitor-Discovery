#!/usr/bin/env python3
"""
Create publication-quality figure layouts from molecular visualization images
Matches the reference layout style with ESP surfaces and HOMO-LUMO orbitals
"""

from PIL import Image, ImageDraw, ImageFont
import os
import sys

def create_esp_figure(molecules, output_file='ESP_Surface_Comparison.png'):
    """
    Create ESP surface comparison figure (similar to Fig. 11 reference)
    Layout: Side-by-side ESP surfaces with labels
    """
    print(f"Creating ESP surface comparison figure...")
    
    # Load images
    images = []
    labels = []
    
    for mol_name, label in molecules:
        esp_file = f"{mol_name}_ESP_Surface.png"
        if os.path.exists(esp_file):
            img = Image.open(esp_file)
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            images.append(img)
            labels.append(label)
            print(f"  ✓ Loaded {esp_file}")
        else:
            print(f"  ✗ Missing {esp_file}")
    
    if not images:
        print("No ESP images found!")
        return
    
    # Calculate dimensions
    n_images = len(images)
    
    # Resize all images to same height
    target_height = 800
    resized_images = []
    for img in images:
        aspect = img.width / img.height
        new_width = int(target_height * aspect)
        resized = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
        resized_images.append(resized)
    
    # Calculate canvas size
    total_width = sum(img.width for img in resized_images)
    margin = 50
    label_height = 80
    colorbar_height = 100
    
    canvas_width = total_width + margin * (n_images + 1)
    canvas_height = target_height + label_height + colorbar_height + margin * 3
    
    # Create transparent canvas
    canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)
    
    # Try to load a font
    try:
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_caption = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
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
    
    # Add caption
    caption = "Molecular electrostatic potential (MEP) surface analysis"
    bbox = draw.textbbox((0, 0), caption, font=font_caption)
    caption_width = bbox[2] - bbox[0]
    caption_x = (canvas_width - caption_width) // 2
    caption_y = canvas_height - colorbar_height - margin
    draw.text((caption_x, caption_y), caption, fill='black', font=font_caption)
    
    # Add color scale legend
    colorbar_y = canvas_height - colorbar_height + 20
    colorbar_width = 600
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
                   (colorbar_x + i, colorbar_y + 30)], 
                  fill=(r, g, b))
    
    # Draw colorbar border
    draw.rectangle([colorbar_x, colorbar_y, 
                    colorbar_x + colorbar_width, colorbar_y + 30], 
                   outline='black', width=2)
    
    # Add colorbar labels
    draw.text((colorbar_x - 80, colorbar_y + 5), "-0.030", fill='black', font=font_caption)
    draw.text((colorbar_x + colorbar_width + 10, colorbar_y + 5), "0.030", fill='black', font=font_caption)
    
    # Save with transparency
    canvas.save(output_file, 'PNG')
    print(f"\n✓ Saved: {output_file}")
    
    # For EPS, create a white background version
    canvas_white = Image.new('RGB', canvas.size, 'white')
    canvas_white.paste(canvas, (0, 0), canvas)
    eps_file = output_file.replace('.png', '.eps')
    canvas_white.save(eps_file, 'EPS')
    print(f"✓ Saved: {eps_file}")


def create_homo_lumo_figure(molecules, output_file='HOMO_LUMO_Comparison.png'):
    """
    Create HOMO-LUMO comparison figure (similar to Fig. 10 reference)
    Layout: Grid with LUMO on top, energy gap in middle, HOMO on bottom
    """
    print(f"\nCreating HOMO-LUMO comparison figure...")
    
    # Load images
    data = []
    
    for mol_name, label in molecules:
        homo_file = f"{mol_name}_HOMO_Orbital.png"
        lumo_file = f"{mol_name}_LUMO_Orbital.png"
        
        homo_img = None
        lumo_img = None
        
        if os.path.exists(homo_file):
            homo_img = Image.open(homo_file)
            if homo_img.mode != 'RGBA':
                homo_img = homo_img.convert('RGBA')
            print(f"  ✓ Loaded {homo_file}")
        else:
            print(f"  ✗ Missing {homo_file}")
            
        if os.path.exists(lumo_file):
            lumo_img = Image.open(lumo_file)
            if lumo_img.mode != 'RGBA':
                lumo_img = lumo_img.convert('RGBA')
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
    
    # Resize images
    target_size = 600
    for item in data:
        item['homo'] = item['homo'].resize((target_size, target_size), Image.Resampling.LANCZOS)
        item['lumo'] = item['lumo'].resize((target_size, target_size), Image.Resampling.LANCZOS)
    
    # Calculate canvas dimensions
    margin = 40
    label_width = 120
    header_height = 80
    gap_box_height = 100
    
    canvas_width = label_width + (target_size + margin) * n_molecules + margin
    canvas_height = header_height + target_size + gap_box_height + target_size + margin * 3
    
    # Create transparent canvas
    canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)
    
    # Fonts
    try:
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_value = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font_header = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_value = ImageFont.load_default()
    
    # Draw row labels
    lumo_y = header_height + margin
    gap_y = lumo_y + target_size + margin
    homo_y = gap_y + gap_box_height + margin
    
    draw.text((20, lumo_y + target_size//2 - 20), "LUMO", fill='black', font=font_label)
    draw.text((20, gap_y + gap_box_height//2 - 20), "ΔE", fill='black', font=font_label)
    draw.text((20, homo_y + target_size//2 - 20), "HOMO", fill='black', font=font_label)
    
    # Place images and labels for each molecule
    x_offset = label_width + margin
    
    for i, item in enumerate(data):
        # Column header
        header_text = f"{chr(65+i)}. {item['label']}"
        bbox = draw.textbbox((0, 0), header_text, font=font_header)
        text_width = bbox[2] - bbox[0]
        text_x = x_offset + (target_size - text_width) // 2
        draw.text((text_x, 20), header_text, fill='black', font=font_header)
        
        # LUMO image
        canvas.paste(item['lumo'], (x_offset, lumo_y))
        
        # Energy gap box (placeholder - you can add actual values)
        gap_box_x = x_offset + target_size//2 - 100
        gap_box_y = gap_y + gap_box_height//2 - 30
        
        draw.rectangle([gap_box_x - 10, gap_box_y - 10,
                       gap_box_x + 220, gap_box_y + 50],
                      outline='black', width=2)
        
     # Energy gap values (calculated from DFT data)
        gap_values = {
            'control': '5.6099',
            'lupeol': '7.2551',
            'hedragenin': '4.9239',
            'maslinic_acid': '4.9451'
        }
        
        gap_value = gap_values.get(item['name'], '0.XXXX')
        gap_text = f"ΔE = {gap_value}"
        draw.text((gap_box_x, gap_box_y), gap_text, fill='black', font=font_value)
        
        # Arrow
        arrow_x = x_offset + target_size//2
        arrow_top = gap_box_y - 20
        arrow_bottom = gap_box_y + 60
        
        draw.line([(arrow_x, lumo_y + target_size + 10),
                   (arrow_x, arrow_top)], fill='black', width=3)
        draw.line([(arrow_x, arrow_bottom),
                   (arrow_x, homo_y - 10)], fill='black', width=3)
        
        # Arrow heads
        draw.polygon([(arrow_x, arrow_top - 15),
                     (arrow_x - 8, arrow_top),
                     (arrow_x + 8, arrow_top)], fill='black')
        draw.polygon([(arrow_x, arrow_bottom + 15),
                     (arrow_x - 8, arrow_bottom),
                     (arrow_x + 8, arrow_bottom)], fill='black')
        
        # HOMO image
        canvas.paste(item['homo'], (x_offset, homo_y))
        
        x_offset += target_size + margin
    
    # Add caption
    caption = "HOMO-LUMO orbitals and energy gaps. Red and green denote orbital phases; ΔE reflects chemical reactivity."
    
    # Word wrap caption
    words = caption.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font_value)
        if bbox[2] - bbox[0] > canvas_width - 100:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw caption lines
    caption_y = canvas_height - 60
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_value)
        text_width = bbox[2] - bbox[0]
        text_x = (canvas_width - text_width) // 2
        draw.text((text_x, caption_y), line, fill='black', font=font_value)
        caption_y += 30
    
    # Save with transparency
    canvas.save(output_file, 'PNG')
    print(f"\n✓ Saved: {output_file}")
    
    # For EPS, create a white background version
    canvas_white = Image.new('RGB', canvas.size, 'white')
    canvas_white.paste(canvas, (0, 0), canvas)
    eps_file = output_file.replace('.png', '.eps')
    canvas_white.save(eps_file, 'EPS')
    print(f"✓ Saved: {eps_file}")


def main():
    """Main execution"""
    print("=" * 60)
    print("Molecular Visualization Figure Compositor")
    print("=" * 60)
    
    # Define your molecules in the correct order
    molecules = [
        ('control', 'Control'),
        ('hedragenin', 'Hedragenin Analogue'),
        ('lupeol', 'Lupeol Analogue'),
        ('maslinic_acid', 'Maslinic Acid Analogue')
    ]
    
    # Create ESP surface comparison
    create_esp_figure(molecules, 'Figure_ESP_Surfaces.png')
    
    # Create HOMO-LUMO comparison
    create_homo_lumo_figure(molecules, 'Figure_HOMO_LUMO.png')
    
    print("\n" + "=" * 60)
    print("Done! Your publication-ready figures are created.")
    print("=" * 60)


if __name__ == "__main__":
    main()
