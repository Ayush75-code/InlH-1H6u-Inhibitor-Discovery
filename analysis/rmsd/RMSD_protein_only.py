import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import sys
import warnings

def load_xvg_data(filename):
    """
    Loads data from a GROMACS .xvg file.
    """
    filtered_lines = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                # Skip header/comment/special lines
                if not line.strip().startswith(('@', '#', '&')):
                    filtered_lines.append(line)
    except FileNotFoundError:
        print(f"Warning: File not found: {filename}. Skipping this plot.", file=sys.stderr)
        return pd.DataFrame(columns=['Time (ns)', 'RMSD (nm)'])
    except Exception as e:
        print(f"Error reading {filename}: {e}", file=sys.stderr)
        return pd.DataFrame(columns=['Time (ns)', 'RMSD (nm)'])

    if not filtered_lines:
        print(f"Warning: No data found in {filename} after filtering.", file=sys.stderr)
        return pd.DataFrame(columns=['Time (ns)', 'RMSD (nm)'])

    try:
        data_io = StringIO("".join(filtered_lines))
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            df = pd.read_csv(
                data_io,
                sep='\s+', 
                header=None,
                names=['Time (ns)', 'RMSD (nm)'],
                dtype={'Time (ns)': float, 'RMSD (nm)': float},
                engine='python'
            )
        return df
    except Exception as e:
        print(f"Error parsing data from {filename}: {e}", file=sys.stderr)
        return pd.DataFrame(columns=['Time (ns)', 'RMSD (nm)'])

def plot_rmsd_on_ax(ax, backbone_file, title, backbone_color='blue'):
    """
    Plots ONLY backbone RMSD data on a given matplotlib axes object.
    """
    # Load data
    df_backbone = load_xvg_data(backbone_file)

    # Plot data if DataFrame is not empty
    if not df_backbone.empty:
        ax.plot(df_backbone['Time (ns)'], df_backbone['RMSD (nm)'], 
                label='Protein Backbone', color=backbone_color, linewidth=1.5)
    
    # Set subplot titles and labels
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('RMSD (nm)')
    
    # Set y-axis limit to emphasize stability (0 to 0.6 nm is appropriate for backbone)
    ax.set_ylim(0, 0.35) 
    
    # Set white background for this subplot
    ax.set_facecolor('white')
    
    # Add legend and grid
    if not df_backbone.empty:
        ax.legend(facecolor='white', edgecolor='black', loc='upper right')
    ax.grid(True, linestyle='--', alpha=0.6, color='gray')

# --- MAIN PLOTTING LOGIC ---
if __name__ == "__main__":
    
    # Set matplotlib to use white background globally
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['savefig.facecolor'] = 'white'
    
    # Create a 2x2 subplot grid
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 12))

    # --- Plot 1 (Top-Left) ---
    plot_rmsd_on_ax(axes[0, 0], 
                    backbone_file='Control_rmsd_backbone_corrected.xvg', 
                    title='A) Control Complex',
                    backbone_color='#1e3a8a')  # Dark Blue

    # --- Plot 2 (Top-Right) ---
    plot_rmsd_on_ax(axes[0, 1], 
                    backbone_file='Hedragenin_rmsd_backbone_corrected.xvg', 
                    title='B) Hederagenin Analogue Complex',
                    backbone_color='#15803d')  # Dark Green

    # --- Plot 3 (Bottom-Left) ---
    plot_rmsd_on_ax(axes[1, 0], 
                    backbone_file='Lupeol_rmsd_backbone_corrected.xvg', 
                    title='C) Lupeol Analogue Complex',
                    backbone_color='#7c3aed')  # Bright Purple

    # --- Plot 4 (Bottom-Right) ---
    plot_rmsd_on_ax(axes[1, 1], 
                    backbone_file='Maslinic_Acid_rmsd_backbone_corrected.xvg', 
                    title='D) Maslinic Acid Analogue Complex',
                    backbone_color='#92400e')  # Dark Brown

    # Add a main title for the entire figure
    fig.suptitle('Protein Backbone Structural Stability Analysis (RMSD)', 
                 fontsize=18, fontweight='bold')

    # Set white background for the entire figure (explicit)
    fig.patch.set_facecolor('white')
    
    # Adjust layout
    fig.tight_layout(rect=[0, 0.03, 1, 0.96]) 
    
    # --- SAVING IN ALL FORMATS ---
    OUTPUT_FILENAME = 'RMSD_Protein_Stability_Final'
    
    # 1. PNG (High Res)
    plt.savefig(f'{OUTPUT_FILENAME}.png', dpi=600, facecolor='white', 
                edgecolor='white', bbox_inches='tight')
    
    # 2. TIFF (High Res - Publication Standard)
    plt.savefig(f'{OUTPUT_FILENAME}.tiff', dpi=600, facecolor='white', 
                edgecolor='white', bbox_inches='tight')
    
    # 3. EPS (Vector - Good for editing)
    plt.savefig(f'{OUTPUT_FILENAME}.eps', format='eps', dpi=600, facecolor='white', 
                edgecolor='white', bbox_inches='tight')
    
    # 4. PDF (Vector - Standard)
    plt.savefig(f'{OUTPUT_FILENAME}.pdf', format='pdf', facecolor='white', 
                edgecolor='white', bbox_inches='tight')
    
    # 5. SVG (Vector - Web/Inkscape)
    plt.savefig(f'{OUTPUT_FILENAME}.svg', format='svg', facecolor='white', 
                edgecolor='white', bbox_inches='tight')
    
    # 6. EMF (Optional - Good for Word/PowerPoint)
    try:
        import pyemf
        plt.savefig(f'{OUTPUT_FILENAME}.emf', format='emf', facecolor='white', 
                    edgecolor='white', bbox_inches='tight')
        print(f"Successfully generated: {OUTPUT_FILENAME}.png, .tiff, .eps, .pdf, .svg, .emf")
    except ImportError:
        print("Note: 'pyemf' library not installed. EMF file skipped.")
        print(f"Successfully generated: {OUTPUT_FILENAME}.png, .tiff, .eps, .pdf, .svg")
