# OpenMFD Repository Cleanup Analysis

Generated: 2025-12-20

## Current State

The repository has accumulated various files and directories over development. This document analyzes what should be kept, moved, archived, or deleted.

---

## 📁 Root Directory Files - Recommendations

### ✅ KEEP (Core Documentation)
- `README.md` - Main project documentation
- `pyproject.toml` - Python package configuration
- `requirements.txt` - Dependencies
- `.gitignore` - Git configuration

### 📦 MOVE TO `archive/` or `docs/archive/`

**Development/Planning Documents:**
- `ALIGNMENT_MARKS_IMPLEMENTATION.md` - Implementation notes (completed feature)
- `ARCHITECTURAL_FIX_PLAN.md` - Architecture planning (completed)
- `CENTERING_BUG_ANALYSIS.md` - Bug analysis (resolved)
- `CHANGELOG_TYPE_DRIVEN_DEFAULTS.md` - Changelog (completed feature)
- `COMMIT_SUMMARY.md` - Commit summary (historical)
- `OPENMFD_IMPLEMENTATION_STATUS.md` - Implementation status (outdated?)
- `PRESET_SYSTEM_EXPLAINED.md` - System explanation (move to docs/)
- `REFACTORING_4X4_PRESET.md` - Refactoring notes (completed)
- `TEST_SETUP_SUMMARY.md` - Test setup (move to tests/docs/)
- `TEST_VERIFICATION.md` - Test verification (move to tests/docs/)

**Recommendation:** Create `docs/archive/development/` and move all these there.

### 📦 ARCHIVE (Obsolete/Temporary)

**Old Scripts (superseded by openmfd package) → `archive/scripts/`:**
- `make_device.py` - Old device generation script (superseded by openmfd CLI)
- `mf_device.py` - Old device script (superseded)
- `mf_device.ipynb` - Old Jupyter notebook (superseded)

**Test Files (should be in tests/):**
- `test_alignment_marks.py` - Move to `tests/`
- `test_full_marks.scad` - Move to `tests/fixtures/`
- `test_hollow_marks.scad` - Move to `tests/fixtures/`
- `verify_device_centering.py` - Move to `tests/`
- `verify_insert_holes.py` - Move to `tests/`
- `verify_preset_geometry.py` - Move to `tests/`

**Utility Scripts (move to scripts/ or tools/):**
- `chamfer_extrude.scad` - Utility script → `scripts/scad/`
- `gcode_offset.py` - Utility script → `scripts/`
- `scad_to_step.py` - Utility script → `scripts/`
- `su-8_calc.py` - Utility script → `scripts/`

**Temporary/Cache Files → Add to .gitignore:**
- `.coverage` - Coverage data (add to .gitignore, keep file locally)
- `cufile.log` - Log file (add to .gitignore, keep file locally)
- `convert_shape.mhtml` - Temporary file → `archive/temp/`
- `mfd.zip` - Archive → `archive/releases/` or delete locally
- `__pycache__/` - Python cache (add to .gitignore)
- `.ipynb_checkpoints/` - Jupyter cache (add to .gitignore)

**Order Forms/Quotes (move to orders/ or archive/):**
- `Fineline Imaging Mylar Mask Quote and Order Form - Nov 19 2018.pdf` → `orders/archive/`
- `orderform.pdf` → `orders/archive/`
- `order_form_tristan.pdf` → `orders/archive/`
- `glass_order.note` → `orders/archive/`
- `dimensions` - Unclear, check content

**Obsolete Files → `archive/scripts/`:**
- `plate_96_3d_print_polypropylene.py_` - Backup file with `_` suffix

---

## 📁 Directory Structure - Recommendations

### ✅ KEEP (Core Directories)
- `openmfd/` - Python package
- `examples/` - Example scripts
- `tests/` - Test suite
- `docs/` - Documentation
- `papers/` - Publications (just added)
- `.github/` - GitHub configuration

### 📦 EVALUATE

**`designs/`** - Generated design files
- **Question:** Should these be in the repo or generated on-demand?
- **Recommendation:** Keep examples, but consider adding to .gitignore for user-generated designs

**`plates/`** - Plate designs?
- **Question:** What's in here? Is it user data or examples?
- **Recommendation:** Check contents, possibly move to examples/ or archive/

**`orders/`** - Order history
- **Question:** Is this personal data or project-related?
- **Recommendation:** Keep if project-related, otherwise move to personal archive

**`plans/`** - Planning documents
- **Recommendation:** Keep active plans, archive completed ones

**`gcode/`** - G-code files
- **Question:** Are these examples or generated files?
- **Recommendation:** If examples, keep. If generated, add to .gitignore

**`$MYVIMDIR`** - Vim configuration
- **Recommendation:** Add to .gitignore (personal editor config)

**`openmfd.egg-info/`** - Python package metadata
- **Recommendation:** Add to .gitignore (auto-generated)

**`.venv/`** - Virtual environment
- **Recommendation:** Should already be in .gitignore

**`revisions/`** - Revision history (EMPTY)
- **Recommendation:** Delete empty directory (or keep, doesn't hurt)

---

## 🎯 Proposed New Structure

```
OpenMFD/
├── openmfd/              # Python package (keep)
├── examples/             # Example scripts (keep)
├── tests/                # Test suite (keep)
│   ├── fixtures/        # Test fixtures (add test .scad files here)
│   └── docs/            # Test documentation (add TEST_*.md here)
├── docs/                 # Documentation (keep)
│   ├── source/          # Sphinx docs (keep)
│   ├── archive/         # Archived development docs (NEW)
│   │   └── development/ # Planning/implementation notes
│   └── PRESET_SYSTEM_EXPLAINED.md (move here)
├── scripts/              # Utility scripts (NEW)
│   ├── scad/            # SCAD utilities
│   └── ...              # Other utilities
├── archive/              # Archived/obsolete files (NEW)
│   ├── scripts/         # Old scripts (superseded)
│   ├── temp/            # Temporary files
│   └── releases/        # Old release archives
├── papers/               # Publications (keep)
├── orders/               # Order history (keep)
│   └── archive/         # Old orders/quotes
├── plans/                # Active planning docs (keep)
│   └── archive/         # Completed plans
├── .github/              # GitHub config (keep)
├── README.md             # Main docs (keep)
├── pyproject.toml        # Package config (keep)
├── requirements.txt      # Dependencies (keep)
└── .gitignore            # Git config (update)
```

---

## 📋 Action Items

### Priority 1: Clean up root directory
1. Create `scripts/` directory
2. Create `docs/archive/development/` directory
3. Create `tests/fixtures/` directory
4. Create `tests/docs/` directory
5. Move files according to recommendations above

### Priority 2: Update .gitignore
Add:
- `.coverage`
- `*.log`
- `__pycache__/`
- `.ipynb_checkpoints/`
- `openmfd.egg-info/`
- `.venv/`
- `*.egg-info/`

### Priority 3: Archive completed work
- Move completed planning docs to archive
- Move old order forms to orders/archive/

### Priority 4: Archive obsolete files
- Move superseded scripts to archive/scripts/
- Move temporary files to archive/temp/
- Add personal config files to .gitignore

---

## ❓ Questions Answered

1. **designs/**: Generated design files - KEEP (examples of generated outputs)
2. **plates/**: 3D print plate designs (HIPS, PP, resin versions) - KEEP (active development)
3. **orders/**: CNC/fabrication orders with dates - KEEP (project history, useful reference)
4. **gcode/**: G-code for 3D printer - KEEP (printer-specific configs)
5. **revisions/**: EMPTY directory - DELETE
6. **dimensions**: Simple text file with wafer dimensions - MOVE to docs/ or delete

---

## 📊 Summary

**Total files to clean up:** ~30 files
**Directories to create:** 6 (scripts/, docs/archive/development/, tests/fixtures/, tests/docs/, archive/scripts/, archive/temp/)
**Directories to gitignore:** 2 ($MYVIMDIR, __pycache__, .ipynb_checkpoints/)
**Files to move:** ~25
**Files to archive (not delete):** ~10
**Files to gitignore:** ~5 (coverage, logs, caches)


