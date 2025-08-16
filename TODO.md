# Personal Progress Log - DICOM Centroid Calculator

## Current Session Progress
- [x] Set up virtual environment for PyInstaller
- [x] Identified PyInstaller permission error (WinError 5)
- [x] Set up git branch: allow-terminal-interactions
- [ ] Fix PyInstaller permission error and create Windows executable

## Next Priority: Validation Against Spark Test Set
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
- [ ] Test executable on clean Windows machines
- [ ] Performance testing with large DICOM files

---
*Last updated: Sat Aug 16 18:58:32 AEST 2025*

