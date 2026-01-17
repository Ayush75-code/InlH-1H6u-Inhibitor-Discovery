#!/usr/bin/env python3
"""
Check if all required data files exist and are valid
"""
import os

print("="*60)
print("DATA FILE VERIFICATION")
print("="*60)

# Expected files for PCA
pca_files = {
    'Control': 'control_2d_projection.xvg',
    'Hedragenin': 'hedragenin_2d_projection.xvg',
    'Lupeol': 'lupeol_2d_projection.xvg',
    'Maslinic Acid': 'maslinic_acid_2d_projection.xvg'
}

# Expected files for FEL
fel_files = {
    'Control': 'control_prob.xpm',
    'Hedragenin': 'hedragenin_prob.xpm',
    'Lupeol': 'lupeol_prob.xpm',
    'Maslinic Acid': 'maslinic_acid_prob.xpm'
}

# Expected files for DCCM
dccm_files = {
    'Control': 'control_covar.xpm',
    'Hedragenin': 'hedragenin_covar.xpm',
    'Lupeol': 'lupeol_dccm.xpm',  # Note: different naming!
    'Maslinic Acid': 'maslinic_acid_covar.xpm'
}

def check_files(file_dict, analysis_type):
    print(f"\n📊 {analysis_type} Files:")
    all_exist = True
    for name, filename in file_dict.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            if size > 0:
                print(f"   ✅ {filename} ({size:,} bytes)")
            else:
                print(f"   ⚠️  {filename} (EMPTY FILE)")
                all_exist = False
        else:
            print(f"   ❌ {filename} (NOT FOUND)")
            all_exist = False
    return all_exist

# Check all file types
pca_ok = check_files(pca_files, "PCA")
fel_ok = check_files(fel_files, "FEL")
dccm_ok = check_files(dccm_files, "DCCM")

# Check for common naming issues
print("\n🔍 Checking for common issues:")

# Check if hedragenin is misspelled
if os.path.exists('hegragenin_prob.xpm'):
    print("   ⚠️  Found 'hegragenin_prob.xpm' (typo!)")
    print("      Run: mv hegragenin_prob.xpm hedragenin_prob.xpm")

# Check if lupeol uses covar instead of dccm
if not os.path.exists('lupeol_dccm.xpm') and os.path.exists('lupeol_covar.xpm'):
    print("   ⚠️  'lupeol_dccm.xpm' not found but 'lupeol_covar.xpm' exists")
    print("      Run: cp lupeol_covar.xpm lupeol_dccm.xpm")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"PCA Files:  {'✅ All present' if pca_ok else '❌ Issues found'}")
print(f"FEL Files:  {'✅ All present' if fel_ok else '❌ Issues found'}")
print(f"DCCM Files: {'✅ All present' if dccm_ok else '❌ Issues found'}")

if pca_ok and fel_ok and dccm_ok:
    print("\n✨ All files present! Run: python3 generate_clean_plots.py")
else:
    print("\n⚠️  Fix missing files before running plot generation")
