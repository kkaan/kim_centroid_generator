# Personal Progress Log - DICOM Centroid Calculator

## Working Directories

### Primary Development Directory
- `/mnt/c/Users/kankean.kandasamy/KIM_centroid_generator`
  - Main codebase and development environment
  - Contains source code, documentation, and build configurations

### Test Data Directory  
- `/mnt/p/04_Projects/07_KIM/Test set for Centroid Script/Spark Centre5 TP RS Centroids/`
  - Test DICOM files for validation and testing
  - Contains RTSTRUCT and RTPLAN sample files for development testing

## Current Session Progress
- [x] Set up virtual environment for PyInstaller
- [x] Identified PyInstaller permission error (WinError 5)
- [x] Set up git branch: allow-terminal-interactions
- [x] Interactive mode implementation for custom structure selection
- [x] Enhanced output using actual structure names from DICOM files
- [x] Improved PyInstaller executable build configuration
- [x] Comprehensive documentation in CLAUDE.md
- [x] Personal progress tracking system established
- [ ] Fix PyInstaller permission error and create Windows executable

## Next Priority: Validation Against Spark Test Set
- [ ] Validate application with Spark Centre test data
- [ ] Compare centroid calculations with Spark reference data
- [ ] **CRITICAL**: Investigate isocenter mismatches in test set
  - Identify which test cases have mismatched isocenters
  - Determine if issue is in our calculation or Spark reference
  - Check DICOM tag interpretation differences
  - Verify coordinate system transformations

## Technical Investigation Tasks
- [ ] Add detailed logging for isocenter extraction process
- [ ] Compare DICOM tag parsing between our code and Spark
- [ ] Check for coordinate system differences (LPS vs RAS)
- [ ] Validate against known ground truth data

## Medical Physics Safety Considerations
- [ ] Document validation methodology
- [ ] Establish acceptable tolerance levels for centroid/isocenter differences
- [ ] Create test report format for clinical validation

## Build & Deployment
- [ ] Complete Windows executable creation
- [ ] Complete terminal interactions feature
- [ ] Test executable on clean Windows machines
- [ ] Test executable with real-world DICOM files
- [ ] Performance testing with large DICOM files
- [ ] Performance optimization for large file sets

---
*Last updated: Sat Aug 16 18:58:32 AEST 2025*

