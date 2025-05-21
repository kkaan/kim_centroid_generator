# DICOM RTSTRUCT/RTPLAN Centroid Calculator

This script monitors a specified folder for pairs of DICOM RTSTRUCT (Radiation Therapy Structure Set) and RTPLAN (Radiation Therapy Plan) files. When a pair is detected, it processes them to:
- Identify predefined structures of interest (e.g., seeds, gold markers).
- Calculate the geometric centroid for each identified structure.
- Retrieve the isocenter position from the RTPLAN.
- Save these details into a text file in a patient-specific folder.
- Backup the processed DICOM files.

## Features

-   **Automated DICOM Monitoring:** Continuously watches a specified folder for new DICOM RTSTRUCT and RTPLAN file pairs.
-   **Structure Identification:** Identifies predefined structures of interest (e.g., "seed1", "seed 2", "au1", "au 2") from the RTSTRUCT file, accommodating various naming conventions (case-insensitive, with or without spaces).
-   **Centroid Calculation:** Calculates the geometric centroid for each successfully identified structure.
-   **Isocenter Retrieval:** Extracts the isocenter position from the RTPLAN file.
-   **Organized Output:** Saves the patient ID, patient name, structure names, their calculated centroids (in cm), and the isocenter coordinates (in cm) into a structured text file.
-   **Patient-Specific Folders:** Creates a unique output folder for each patient/beam combination (e.g., `PatientID_BeamID_Beam1_Beam2`) to store the centroid file.
-   **Data Backup:** Moves the processed RTSTRUCT and RTPLAN files to a central `backup` folder.
-   **Robust Error Handling:** Implements comprehensive error handling to manage issues like missing files, invalid DICOM formats, missing DICOM tags, and file operation failures.
-   **Detailed Logging:** Provides real-time status updates and error messages to the terminal, facilitating monitoring and troubleshooting.
-   **Cross-Platform:** Developed in Python, making it usable across different operating systems with Python installed.

## Prerequisites

-   **Python 3.x:** The script is written for Python 3. Ensure you have a Python 3 interpreter installed.
-   **Required Python Packages:**
    -   `pydicom`: For reading and parsing DICOM files.
    -   `numpy`: For numerical operations, particularly for array manipulations and centroid calculation.
    -   `watchdog`: For monitoring file system events.

    You can install these packages using pip:
    ```bash
    pip install pydicom numpy watchdog
    ```

## Setup and Usage

1.  **Configure the Monitored Folder:**
    -   Open the `KIM_Centroid_using_Folder_Monitoring.py` script in a text editor.
    -   Locate the following line near the end of the script:
        ```python
        folder_to_watch = r"C:\kim"  # Folder to monitor
        ```
    -   Change the path `r"C:\kim"` to the full path of the folder you want the script to monitor for DICOM files.
    -   **Note:** The script also uses this base path for creating output (`PatientID_BeamID_...`) and `backup` subdirectories. Ensure the script has write permissions for this location.

2.  **Run the Script:**
    -   Open a terminal or command prompt.
    -   Navigate to the directory where you saved the `KIM_Centroid_using_Folder_Monitoring.py` script.
    -   Execute the script using the Python interpreter:
        ```bash
        python KIM_Centroid_using_Folder_Monitoring.py
        ```

3.  **Operation:**
    -   Once running, the script will print a message indicating which folder it is monitoring (e.g., "Monitoring folder: C:\kim").
    -   It will then wait for new files to be created in that folder.
    -   When an RTSTRUCT (`.dcm` typically containing structure set) and an RTPLAN (`.dcm` typically containing plan details) file appear in the monitored folder, the script will attempt to process them.
    -   Status messages, including detected files, processing steps, and any errors, will be printed to the terminal.

4.  **Stopping the Script:**
    -   To stop the script, press `Ctrl+C` in the terminal where it is running.
```

## Output

1.  **Centroid Text File:**
    -   For each processed pair of RTSTRUCT and RTPLAN files, a text file is generated.
    -   **Location:** `[Monitored_Folder]\[PatientID]_BeamID_[BeamID1]_[BeamID2]\Centroid_[PatientID]_BeamID_[BeamID1]_[BeamID2].txt`
        -   `[Monitored_Folder]` is the folder configured in the script (e.g., `C:\kim`).
        -   `[PatientID]`, `[BeamID1]`, and `[BeamID2]` are extracted from the DICOM files. If fewer than two beam IDs are found, the folder/file name might be simpler (e.g., just `PatientID`).
    -   **Content Format:**
        ```text
        PatientID
        PatientName (Last,First)
        Seed 1, X= XX.XX, Y= YY.YY, Z= ZZ.ZZ
        Seed 2, X= XX.XX, Y= YY.YY, Z= ZZ.ZZ
        ...
        Isocenter (cm), X= XX.XX, Y= YY.YY, Z= ZZ.ZZ
        ```
        -   Coordinates are in centimeters (cm), rounded to two decimal places.
        -   If an isocenter cannot be found, "No isocenter data found." will be written instead.
        -   If no targetable structures are found with valid contours, the centroid file will not be generated for that pair.

2.  **Backup Files:**
    -   After successful processing, the original RTSTRUCT and RTPLAN files are moved to a `backup` subdirectory within the monitored folder.
    -   **Location:** `[Monitored_Folder]\backup\`
    -   Files in the backup directory will overwrite existing files with the same name if any.
```

## Troubleshooting/Logging

-   **Terminal Output:** The script prints detailed status messages and error information directly to the terminal window where it is running. This is the primary source for monitoring its activity and diagnosing any issues.
-   **Common Issues:**
    -   **Incorrect Folder Path:** Double-check the `folder_to_watch` path in the script.
    -   **Permissions:** Ensure the script has read permissions for the monitored folder and write permissions for creating output subdirectories, centroid files, and the `backup` folder.
    -   **DICOM File Issues:** If files are not processed, check the terminal for errors related to DICOM parsing (e.g., "Invalid DICOM file," "Modality tag missing," "AttributeError"). The files might be corrupted, not valid DICOM, or missing essential tags.
    -   **Structure Naming:** Ensure the ROI names for your target structures in the RTSTRUCT file (e.g., "Seed 1", "AU1") match the patterns the script looks for (case-insensitive "seed" or "au" followed by a number, with or without a space).
```
