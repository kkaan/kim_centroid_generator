# TODO - DICOM Centroid Calculator

## Working Directories


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
- [x] Fix PyInstaller permission error and create Windows executable

## Testing & Validation Results
- [x] Compared original baseline branch output with interactive mode branch output
  - Tested against verified centroid files
  - **Result**: Identical centroid calculations - interactive mode additions have not affected core functionality
- [x] KIM reads centroid files outputted from new code without any errors
  - Output format validated and compatible with KIM system
- [x] Manually edit structuresets in mim and check is centroid locations match the shifts.
- [ ] We need to check against spark (see below).

## Next Priority: Validation Against Spark Test Set
- [ ] Validate application with Spark Centre test data
- [ ] Compare centroid calculations with Spark reference data

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
- [x] Complete Windows executable creation
- [x] Complete terminal interactions feature
- [x] Auto build workflow setup in github
- [ ] Auto test workflow setup in github


---
*Last updated: Sat Dec 10 14:58:32 AEST 2025*

