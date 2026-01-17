import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os
import re

# Set matplotlib to use Agg backend
import matplotlib
matplotlib.use('Agg')

# Set clean style
sns.set_style("white")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

def parse_prob_xpm_file(xpm_file):
    """Parse GROMACS probability XPM file - FIXED VERSION"""
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
        
        # Parse color map - FIXED REGEX
        color_dict = {}
        for line in lines:
            # Match: "A  c #000000 " /* "0" */,
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
    
    # Avoid log(0) issues
    min_prob = np.min(prob_matrix[prob_matrix > 0])
    prob_matrix = np.where(prob_matrix > 0, prob_matrix, min_prob * 0.1)
    
    # Convert to free energy
    with np.errstate(divide='ignore', invalid='ignore'):
        free_energy = -kT * np.log(prob_matrix)
        free_energy[~np.isfinite(free_energy)] = np.max(free_energy[np.isfinite(free_energy)])
        free_energy = free_energy - np.min(free_energy)
    
    return free_energy

# Systems data for FELs
systems_fel = {
    'A) Control Complex': 'control_prob.xpm',
    'B) Hedragenin Analogue Complex': 'hedragenin_prob.xpm',  
    'C) Lupeol Analogue Complex': 'lupeol_prob.xpm',
    'D) Maslinic Acid Analogue Complex': 'maslinic_acid_prob.xpm'
}

# Create figure
fig = plt.figure(figsize=(14, 10), facecolor='white')

# Add main title
fig.suptitle('Comparative Free Energy Landscape Analysis', 
             fontsize=16, fontweight='normal', y=0.96)

# Define positions for subplots
positions = [
    (0.08, 0.53, 0.37, 0.37),  # A) Top-left
    (0.55, 0.53, 0.37, 0.37),  # B) Top-right
    (0.08, 0.08, 0.37, 0.37),  # C) Bottom-left
    (0.55, 0.08, 0.37, 0.37)   # D) Bottom-right
]

for idx, (system_name, xpm_file) in enumerate(systems_fel.items()):
    ax = fig.add_axes(positions[idx])
    
    try:
        if os.path.exists(xpm_file):
            prob_matrix = parse_prob_xpm_file(xpm_file)
            
            if prob_matrix is not None:
                fel_matrix = create_fel_from_probability(prob_matrix)
                
                if fel_matrix is not None:
                    # Plot FEL with clean colormap
                    im = ax.imshow(fel_matrix, cmap='viridis', 
                                 aspect='auto', interpolation='bilinear', 
                                 origin='lower')
                    
                    # Add contour lines
                    levels = np.linspace(np.min(fel_matrix), np.max(fel_matrix), 8)
                    ax.contour(fel_matrix, levels=levels, colors='white', 
                              alpha=0.3, linewidths=0.5)
                    
                    # Clean styling
                    ax.set_title(system_name, fontsize=12, fontweight='normal', pad=10)
                    ax.set_xlabel('PC1', fontsize=10)
                    ax.set_ylabel('PC2', fontsize=10)
                    
                    # Clean spines
                    for spine in ax.spines.values():
                        spine.set_color('black')
                        spine.set_linewidth(0.8)
                    
                    # Tick parameters
                    ax.tick_params(labelsize=9, length=3, width=0.8)
                    
                    # Add colorbar
                    cbar = plt.colorbar(im, ax=ax, pad=0.02)
                    cbar.set_label('Free Energy (kJ/mol)', fontsize=9, labelpad=8)
                    cbar.ax.tick_params(labelsize=8, length=2)
                    cbar.outline.set_linewidth(0.8)
                    
                    print(f"✓ Successfully plotted FEL for {system_name}")
                    
                else:
                    ax.text(0.5, 0.5, 'FEL calculation failed', 
                           ha='center', va='center', transform=ax.transAxes,
                           fontsize=10, style='italic', color='gray')
                    ax.set_title(system_name, fontsize=12, fontweight='normal', pad=10)
                    ax.set_xlabel('PC1', fontsize=10)
                    ax.set_ylabel('PC2', fontsize=10)
                    
                    for spine in ax.spines.values():
                        spine.set_color('black')
                        spine.set_linewidth(0.8)
                    ax.tick_params(labelsize=9, length=3, width=0.8)
                
            else:
                ax.text(0.5, 0.5, 'Error parsing data', 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=10, style='italic', color='gray')
                ax.set_title(system_name, fontsize=12, fontweight='normal', pad=10)
                ax.set_xlabel('PC1', fontsize=10)
                ax.set_ylabel('PC2', fontsize=10)
                
                for spine in ax.spines.values():
                    spine.set_color('black')
                    spine.set_linewidth(0.8)
                ax.tick_params(labelsize=9, length=3, width=0.8)
                
        else:
            ax.text(0.5, 0.5, 'File not found', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=10, style='italic', color='gray')
            ax.set_title(system_name, fontsize=12, fontweight='normal', pad=10)
            ax.set_xlabel('PC1', fontsize=10)
            ax.set_ylabel('PC2', fontsize=10)
            
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(0.8)
            ax.tick_params(labelsize=9, length=3, width=0.8)
            
    except Exception as e:
        print(f"Error processing {system_name}: {e}")
        ax.text(0.5, 0.5, 'Error loading data', 
               ha='center', va='center', transform=ax.transAxes,
               fontsize=10, style='italic', color='gray')
        ax.set_title(system_name, fontsize=12, fontweight='normal', pad=10)
        ax.set_xlabel('PC1', fontsize=10)
        ax.set_ylabel('PC2', fontsize=10)
        
        for spine in ax.spines.values():
            spine.set_color('black')
            spine.set_linewidth(0.8)
        ax.tick_params(labelsize=9, length=3, width=0.8)

# Save with high quality
plt.savefig('comparative_fels_clean.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.savefig('comparative_fels_clean.eps', format='eps', dpi=300, 
            bbox_inches='tight', facecolor='white', edgecolor='none')
print("✓ Saved comparative_fels_clean.png and comparative_fels_clean.eps")
plt.close()
