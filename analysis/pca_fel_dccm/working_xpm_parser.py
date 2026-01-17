#!/usr/bin/env python3
"""
Working XPM parser for your GROMACS format
"""
import numpy as np
import re

def parse_xpm_gromacs(xpm_file):
    """
    Parse GROMACS XPM files with format:
    "A  c #0000FF " /* "-0.0143" */,
    """
    try:
        with open(xpm_file, 'r') as f:
            lines = f.readlines()
        
        # Find matrix dimensions
        width, height, ncolors = None, None, None
        for line in lines[:30]:
            match = re.search(r'"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"', line)
            if match:
                width = int(match.group(1))
                height = int(match.group(2))
                ncolors = int(match.group(3))
                print(f"Dimensions: {width}x{height}, {ncolors} colors")
                break
        
        if not width:
            print(f"ERROR: No dimensions found")
            return None
        
        # Parse color map with the correct format
        color_dict = {}
        
        for line in lines:
            # Match: "A  c #0000FF " /* "-0.0143" */,
            # The key part is there's a SPACE before /*
            match = re.match(r'"(.)\s+c\s+\S+\s+"\s*/\*\s*"([^"]*)"', line)
            if match:
                char = match.group(1)
                value_str = match.group(2).strip()
                try:
                    value = float(value_str)
                    color_dict[char] = value
                except ValueError:
                    pass
        
        print(f"Parsed {len(color_dict)} colors")
        
        if len(color_dict) == 0:
            print("ERROR: No colors parsed")
            # Show a sample line for debugging
            for line in lines[10:20]:
                if ' c ' in line and '/*' in line:
                    print(f"Sample line: {line.strip()}")
                    break
            return None
        
        # Parse data matrix
        matrix_data = []
        reading_data = False
        
        for line in lines:
            # Data rows start after color definitions
            # They look like: "FFFFFFGGGHHHIII...",
            if line.strip().startswith('"') and ' c ' not in line and '/*' not in line:
                reading_data = True
                
            if reading_data and line.strip().startswith('"'):
                # Extract characters between quotes
                match = re.search(r'"([^"]+)"', line)
                if match:
                    row_chars = match.group(1)
                    row_values = [color_dict.get(c, 0.0) for c in row_chars]
                    
                    if len(row_values) == width:
                        matrix_data.append(row_values)
                    
                    if len(matrix_data) >= height:
                        break
        
        if len(matrix_data) == 0:
            print("ERROR: No data rows found")
            return None
        
        matrix = np.array(matrix_data)
        print(f"✅ Matrix: {matrix.shape}, range [{matrix.min():.4f}, {matrix.max():.4f}]")
        return matrix
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


# Test on your files
if __name__ == "__main__":
    print("="*60)
    print("TESTING WORKING XPM PARSER")
    print("="*60)
    
    test_files = [
        'control_covar.xpm',
        'control_prob.xpm',
        'hedragenin_covar.xpm',
        'lupeol_covar.xpm'
    ]
    
    for filename in test_files:
        print(f"\n{filename}:")
        print("-"*60)
        result = parse_xpm_gromacs(filename)
        print()
