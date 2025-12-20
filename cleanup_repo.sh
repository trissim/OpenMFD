#!/bin/bash
# OpenMFD Repository Cleanup Script
# This script reorganizes the repository structure
# Run with: bash cleanup_repo.sh

set -e  # Exit on error

echo "🧹 OpenMFD Repository Cleanup"
echo "=============================="
echo ""

# Create new directory structure
echo "📁 Creating new directories..."
mkdir -p scripts/scad
mkdir -p docs/archive/development
mkdir -p tests/fixtures
mkdir -p tests/docs
mkdir -p archive/scripts
mkdir -p archive/temp
mkdir -p archive/releases
mkdir -p orders/archive

echo "✅ Directories created"
echo ""

# Move development documentation
echo "📦 Moving development documentation to docs/archive/development/..."
mv ALIGNMENT_MARKS_IMPLEMENTATION.md docs/archive/development/
mv ARCHITECTURAL_FIX_PLAN.md docs/archive/development/
mv CENTERING_BUG_ANALYSIS.md docs/archive/development/
mv CHANGELOG_TYPE_DRIVEN_DEFAULTS.md docs/archive/development/
mv COMMIT_SUMMARY.md docs/archive/development/
mv OPENMFD_IMPLEMENTATION_STATUS.md docs/archive/development/
mv REFACTORING_4X4_PRESET.md docs/archive/development/

echo "✅ Development docs moved"
echo ""

# Move PRESET_SYSTEM_EXPLAINED to docs/
echo "📦 Moving PRESET_SYSTEM_EXPLAINED.md to docs/..."
mv PRESET_SYSTEM_EXPLAINED.md docs/

echo "✅ Preset docs moved"
echo ""

# Move test files
echo "🧪 Moving test files to tests/..."
mv test_alignment_marks.py tests/
mv verify_device_centering.py tests/
mv verify_insert_holes.py tests/
mv verify_preset_geometry.py tests/

echo "🧪 Moving test fixtures to tests/fixtures/..."
mv test_full_marks.scad tests/fixtures/
mv test_hollow_marks.scad tests/fixtures/

echo "🧪 Moving test documentation to tests/docs/..."
mv TEST_SETUP_SUMMARY.md tests/docs/
mv TEST_VERIFICATION.md tests/docs/

echo "✅ Test files moved"
echo ""

# Move utility scripts
echo "🔧 Moving utility scripts to scripts/..."
mv gcode_offset.py scripts/
mv scad_to_step.py scripts/
mv su-8_calc.py scripts/

echo "🔧 Moving SCAD utilities to scripts/scad/..."
mv chamfer_extrude.scad scripts/scad/

echo "✅ Utility scripts moved"
echo ""

# Archive obsolete scripts
echo "📦 Archiving obsolete scripts to archive/scripts/..."
mv make_device.py archive/scripts/
mv mf_device.py archive/scripts/
mv mf_device.ipynb archive/scripts/
mv plate_96_3d_print_polypropylene.py_ archive/scripts/

echo "✅ Obsolete scripts archived"
echo ""

# Archive temporary files
echo "📦 Archiving temporary files to archive/temp/..."
mv convert_shape.mhtml archive/temp/ 2>/dev/null || echo "  (convert_shape.mhtml not found, skipping)"

echo "📦 Archiving old releases to archive/releases/..."
mv mfd.zip archive/releases/ 2>/dev/null || echo "  (mfd.zip not found, skipping)"

echo "✅ Temporary files archived"
echo ""

# Move old order forms
echo "📦 Moving old order forms to orders/archive/..."
mv "Fineline Imaging Mylar Mask Quote and Order Form - Nov 19 2018.pdf" orders/archive/
mv orderform.pdf orders/archive/
mv order_form_tristan.pdf orders/archive/
mv glass_order.note orders/archive/
mv dimensions orders/archive/ 2>/dev/null || echo "  (dimensions not found, skipping)"

echo "✅ Order forms moved"
echo ""

# Update .gitignore
echo "📝 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Coverage and test artifacts
.coverage
*.coverage
htmlcov/

# Logs
*.log

# Python cache
__pycache__/
*.pyc
*.pyo

# Jupyter
.ipynb_checkpoints/

# Package metadata
*.egg-info/
openmfd.egg-info/

# Virtual environments
.venv/
venv/
ENV/

# Personal editor configs
$MYVIMDIR/

# OS files
.DS_Store
Thumbs.db
EOF

echo "✅ .gitignore updated"
echo ""

echo "🎉 Cleanup complete!"
echo ""
echo "Next steps:"
echo "1. Review the changes: git status"
echo "2. Test that everything still works"
echo "3. Commit the reorganization: git add -A && git commit -m 'Reorganize repository structure'"
echo "4. Push to GitHub: git push origin master"
