# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a medical imaging application that monitors a folder for DICOM RTSTRUCT (Radiation Therapy Structure Set) and RTPLAN (Radiation Therapy Plan) files, automatically processes them to calculate centroids of specified structures (seeds, gold markers), and generates structured output files with patient-specific information.

## Key Architecture Components

### Core Classes

- **`DICOMHandler`**: Main processing engine that handles DICOM file loading, structure analysis, centroid calculation, and isocenter extraction. Contains all the medical imaging logic and coordinates the entire processing workflow.

- **`DICOMEventHandler`**: File system event handler that monitors for new DICOM files, identifies RTSTRUCT/RTPLAN pairs, and triggers processing when complete pairs are detected.

### Processing Flow

1. File system monitoring detects new DICOM files
2. Files are validated and identified by modality (RTSTRUCT vs RTPLAN)  
3. When both files for a patient are present, `DICOMHandler` processes them:
   - Loads and validates DICOM files
   - Searches for predefined structures (seed1-3, au1-3 with flexible naming)
   - Calculates geometric centroids for found structures
   - Extracts isocenter position from treatment plan
   - Generates patient-specific output folder and centroid file
   - Moves processed files to backup directory

### Data Flow and File Organization

- **Input**: Monitored folder receives RTSTRUCT and RTPLAN DICOM files
- **Output**: Patient-specific folders (`PatientID_BeamID_Beam1_Beam2/`) containing centroid text files
- **Backup**: Processed DICOM files moved to `backup/` subdirectory
- **Default monitoring path**: `C:\kim` (configurable via `--folder` argument)

## Development Commands

### Environment Setup
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
# Use default folder (C:\kim) - will prompt for interactive mode at startup
python KIM_Centroid_using_Folder_Monitoring.py

# Monitor custom folder - will prompt for interactive mode at startup
python KIM_Centroid_using_Folder_Monitoring.py --folder "path/to/dicom/folder"

# Force enable interactive mode (skip startup prompt)
python KIM_Centroid_using_Folder_Monitoring.py --interactive

# Combine options
python KIM_Centroid_using_Folder_Monitoring.py --folder "path/to/dicom/folder" --interactive
```

**Startup Behavior**: If the `--interactive` flag is not used, the application will prompt the user at startup to choose whether to enable interactive mode for custom structure selection.

### Building Executable
```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Build single-file executable using provided spec file
pyinstaller KIM_Centroid_using_Folder_Monitoring.spec

# Alternative: Build directly (without spec customizations)
pyinstaller --onefile KIM_Centroid_using_Folder_Monitoring.py
```

### Type Checking
```bash
# Pyright configuration is in pyrightconfig.json
pyright KIM_Centroid_using_Folder_Monitoring.py
```

## Important Implementation Details

### Structure Naming Conventions
The application searches for structures using case-insensitive matching with flexible naming:
- Seeds: "seed1", "seed 1", "seed2", "seed 2", "seed3", "seed 3"
- Gold markers: "au1", "au 1", "au2", "au 2", "au3", "au 3"

### Interactive Mode for Custom Structures
**Startup Configuration**: Application prompts user at startup to enable/disable interactive mode unless `--interactive` flag is used.

When interactive mode is enabled and no default structures are found:
- Application displays all available structures from the DICOM file
- User can select specific structures by number (e.g., "1,3,5")
- User can select all structures with "all"
- User can skip processing with "skip"
- Selected structures are processed and labeled as "Seed 1", "Seed 2", etc. in output

**Executable Usage**: When running the built executable, users simply double-click it and will be prompted to configure interactive mode at startup - no command-line knowledge required.

### Error Handling Strategy
- Comprehensive error handling at each processing stage
- Detailed logging to console for monitoring and troubleshooting
- Graceful failure handling that allows continued monitoring after errors
- File readiness checking with timeout to handle incomplete file transfers

### DICOM Processing Specifics
- Uses `pydicom.dcmread()` with `force=True` for robust file reading
- Patient ID validation between RTSTRUCT and RTPLAN files
- Contour data extraction from ROIContourSequence
- Coordinate conversion from millimeters to centimeters for output
- Isocenter extraction from BeamSequence control points

### File Management
- Automatic patient-specific folder creation
- File overwriting for existing output files
- Safe file moving with error handling for backup operations
- File readiness verification before processing to handle network transfers

## Configuration Notes

- **pyrightconfig.json**: Basic type checking with relaxed attribute access checking suitable for DICOM data structures
- **PyInstaller spec file**: Includes watchdog hidden imports for proper executable building
- **Requirements**: Pinned versions for medical application stability (numpy 2.2.6, pydicom 3.0.1, watchdog 6.0.0)