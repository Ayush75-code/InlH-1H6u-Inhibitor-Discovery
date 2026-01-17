#!/usr/bin/env python3
"""
Generate all comparative analysis plots with clean spacing
"""

import os
import subprocess

print("="*60)
print("GENERATING CLEAN COMPARATIVE ANALYSIS PLOTS")
print("="*60)

# Run all clean analysis scripts
scripts = [
    'comparative_pca_clean_titles.py',
    'comparative_fels_clean_titles.py', 
    'comparative_dccm_clean_titles.py'
]

for script in scripts:
    if os.path.exists(script):
        print(f"\n🎯 Running {script}...")
        try:
            result = subprocess.run(['python3', script], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {script} completed successfully")
                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        if line and not line.startswith('#'):
                            print(f"   📝 {line}")
            else:
                print(f"❌ Error running {script}")
                if result.stderr:
                    print(f"   💥 Error: {result.stderr}")
        except Exception as e:
            print(f"❌ Exception running {script}: {e}")
    else:
        print(f"❌ {script} not found")

print("\n" + "="*60)
print("CLEAN PLOTS GENERATION COMPLETE!")
print("="*60)

# List all generated files
output_files = [
    'comparative_pca_clean.eps',
    'comparative_fels_clean.eps', 
    'comparative_dccm_clean.eps',
    'comparative_pca_clean.png',
    'comparative_fels_clean.png',
    'comparative_dccm_clean.png'
]

print("\n📁 GENERATED CLEAN FILES:")
for file in output_files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} (not created)")

print("\n✨ Clean plot features:")
print("   • Better main title placement (y=0.95)")
print("   • Manual subplot positioning for consistent spacing")
print("   • Smaller font sizes for cleaner look")
print("   • More space between title and subplots")
