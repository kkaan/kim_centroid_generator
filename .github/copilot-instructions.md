# GitHub Copilot Instructions

This file provides guidance to GitHub Copilot when working with code in this repository.

## Project Overview

This is a medical imaging application that monitors a folder for DICOM RTSTRUCT (Radiation Therapy Structure Set) and RTPLAN (Radiation Therapy Plan) files, automatically processes them to calculate centroids of specified structures (seeds, gold markers), and generates structured output files with patient-specific information.

**Tech Stack:** Python 3.11, pydicom, numpy, watchdog

## Key Architecture

### Core Components

- **`DICOMHandler`**: Main processing engine handling DICOM file loading, structure analysis, centroid calculation, and isocenter extraction
- **`DICOMEventHandler`**: File system event handler monitoring for new DICOM files and triggering processing when complete RTSTRUCT/RTPLAN pairs are detected

### Processing Workflow

1. Monitor folder for new DICOM files (RTSTRUCT and RTPLAN)
2. Validate and identify files by modality
3. When both files present for a patient:
   - Load and validate DICOM files
   - Search for predefined structures (seed1-3, au1-3)
   - Calculate geometric centroids
   - Extract isocenter from treatment plan
   - Generate patient-specific output folder and file
   - Move processed files to backup directory

### Data Organization

- **Input**: Monitored folder (default: `C:\kim`)
- **Output**: Patient-specific folders (`PatientID_BeamID_Beam1_Beam2/`) with centroid text files
- **Backup**: Processed files moved to `backup/` subdirectory

## Development Setup

### Install Dependencies
```bash
# Production dependencies
pip install -r requirements.txt

# Development/testing dependencies
pip install -r requirements-dev.txt
```

### Running the Application
```bash
# Default monitoring folder (C:\kim) - prompts for interactive mode
python KIM_Centroid_using_Folder_Monitoring.py

# Custom folder
python KIM_Centroid_using_Folder_Monitoring.py --folder "path/to/dicom/folder"

# Enable interactive mode (skip startup prompt)
python KIM_Centroid_using_Folder_Monitoring.py --interactive
```

### Testing
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Building Executable
```bash
# Using provided spec file
pyinstaller KIM_Centroid_using_Folder_Monitoring.spec

# Direct build
pyinstaller --onefile KIM_Centroid_using_Folder_Monitoring.py
```

## Code Guidelines

### Structure Naming Conventions
The application uses case-insensitive matching with flexible naming:
- Seeds: "seed1", "seed 1", "seed2", "seed 2", "seed3", "seed 3"
- Gold markers: "au1", "au 1", "au2", "au 2", "au3", "au 3"

### Interactive Mode
When enabled and default structures not found:
- Display all available structures from DICOM file
- Allow user selection by number (e.g., "1,3,5") or "all"
- Label selected structures as "Seed 1", "Seed 2", etc.

### DICOM Processing Best Practices
- Use `pydicom.dcmread()` with `force=True` for robust file reading
- Always validate Patient ID consistency between RTSTRUCT and RTPLAN
- Extract contour data from ROIContourSequence
- Convert coordinates from millimeters to centimeters for output
- Extract isocenter from BeamSequence control points

### Error Handling
- Implement comprehensive error handling at each processing stage
- Log detailed information to console for monitoring
- Handle graceful failures allowing continued monitoring
- Verify file readiness before processing (handle incomplete transfers)

### File Operations
- Create patient-specific folders automatically
- Overwrite existing output files when needed
- Use safe file moving with error handling for backups
- Check file readiness to handle network transfers

## Testing Approach

- Smoke tests verify basic functionality
- Test with actual DICOM test data when possible
- Mock file system events for unit testing
- Verify coordinate calculations and conversions

## Important Dependencies

- **numpy 2.2.6**: Numerical operations and centroid calculations
- **pydicom 3.0.1**: DICOM file parsing and manipulation
- **watchdog 6.0.0**: File system monitoring
- **pyinstaller >= 6**: Executable building

## Configuration Files

- **pyrightconfig.json**: Type checking with relaxed attribute access for DICOM structures
- **KIM_Centroid_using_Folder_Monitoring.spec**: PyInstaller spec with watchdog hidden imports
- **requirements.txt**: Pinned versions for medical application stability

## Code Style Preferences

When suggesting code:
- Follow existing code patterns and style
- Use descriptive variable names for medical/DICOM concepts
- Add comments for complex DICOM data structure navigation
- Preserve error handling patterns
- Maintain logging consistency with existing messages
- Keep coordinate conversion logic explicit and clear
