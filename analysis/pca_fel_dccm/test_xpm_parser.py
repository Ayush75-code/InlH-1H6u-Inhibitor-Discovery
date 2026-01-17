#!/usr/bin/env python3
"""
Fixed XPM parsers that handle multiple GROMACS formats
Replace the parse functions in your scripts with these
"""
import numpy as np
import re

def parse_xpm_robust(xpm_file):
    """
    Robust XPM parser for GROMACS covariance/correlation matrices
    Handles multiple XPM format variations
    """
    try:
        with open(xpm_file, 'r') as f:
            lines = f.readlines()
        
        # Find matrix dimensions
        width, height, ncolors = None, None, None
        for line in lines[:30]:
            # Format: "width height ncolors chars_per_pixel"
            match = re.search(r'"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"', line)
            if match:
                width = int(match.group(1))
                height = int(match.group(2))
                ncolors = int(match.group(3))
                print(f"Found dimensions: {width}x{height}, {ncolors} colors")
                break
        
        if not width:
            print(f"ERROR: Could not find dimensions in {xpm_file}")
            return None
        
        # Parse color map
        color_dict = {}
        in_colors = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Start reading colors after static section
            if '"' in line and ' c ' in line and 'static' not in line:
                in_colors = True
            
            # Parse color definitions
            # Format: "X c #hexcolor /* "value" */"
            if in_colors and '"' in line and ' c ' in line:
                # Try to extract character and value
                match = re.match(r'"(.)\s+c\s+\S+\s*/\*\s*"([^"]*)"', line_stripped)
                if match:
                    char = match.group(1)
                    value_str = match.group(2).strip()
                    try:
                        value = float(value_str)
                        color_dict[char] = value
                    except ValueError:
                        pass
                
                # Stop reading colors when we have enough
                if len(color_dict) >= ncolors:
                    break
        
        print(f"Parsed {len(color_dict)} colors from {xpm_file}")
        
        if len(color_dict) == 0:
            print(f"ERROR: No color map found in {xpm_file}")
            return None
        
        # Parse data rows
        matrix_data = []
        in_data = False
        
        for line in lines:
            # Data rows start after colors and comments
            if not in_data and len(color_dict) > 0 and line.strip().startswith('"'):
                # Check if this is a data row (not a color definition)
                if ' c ' not in line:
                    in_data = True
            
            # Read data rows
            if in_data and line.strip().startswith('"'):
                # Extract character sequence between quotes
                match = re.search(r'"([^"]+)"', line)
                if match:
                    row_chars = match.group(1)
                    # Convert characters to values
                    row_values = [color_dict.get(c, 0.0) for c in row_chars]
                    
                    if len(row_values) == width:
                        matrix_data.append(row_values)
                    
                    # Stop when we have all rows
                    if len(matrix_data) >= height:
                        break
        
        if len(matrix_data) == 0:
            print(f"ERROR: No matrix data found in {xpm_file}")
            return None
        
        matrix = np.array(matrix_data)
        print(f"Successfully parsed {xpm_file}: {matrix.shape}, range [{matrix.min():.3f}, {matrix.max():.3f}]")
        return matrix
        
    except Exception as e:
        print(f"ERROR parsing {xpm_file}: {e}")
        import traceback
        traceback.print_exc()
        return None


# Test the parser
if __name__ == "__main__":
    print("="*60)
    print("TESTING ROBUST XPM PARSER")
    print("="*60)
    
    test_files = [
        'control_covar.xpm',
        'hedragenin_covar.xpm',
        'control_prob.xpm',
        'hedragenin_prob.xpm'
    ]
    
    for filename in test_files:
        print(f"\nTesting {filename}...")
        print("-"*60)
        result = parse_xpm_robust(filename)
        if result is not None:
            print(f"✅ SUCCESS: {filename}")
        else:
            print(f"❌ FAILED: {filename}")
        print()
