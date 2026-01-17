import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import sys
import warnings

def load_xvg_data(filename):
    """
    Loads data from a GROMACS .xvg file.
    
    Skips lines starting with '@', '#', or '&'.
    Returns a pandas DataFrame with columns ['Time (ns)', 'RMSD (nm)'].
    Returns an empty DataFrame if the file is not found or is empty.
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
        # Use StringIO to read the list of strings as if it were a file
        data_io = StringIO("".join(filtered_lines))
        
        # Suppress the FutureWarning from pandas
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            df = pd.read_csv(
                data_io,
                sep='\s+',  # Use sep='\s+' instead of delim_whitespace=True
                header=None,
                names=['Time (ns)', 'RMSD (nm)'],
                dtype={'Time (ns)': float, 'RMSD (nm)': float},
                engine='python' # Use python engine for more robust sep handling
            )
        return df
    except Exception as e:
        print(f"Error parsing data from {filename}: {e}", file=sys.stderr)
        return pd.DataFrame(columns=['Time (ns)', 'RMSD (nm)'])

def plot_rmsd_on_ax(ax, backbone_file, ligand_file, title, backbone_color='blue', ligand_color='red'):
    """
    Plots backbone and ligand RMSD data on a given matplotlib axes object.
    
    Args:
        ax (matplotlib.axes.Axes): The subplot axes to plot on.
        backbone_file (str): Filename for the backbone RMSD .xvg file.
        ligand_file (str): Filename for the ligand RMSD .xvg file.
        title (str): The title for this subplot.
        backbone_color (str): Matplotlib color for the backbone plot.
        ligand_color (str): Matplotlib color for the ligand plot.
    """
    # Load data
    df_backbone = load_xvg_data(backbone_file)
    df_ligand = load_xvg_data(ligand_file)

    # Plot data if DataFrames are not empty
    if not df_backbone.empty:
        ax.plot(df_backbone['Time (ns)'], df_backbone['RMSD (nm)'], 
                label='Backbone', color=backbone_color, linewidth=1.5)
    
    if not df_ligand.empty:
        ax.plot(df_ligand['Time (ns)'], df_ligand['RMSD (nm)'], 
                label='Ligand', color=ligand_color, linewidth=1.5)

    # Set subplot titles and labels
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('RMSD (nm)')
    
    # Add legend and grid
    if not df_backbone.empty or not df_ligand.empty:
        ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)

# --- MAIN PLOTTING LOGIC ---
if __name__ == "__main__":
    
    # Create a 2x2 subplot grid
    # fig is the entire figure, axes is a 2D array of the 4 subplots
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 12))

   # --- Plot 1 (Top-Left) ---
    # Using a dark blue/bright red pair for maximum contrast
    plot_rmsd_on_ax(axes[0, 0], 
                    backbone_file='Control_rmsd_backbone.xvg', 
                    ligand_file='Control_rmsd_ligand.xvg', 
                    title='A) Control Complex',
                    backbone_color='#1e3a8a',  # Dark Blue
                    ligand_color='#dc2626')  # Bright Red

    # --- Plot 2 (Top-Right) ---
    # Using a dark green/bright orange pair
    plot_rmsd_on_ax(axes[0, 1], 
                    backbone_file='Hedragenin_rmsd_backbone.xvg', 
                    ligand_file='Hedragenin_rmsd_ligand.xvg', 
                    title='B) Hedragenin Analogue Complex',
                    backbone_color='#15803d',  # Dark Green
                    ligand_color='#f97316')  # Bright Orange

    # --- Plot 3 (Bottom-Left) ---
    # Using a dark purple/bright cyan pair
    plot_rmsd_on_ax(axes[1, 0], 
                    backbone_file='Lupeol_rmsd_backbone.xvg', 
                    ligand_file='Lupeol_rmsd_ligand.xvg', 
                    title='C) Lupeol Analogue Complex',
                    backbone_color='#7c3aed',  # Bright Purple
                    ligand_color='#06b6d4')  # Bright Cyan

    # --- Plot 4 (Bottom-Right) ---
    # Using a dark brown/bright magenta pair
    plot_rmsd_on_ax(axes[1, 1], 
                    backbone_file='Maslininc_Acid_rmsd_backbone.xvg', 
                    ligand_file='Maslinic_Acid_rmsd_ligand.xvg', 
                    title='D) Maslinic Acid Analogue Complex',
                    backbone_color='#92400e',  # Dark Brown
                    ligand_color='#ec4899')  # Bright Pink

    # Add a main title for the entire figure
    fig.suptitle('Comparative RMSD Analysis of Protein Backbone and Ligand Stability', fontsize=18, fontweight='bold')

    # Adjust layout to prevent labels from overlapping
    fig.tight_layout(rect=[0, 0.03, 1, 0.96]) # rect leaves space for suptitle

    # Save the final figure to a file
    output_filename = 'rmsd_subplot_comparison_final.png'
    plt.savefig(output_filename, dpi=300)
# Save the final figure as EPS
    output_filename = 'rmsd_subplot_comparison.eps'
    plt.savefig(output_filename, format='eps')
    print(f"Successfully generated subplot comparison plot: {output_filename}")

    # Optionally, uncomment the next line to show the plot interactively
    # plt.show()

