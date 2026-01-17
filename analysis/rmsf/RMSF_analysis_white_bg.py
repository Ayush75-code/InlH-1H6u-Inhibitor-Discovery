import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import sys
import warnings

def load_xvg_data(filename, x_col="X-Axis", y_col="Y-Axis"):
    """
    Loads data from a GROMACS .xvg file.
    
    Skips lines starting with '@', '#', or '&'.
    Returns a pandas DataFrame with specified column names.
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
        return pd.DataFrame(columns=[x_col, y_col])
    except Exception as e:
        print(f"Error reading {filename}: {e}", file=sys.stderr)
        return pd.DataFrame(columns=[x_col, y_col])

    if not filtered_lines:
        print(f"Warning: No data found in {filename} after filtering.", file=sys.stderr)
        return pd.DataFrame(columns=[x_col, y_col])

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
                names=[x_col, y_col], # Use the provided column names
                dtype={x_col: float, y_col: float},
                engine='python' 
            )
        return df
    except Exception as e:
        print(f"Error parsing data from {filename}: {e}", file=sys.stderr)
        return pd.DataFrame(columns=[x_col, y_col])

def plot_analysis_on_ax(ax, data_file, title, x_label, y_label, plot_color, legend_label):
    """
    Plots a single analysis (like Rg, RMSF, or SASA) on a given matplotlib axes.
    """
    # Load the data using our flexible function
    df = load_xvg_data(data_file, x_col=x_label, y_col=y_label)

    # Plot data if DataFrame is not empty
    if not df.empty:
        ax.plot(df[x_label], df[y_label], 
                label=legend_label, color=plot_color, linewidth=1.5)
    
    # Set subplot titles and labels
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    
    # Add legend and grid
    # --- THIS IS THE MODIFIED LINE ---
    # Only show legend if the dataframe is not empty AND legend_label is not empty
    if not df.empty and legend_label:
        ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)

# --- MAIN PLOTTING LOGIC ---
if __name__ == "__main__":
    
    # --- 1. CONFIGURE YOUR ANALYSIS ---
    
    # Change these 5 variables for each new analysis (RMSF, SASA, etc.)
    
    # For Radius of Gyration (Rg)
    MAIN_TITLE = 'Comparative Analysis of RMS Fluctuation'
    X_AXIS_LABEL = 'Residue Number'
    Y_AXIS_LABEL = 'RMSF (nm)'
   
    # --- TO REMOVE THE LEGEND, SET THIS TO '' ---
    LEGEND_LABEL = '' # Was 'Rg', now it's an empty string
    
    OUTPUT_FILENAME = 'RMSF_subplot_comparison_white_bg'

    # --- 2. DEFINE YOUR FILES AND SUBPLOTS ---
    # Create a 2x2 subplot grid
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 12))

    # --- Plot 1 (Top-Left) ---
    plot_analysis_on_ax(axes[0, 0], 
                        data_file='control_rmsf_per_residue.xvg', 
                        title='A) Control Complex Complex',
                        x_label=X_AXIS_LABEL, y_label=Y_AXIS_LABEL,
                        plot_color='#1e3a8a',  # Dark Blue
                        legend_label=LEGEND_LABEL)

    # --- Plot 2 (Top-Right) ---
    plot_analysis_on_ax(axes[0, 1], 
                        data_file='hedragenin_rmsf_per_residue.xvg', 
                        title='B) Hedragenin Analogue Complex',
                        x_label=X_AXIS_LABEL, y_label=Y_AXIS_LABEL,
                        plot_color='#15803d',  # Dark Green
                        legend_label=LEGEND_LABEL)

    # --- Plot 3 (Bottom-Left) ---
    plot_analysis_on_ax(axes[1, 0], 
                        data_file='lupeol_rmsf_per_residue.xvg', 
                        title='C) Lupeol Analogue Complex',
                        x_label=X_AXIS_LABEL, y_label=Y_AXIS_LABEL,
                        plot_color='#7c3aed',  # Bright Purple
                        legend_label=LEGEND_LABEL)

    # --- Plot 4 (Bottom-Right) ---
    plot_analysis_on_ax(axes[1, 1], 
                        data_file='maslinic_acid_rmsf_per_residue.xvg', 
                        title='D) Maslinic Acid Analogue Complex',
                        x_label=X_AXIS_LABEL, y_label=Y_AXIS_LABEL,
                        plot_color='#92400e',  # Dark Brown
                        legend_label=LEGEND_LABEL)

    # --- 3. SAVE THE FIGURE ---
    fig.suptitle(MAIN_TITLE, fontsize=18, fontweight='bold')
    fig.tight_layout(rect=[0, 0.03, 1, 0.96])
    
    # Set white background for the entire figure
    fig.patch.set_facecolor('white')
    
    # Save in multiple formats with white background
    plt.savefig(f'{OUTPUT_FILENAME}.png', dpi=900, facecolor='white', bbox_inches='tight')
    plt.savefig(f'{OUTPUT_FILENAME}.tiff', dpi=900, facecolor='white', bbox_inches='tight')
    plt.savefig(f'{OUTPUT_FILENAME}.eps', format='eps', dpi=900, facecolor='white', bbox_inches='tight')
    plt.savefig(f'{OUTPUT_FILENAME}.pdf', format='pdf', bbox_inches='tight', facecolor='white')
    plt.savefig(f'{OUTPUT_FILENAME}.svg', format='svg', bbox_inches='tight', facecolor='white')
    
    # For EMF format
    try:
        import pyemf
        plt.savefig(f'{OUTPUT_FILENAME}.emf', format='emf', bbox_inches='tight', facecolor='white')
        print(f"Successfully generated: {OUTPUT_FILENAME}.png, .tiff, .eps, .pdf, .svg, .emf")
    except ImportError:
        print("pyemf not available, skipping EMF format")
        print(f"Successfully generated: {OUTPUT_FILENAME}.png, .tiff, .eps, .pdf, .svg")
