import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats
import os
import re

# Set matplotlib to use Agg backend
import matplotlib
matplotlib.use('Agg')

# Set clean style
sns.set_style("white")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

def read_xvg_safe(filename):
    """Safely read XVG files"""
    pc1, pc2 = [], []
    try:
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('#') or line.startswith('@') or line.strip() == '':
                    continue
                parts = line.strip().split()
                numeric_parts = []
                for part in parts:
                    try:
                        numeric_parts.append(float(part))
                    except ValueError:
                        continue
                
                if len(numeric_parts) >= 2:
                    pc1.append(numeric_parts[0])
                    pc2.append(numeric_parts[1])
        
        return np.array(pc1), np.array(pc2)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return np.array([]), np.array([])

def parse_prob_xpm_file(xpm_file):
    """Parse GROMACS probability XPM file"""
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

def create_fel_from_probability(prob_matrix):
    """Convert probability matrix to Free Energy Landscape"""
    if prob_matrix is None:
        return None
        
    kT = 2.494  # kJ/mol at 300K
    min_prob = np.min(prob_matrix[prob_matrix > 0])
    prob_matrix = np.where(prob_matrix > 0, prob_matrix, min_prob * 0.1)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        free_energy = -kT * np.log(prob_matrix)
        free_energy[~np.isfinite(free_energy)] = np.max(free_energy[np.isfinite(free_energy)])
        free_energy = free_energy - np.min(free_energy)
    
    return free_energy

# Systems data
systems = {
    'A) Control Complex': ('control_2d_projection.xvg', 'control_prob.xpm'),
    'B) Hedragenin Analogue Complex': ('hedragenin_2d_projection.xvg', 'hedragenin_prob.xpm'),
    'C) Lupeol Analogue Complex': ('lupeol_2d_projection.xvg', 'lupeol_prob.xpm'),
    'D) Maslinic Acid Analogue Complex': ('maslinic_acid_2d_projection.xvg', 'maslinic_acid_prob.xpm')
}

# --- MODIFICATION START ---

# Create figure with 8 subplots (4 PCA + 4 FEL)
# Changed figsize to (20, 10) for a wider, more appropriate aspect ratio
fig = plt.figure(figsize=(20, 10), facecolor='white')

# Add main title
# Lowered title from y=0.98 to y=0.95 to give it space
fig.suptitle('Principal Component Analysis (PCA) and Free Energy Landscape (FEL) Models', 
             fontsize=16, fontweight='normal', y=0.95)

# Define positions for subplots [left, bottom, width, height]
# Recalculated all positions for better spacing
plot_width = 0.18
plot_height = 0.35
pca_bottom = 0.55
fel_bottom = 0.1
left_1 = 0.07
left_2 = 0.30
left_3 = 0.53
left_4 = 0.76

# Top 4 rows: PCA
pca_positions = [
    [left_1, pca_bottom, plot_width, plot_height],  # A) PCA
    [left_2, pca_bottom, plot_width, plot_height],  # B) PCA
    [left_3, pca_bottom, plot_width, plot_height],  # C) PCA
    [left_4, pca_bottom, plot_width, plot_height]   # D) PCA
]

# Bottom 4 rows: FEL
fel_positions = [
    [left_1, fel_bottom, plot_width, plot_height],  # A) FEL
    [left_2, fel_bottom, plot_width, plot_height],  # B) FEL
    [left_3, fel_bottom, plot_width, plot_height],  # C) FEL
    [left_4, fel_bottom, plot_width, plot_height]   # D) FEL
]

# --- MODIFICATION END ---


# Create a darker version of YlOrRd colormap
# This makes the light yellows more visible
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap

# Custom colormap: darker yellows to reds
colors = ['#FFA500', '#FF8C00', '#FF7F00', '#FF6347', '#FF4500', '#DC143C', '#8B0000']
n_bins = 100
cmap_name = 'DarkYlOrRd'
cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

# Plot PCA (top row)
print("\n=== Generating PCA Plots ===")
for idx, (system_name, (xvg_file, _)) in enumerate(systems.items()):
    ax = fig.add_axes(pca_positions[idx])
    
    if os.path.exists(xvg_file):
        pc1, pc2 = read_xvg_safe(xvg_file)
        
        if len(pc1) > 100:
            # Hexbin with darker colormap
            h = ax.hexbin(pc1, pc2, gridsize=50, cmap=cm, 
                         mincnt=1, linewidths=0.2, alpha=0.9)
            
            # Add contour lines
            try:
                xmin, xmax = pc1.min(), pc1.max()
                ymin, ymax = pc2.min(), pc2.max()
                xpad = (xmax - xmin) * 0.1
                ypad = (ymax - ymin) * 0.1
                
                xx, yy = np.mgrid[xmin-xpad:xmax+xpad:100j, ymin-ypad:ymax+ypad:100j]
                positions_kde = np.vstack([xx.ravel(), yy.ravel()])
                values = np.vstack([pc1, pc2])
                kernel = stats.gaussian_kde(values)
                f = np.reshape(kernel(positions_kde).T, xx.shape)
                
                ax.contour(xx, yy, f, colors='black', alpha=0.3, 
                          linewidths=0.5, levels=5)
            except Exception as e:
                print(f"Skipping contours for {system_name}: {e}")
            
            ax.set_title(system_name, fontsize=11, fontweight='normal', pad=8)
            ax.set_xlabel('Principal Component 1 (PC1)', fontsize=9)
            ax.set_ylabel('Principal Component 2 (PC2)', fontsize=9)
            
            ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='gray')
            ax.set_axisbelow(True)
            
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(0.8)
            
            ax.tick_params(labelsize=8, length=3, width=0.8)
            
            # Add colorbar
            cbar = plt.colorbar(h, ax=ax, pad=0.02, fraction=0.046)
            cbar.set_label('Count', fontsize=8, labelpad=6)
            cbar.ax.tick_params(labelsize=7, length=2)
            cbar.outline.set_linewidth(0.8)
            
            print(f"âœ“ PCA: {system_name} ({len(pc1)} points)")
        else:
            ax.text(0.5, 0.5, f'Insufficient data', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=9, style='italic', color='gray')
    else:
        ax.text(0.5, 0.5, 'File not found', 
               ha='center', va='center', transform=ax.transAxes,
               fontsize=9, style='italic', color='gray')
    
    ax.set_title(system_name, fontsize=11, fontweight='normal', pad=8)
    ax.set_xlabel('Principal Component 1 (PC1)', fontsize=9)
    ax.set_ylabel('Principal Component 2 (PC2)', fontsize=9)
    
    for spine in ax.spines.values():
        spine.set_color('black')
        spine.set_linewidth(0.8)
    ax.tick_params(labelsize=8, length=3, width=0.8)

# Plot FEL (bottom row)
print("\n=== Generating FEL Plots ===")
for idx, (system_name, (_, xpm_file)) in enumerate(systems.items()):
    ax = fig.add_axes(fel_positions[idx])
    
    if os.path.exists(xpm_file):
        prob_matrix = parse_prob_xpm_file(xpm_file)
        
        if prob_matrix is not None:
            fel_matrix = create_fel_from_probability(prob_matrix)
            
            if fel_matrix is not None:
                # Keep original viridis colormap
                im = ax.imshow(fel_matrix, cmap='viridis', 
                             aspect='auto', interpolation='bilinear', 
                             origin='lower')
                
                # Add contour lines
                levels = np.linspace(np.min(fel_matrix), np.max(fel_matrix), 8)
                ax.contour(fel_matrix, levels=levels, colors='white', 
                          alpha=0.3, linewidths=0.5)
                
                ax.set_title(system_name, fontsize=11, fontweight='normal', pad=8)
                ax.set_xlabel('PC1', fontsize=9)
                ax.set_ylabel('PC2', fontsize=9)
                
                for spine in ax.spines.values():
                    spine.set_color('black')
                    spine.set_linewidth(0.8)
                
                ax.tick_params(labelsize=8, length=3, width=0.8)
                
                # Add colorbar
                cbar = plt.colorbar(im, ax=ax, pad=0.02, fraction=0.046)
                cbar.set_label('G (kJ/mol)', fontsize=8, labelpad=6)
                cbar.ax.tick_params(labelsize=7, length=2)
                cbar.outline.set_linewidth(0.8)
                
                print(f"âœ“ FEL: {system_name}")
            else:
                ax.text(0.5, 0.5, 'FEL failed', 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=9, style='italic', color='gray')
        else:
            ax.text(0.5, 0.5, 'Parse error', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=9, style='italic', color='gray')
    else:
        ax.text(0.5, 0.5, 'File not found', 
               ha='center', va='center', transform=ax.transAxes,
               fontsize=9, style='italic', color='gray')
    
    ax.set_title(system_name, fontsize=11, fontweight='normal', pad=8)
    ax.set_xlabel('PC1', fontsize=9)
    ax.set_ylabel('PC2', fontsize=9)
    
    for spine in ax.spines.values():
        spine.set_color('black')
        spine.set_linewidth(0.8)
    ax.tick_params(labelsize=8, length=3, width=0.8)

# Save with high quality
plt.savefig('combined_pca_fel_publication_FIXED.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.savefig('combined_pca_fel_publication_FIXED.eps', format='eps', dpi=300, 
            bbox_inches='tight', facecolor='white', edgecolor='none')
print("\nâœ“ Saved combined_pca_fel_publication_FIXED.png and .eps")
plt.close()
