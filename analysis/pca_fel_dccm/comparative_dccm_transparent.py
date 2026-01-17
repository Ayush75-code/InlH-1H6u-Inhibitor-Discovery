#!/usr/bin/env python3
"""
Comparative DCCM Analysis with Transparent Background
Fixed aspect ratios and proper spacing
"""
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os
import re

# Set matplotlib backend
import matplotlib
matplotlib.use('Agg')

# Set clean style with transparent background
sns.set_style("white")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['savefig.transparent'] = True

def parse_xpm_file(xpm_file):
    """Parse GROMACS XPM file"""
    try:
        with open(xpm_file, 'r') as f:
            lines = f.readlines()
        
        # Find dimensions
        width, height, ncolors = None, None, None
        for line in lines[:30]:
            match = re.search(r'"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"', line)
            if match:
                width = int(match.group(1))
                height = int(match.group(2))
                ncolors = int(match.group(3))
                break
        
        if not width:
            return None
        
        # Parse color map
        color_dict = {}
        for line in lines:
            match = re.match(r'"(.)\s+c\s+\S+\s+"\s*/\*\s*"([^"]*)"', line)
            if match:
                char = match.group(1)
                value_str = match.group(2).strip()
                try:
                    value = float(value_str)
                    color_dict[char] = value
                except ValueError:
                    pass
        
        if len(color_dict) == 0:
            return None
        
        # Parse data matrix
        matrix_data = []
        reading_data = False
        
        for line in lines:
            if line.strip().startswith('"') and ' c ' not in line and '/*' not in line:
                reading_data = True
                
            if reading_data and line.strip().startswith('"'):
                match = re.search(r'"([^"]+)"', line)
                if match:
                    row_chars = match.group(1)
                    row_values = [color_dict.get(c, 0.0) for c in row_chars]
                    
                    if len(row_values) == width:
                        matrix_data.append(row_values)
                    
                    if len(matrix_data) >= height:
                        break
        
        return np.array(matrix_data) if matrix_data else None
        
    except Exception as e:
        print(f"Error parsing {xpm_file}: {e}")
        return None

# Systems data
systems = {
    'A) Control Complex': 'control_covar.xpm',
    'B) Hedragenin Analogue Complex': 'hedragenin_covar.xpm',  
    'C) Lupeol Analogue Complex': 'lupeol_covar.xpm',
    'D) Maslinic Acid Analogue Complex': 'maslinic_acid_covar.xpm'
}

# Create figure with TRANSPARENT background
fig = plt.figure(figsize=(16, 12), facecolor='none')

# Add main title
fig.suptitle('Comparative Dynamic Cross-Correlation Matrix Analysis', 
             fontsize=16, fontweight='normal', y=0.96)

# Define positions for subplots - FIXED for equal sizes
plot_size = 0.38  # Square plots
left_margin = 0.08
right_col = 0.54
top_row = 0.54
bottom_row = 0.08

positions = [
    [left_margin, top_row, plot_size, plot_size],      # A) Top-left
    [right_col, top_row, plot_size, plot_size],        # B) Top-right
    [left_margin, bottom_row, plot_size, plot_size],   # C) Bottom-left
    [right_col, bottom_row, plot_size, plot_size]      # D) Bottom-right
]

# Collect all matrices to find global range
all_matrices = {}
for system_name, xpm_file in systems.items():
    if os.path.exists(xpm_file):
        matrix = parse_xpm_file(xpm_file)
        if matrix is not None:
            all_matrices[system_name] = matrix

# Find global percentile-based range
if all_matrices:
    all_values = np.concatenate([m.flatten() for m in all_matrices.values()])
    percentile_min = np.percentile(all_values, 2)
    percentile_max = np.percentile(all_values, 98)
    vmax = max(abs(percentile_min), abs(percentile_max))
    vmin = -vmax
    
    print(f"Using symmetric scale: [{vmin:.4f}, {vmax:.4f}]")
else:
    vmin, vmax = -0.1, 0.1

# Plot all systems
for idx, (system_name, xpm_file) in enumerate(systems.items()):
    ax = fig.add_axes(positions[idx])
    ax.set_facecolor('none')  # Transparent background
    
    try:
        if system_name in all_matrices:
            dccm_matrix = all_matrices[system_name]
            
            # Plot DCCM with enhanced contrast
            im = ax.imshow(dccm_matrix, cmap='RdBu_r', vmin=vmin, vmax=vmax,
                         aspect='equal', interpolation='nearest')
            
            # Clean styling
            ax.set_title(system_name, fontsize=11, fontweight='normal', pad=8)
            ax.set_xlabel('Residue Index', fontsize=10)
            ax.set_ylabel('Residue Index', fontsize=10)
            
            # Clean spines
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(0.8)
            
            # Tick parameters
            ax.tick_params(labelsize=9, length=3, width=0.8)
            
            # Add colorbar with better formatting
            cbar = plt.colorbar(im, ax=ax, pad=0.02, fraction=0.046)
            cbar.set_label('Covariance (nm²)', fontsize=9, labelpad=8)
            cbar.ax.tick_params(labelsize=8, length=2)
            cbar.outline.set_linewidth(0.8)
            cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
            
            print(f"✓ Successfully plotted DCCM for {system_name}")
            print(f"   Range: [{dccm_matrix.min():.4f}, {dccm_matrix.max():.4f}]")
            
        elif os.path.exists(xpm_file):
            ax.text(0.5, 0.5, 'Error parsing data', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=10, style='italic', color='gray')
            ax.set_title(system_name, fontsize=11, fontweight='normal', pad=8)
            ax.set_xlabel('Residue Index', fontsize=10)
            ax.set_ylabel('Residue Index', fontsize=10)
            ax.set_aspect('equal')
            
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(0.8)
            ax.tick_params(labelsize=9, length=3, width=0.8)
        else:
            ax.text(0.5, 0.5, 'File not found', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=10, style='italic', color='gray')
            ax.set_title(system_name, fontsize=11, fontweight='normal', pad=8)
            ax.set_xlabel('Residue Index', fontsize=10)
            ax.set_ylabel('Residue Index', fontsize=10)
            ax.set_aspect('equal')
            
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(0.8)
            ax.tick_params(labelsize=9, length=3, width=0.8)
            
    except Exception as e:
        print(f"Error processing {system_name}: {e}")
        ax.text(0.5, 0.5, 'Error loading data', 
               ha='center', va='center', transform=ax.transAxes,
               fontsize=10, style='italic', color='gray')
        ax.set_title(system_name, fontsize=11, fontweight='normal', pad=8)
        ax.set_xlabel('Residue Index', fontsize=10)
        ax.set_ylabel('Residue Index', fontsize=10)
        ax.set_aspect('equal')
        
        for spine in ax.spines.values():
            spine.set_color('black')
            spine.set_linewidth(0.8)
        ax.tick_params(labelsize=9, length=3, width=0.8)

# Save with TRANSPARENT background
plt.savefig('comparative_dccm_transparent.png', dpi=300, bbox_inches='tight',
            facecolor='none', edgecolor='none', transparent=True)
plt.savefig('comparative_dccm_transparent.eps', format='eps', dpi=300, 
            bbox_inches='tight', transparent=True)
print("\n✓ Saved comparative_dccm_transparent.png and .eps with TRANSPARENT background")
plt.close()

print("\n" + "="*60)
print("FEATURES:")
print("  ✓ Transparent background")
print("  ✓ Equal aspect ratios (square plots)")
print("  ✓ Consistent spacing")
print("  ✓ All subplots same size")
print("="*60)
