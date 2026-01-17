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

def parse_xpm_file(xpm_file):
    """Parse GROMACS XPM file - FIXED VERSION"""
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
            # Match: "A  c #0000FF " /* "-0.0143" */,
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

# Create figure
fig = plt.figure(figsize=(14, 10), facecolor='white')

# Add main title
fig.suptitle('Comparative Dynamic Cross-Correlation Matrix Analysis', 
             fontsize=16, fontweight='normal', y=0.96)

# Define positions for subplots
positions = [
    (0.08, 0.53, 0.37, 0.37),  # A) Top-left
    (0.55, 0.53, 0.37, 0.37),  # B) Top-right
    (0.08, 0.08, 0.37, 0.37),  # C) Bottom-left
    (0.55, 0.08, 0.37, 0.37)   # D) Bottom-right
]

# First pass: collect all matrices to find global range
all_matrices = {}
for system_name, xpm_file in systems.items():
    if os.path.exists(xpm_file):
        matrix = parse_xpm_file(xpm_file)
        if matrix is not None:
            all_matrices[system_name] = matrix

# Find global percentile-based range for better contrast
if all_matrices:
    all_values = np.concatenate([m.flatten() for m in all_matrices.values()])
    
    # Use percentile clipping for better visualization
    # This focuses on the main data distribution, not extreme outliers
    percentile_min = np.percentile(all_values, 2)
    percentile_max = np.percentile(all_values, 98)
    
    # Make symmetric around zero
    vmax = max(abs(percentile_min), abs(percentile_max))
    vmin = -vmax
    
    global_min = all_values.min()
    global_max = all_values.max()
    
    print(f"Full data range: [{global_min:.4f}, {global_max:.4f}]")
    print(f"98th percentile range: [{percentile_min:.4f}, {percentile_max:.4f}]")
    print(f"Using symmetric scale: [{vmin:.4f}, {vmax:.4f}]")
else:
    vmin, vmax = -0.1, 0.1

# Plot all systems
for idx, (system_name, xpm_file) in enumerate(systems.items()):
    ax = fig.add_axes(positions[idx])
    
    try:
        if system_name in all_matrices:
            dccm_matrix = all_matrices[system_name]
            
            # Plot DCCM with enhanced contrast
            im = ax.imshow(dccm_matrix, cmap='RdBu_r', vmin=vmin, vmax=vmax,
                         aspect='auto', interpolation='nearest')
            
            # Clean styling
            ax.set_title(system_name, fontsize=12, fontweight='normal', pad=10)
            ax.set_xlabel('Residue Index', fontsize=10)
            ax.set_ylabel('Residue Index', fontsize=10)
            
            # Clean spines
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(0.8)
            
            # Tick parameters
            ax.tick_params(labelsize=9, length=3, width=0.8)
            
            # Add colorbar with better formatting
            cbar = plt.colorbar(im, ax=ax, pad=0.02)
            cbar.set_label('Covariance (nm²)', fontsize=9, labelpad=8)
            cbar.ax.tick_params(labelsize=8, length=2)
            cbar.outline.set_linewidth(0.8)
            
            # Format colorbar tick labels to show more precision
            cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}'))
            
            print(f"✓ Successfully plotted DCCM for {system_name}")
            print(f"   Range: [{dccm_matrix.min():.4f}, {dccm_matrix.max():.4f}]")
            
        elif os.path.exists(xpm_file):
            ax.text(0.5, 0.5, 'Error parsing data', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=10, style='italic', color='gray')
            ax.set_title(system_name, fontsize=12, fontweight='normal', pad=10)
            ax.set_xlabel('Residue Index', fontsize=10)
            ax.set_ylabel('Residue Index', fontsize=10)
            
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(0.8)
            ax.tick_params(labelsize=9, length=3, width=0.8)
        else:
            ax.text(0.5, 0.5, 'File not found', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=10, style='italic', color='gray')
            ax.set_title(system_name, fontsize=12, fontweight='normal', pad=10)
            ax.set_xlabel('Residue Index', fontsize=10)
            ax.set_ylabel('Residue Index', fontsize=10)
            
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
        ax.set_xlabel('Residue Index', fontsize=10)
        ax.set_ylabel('Residue Index', fontsize=10)
        
        for spine in ax.spines.values():
            spine.set_color('black')
            spine.set_linewidth(0.8)
        ax.tick_params(labelsize=9, length=3, width=0.8)

# Save with high quality
plt.savefig('comparative_dccm_clean.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.savefig('comparative_dccm_clean.eps', format='eps', dpi=300, 
            bbox_inches='tight', facecolor='white', edgecolor='none')
print("\n✓ Saved comparative_dccm_clean.png and comparative_dccm_clean.eps")
plt.close()
