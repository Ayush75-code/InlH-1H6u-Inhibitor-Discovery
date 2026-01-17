import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats
import os

# Set matplotlib to use Agg backend
import matplotlib
matplotlib.use('Agg')

# Set clean style
sns.set_style("white")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

# Systems data
systems = {
    'A) Control Complex': 'control_proj_pc1_pc2.xvg',
    'B) Hedragenin Analogue Complex': 'hedragenin_proj_pc1_pc2.xvg', 
    'C) Lupeol Analogue Complex': 'lupeol_proj_pc1_pc2.xvg',
    'D) Maslinic Acid Analogue Complex': 'maslinic_acid_proj_pc1_pc2.xvg'
}

def read_xvg_safe(filename):
    """Safely read XVG files with inconsistent columns"""
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
        
        print(f"Read {len(pc1)} data points from {filename}")
        return np.array(pc1), np.array(pc2)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return np.array([]), np.array([])

# Create figure
fig = plt.figure(figsize=(14, 10), facecolor='white')

# Add main title
fig.suptitle('Comparative PCA of Protein Dynamics', 
             fontsize=16, fontweight='normal', y=0.96)

# Define positions for subplots [left, bottom, width, height]
positions = [
    [0.08, 0.53, 0.37, 0.37],
    [0.55, 0.53, 0.37, 0.37],
    [0.08, 0.08, 0.37, 0.37],
    [0.55, 0.08, 0.37, 0.37]
]

for idx, (system_name, filename) in enumerate(systems.items()):
    ax = fig.add_axes(positions[idx])
    
    try:
        if not os.path.exists(filename):
            ax.text(0.5, 0.5, 'File not found', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=10, style='italic', color='gray')
            ax.set_title(system_name, fontsize=12, fontweight='normal', pad=10)
            ax.set_xlabel('Principal Component 1 (PC1)', fontsize=10)
            ax.set_ylabel('Principal Component 2 (PC2)', fontsize=10)
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(0.8)
            ax.tick_params(labelsize=9, length=3, width=0.8)
            continue
        
        pc1, pc2 = read_xvg_safe(filename)
        
        if len(pc1) > 100:
            h = ax.hexbin(pc1, pc2, gridsize=50, cmap='YlOrRd', 
                         mincnt=1, linewidths=0.2, alpha=0.9)
            
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
            
            ax.set_title(system_name, fontsize=12, fontweight='normal', pad=10)
            ax.set_xlabel('Principal Component 1 (PC1)', fontsize=10)
            ax.set_ylabel('Principal Component 2 (PC2)', fontsize=10)
            ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='gray')
            ax.set_axisbelow(True)
            
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(0.8)
            
            ax.tick_params(labelsize=9, length=3, width=0.8)
            
            cbar = plt.colorbar(h, ax=ax, pad=0.02)
            cbar.set_label('Time (ns)', fontsize=9, labelpad=8)
            cbar.ax.tick_params(labelsize=8, length=2)
            cbar.outline.set_linewidth(0.8)
            
            print(f"✓ Successfully plotted {system_name} with {len(pc1)} points")
        else:
            ax.text(0.5, 0.5, f'Insufficient data\n({len(pc1)} points)', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=10, style='italic', color='gray')
            ax.set_title(system_name, fontsize=12, fontweight='normal', pad=10)
            ax.set_xlabel('Principal Component 1 (PC1)', fontsize=10)
            ax.set_ylabel('Principal Component 2 (PC2)', fontsize=10)
            
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
        ax.set_xlabel('Principal Component 1 (PC1)', fontsize=10)
        ax.set_ylabel('Principal Component 2 (PC2)', fontsize=10)
        
        for spine in ax.spines.values():
            spine.set_color('black')
            spine.set_linewidth(0.8)
        ax.tick_params(labelsize=9, length=3, width=0.8)

plt.savefig('comparative_pca_clean.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.savefig('comparative_pca_clean.eps', format='eps', dpi=300, 
            bbox_inches='tight', facecolor='white', edgecolor='none')
print("✓ Saved comparative_pca_clean.png and comparative_pca_clean.eps")
plt.close()
