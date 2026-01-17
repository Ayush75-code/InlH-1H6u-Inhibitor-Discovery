#!/usr/bin/env python3
"""
Diagnostic script to find all molecular orbital and ESP files
"""

import os
import glob

print("=" * 70)
print("MOLECULAR VISUALIZATION FILE FINDER")
print("=" * 70)

# Find all ESP files
print("\n📊 ESP SURFACE FILES:")
esp_files = glob.glob("*ESP*.png")
if esp_files:
    for f in sorted(esp_files):
        size = os.path.getsize(f) / 1024
        print(f"  ✓ {f:50s} ({size:.1f} KB)")
else:
    print("  ✗ No ESP surface files found")

# Find all HOMO files
print("\n🔴 HOMO ORBITAL FILES:")
homo_files = glob.glob("*HOMO*.png")
if homo_files:
    for f in sorted(homo_files):
        size = os.path.getsize(f) / 1024
        print(f"  ✓ {f:50s} ({size:.1f} KB)")
else:
    print("  ✗ No HOMO orbital files found")

# Find all LUMO files
print("\n🔵 LUMO ORBITAL FILES:")
lumo_files = glob.glob("*LUMO*.png")
if lumo_files:
    for f in sorted(lumo_files):
        size = os.path.getsize(f) / 1024
        print(f"  ✓ {f:50s} ({size:.1f} KB)")
else:
    print("  ✗ No LUMO orbital files found")

# Check for each molecule
print("\n" + "=" * 70)
print("MOLECULE-BY-MOLECULE CHECK:")
print("=" * 70)

molecules = ['control', 'hedragenin', 'lupeol', 'maslinic_acid']
variations = {
    'hedragenin': ['hedragenin', 'hedrageinin', 'hedrageini', "'hedragenin HOMO_Orbital'"]
}

for mol in molecules:
    print(f"\n🧬 {mol.upper().replace('_', ' ')}:")
    
    # Check variations
    names_to_try = [mol]
    if mol in variations:
        names_to_try.extend(variations[mol])
    
    found_esp = False
    found_homo = False
    found_lumo = False
    
    for name in names_to_try:
        # ESP variations
        esp_patterns = [
            f"{name}_ESP_Surface.png",
            f"{name}ESP_Surface.png",
            f"{name} ESP_Surface.png"
        ]
        
        for pattern in esp_patterns:
            if os.path.exists(pattern):
                print(f"  ✓ ESP:  {pattern}")
                found_esp = True
                break
        
        # HOMO variations
        homo_patterns = [
            f"{name}_HOMO_Orbital.png",
            f"{name}HOMO_Orbital.png",
            f"{name} HOMO_Orbital.png"
        ]
        
        for pattern in homo_patterns:
            if os.path.exists(pattern):
                print(f"  ✓ HOMO: {pattern}")
                found_homo = True
                break
        
        # LUMO variations
        lumo_patterns = [
            f"{name}_LUMO_Orbital.png",
            f"{name}LUMO_Orbital.png",
            f"{name} LUMO_Orbital.png"
        ]
        
        for pattern in lumo_patterns:
            if os.path.exists(pattern):
                print(f"  ✓ LUMO: {pattern}")
                found_lumo = True
                break
        
        if found_esp and found_homo and found_lumo:
            break
    
    if not found_esp:
        print(f"  ✗ ESP:  Missing")
    if not found_homo:
        print(f"  ✗ HOMO: Missing")
    if not found_lumo:
        print(f"  ✗ LUMO: Missing")

print("\n" + "=" * 70)
print("RECOMMENDATIONS:")
print("=" * 70)

# Find what's actually there for hedragenin
hedra_files = [f for f in glob.glob("*") if 'hedra' in f.lower() and f.endswith('.png')]
if hedra_files:
    print("\n📁 Found these hedragenin-related files:")
    for f in hedra_files:
        print(f"  • {f}")
    print("\nTo fix, rename them to standard format:")
    for f in hedra_files:
        if 'esp' in f.lower():
            print(f"  mv '{f}' 'hedragenin_ESP_Surface.png'")
        elif 'homo' in f.lower():
            print(f"  mv '{f}' 'hedragenin_HOMO_Orbital.png'")
        elif 'lumo' in f.lower():
            print(f"  mv '{f}' 'hedragenin_LUMO_Orbital.png'")
else:
    print("\n⚠️  No hedragenin files found at all!")
    print("   Make sure you have generated the images for hedragenin.")

print("\n" + "=" * 70)
