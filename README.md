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

1.  **Choose the Monitored Folder:**
    -   Decide on the full path of the folder you want the script to monitor for DICOM files.
    -   The script will use this base path for creating output subdirectories (e.g., `PatientID_BeamID_...`) and a `backup` subdirectory. Ensure the script has write permissions for this location.

2.  **Run the Script:**
    -   Open a terminal or command prompt.
    -   Navigate to the directory where `KIM_Centroid_using_Folder_Monitoring.py` is located.
    -   Execute the script using the Python interpreter. You have two options:

    *   **Option A: Use the default folder path (`C:\kim`):**
        ```bash
        python KIM_Centroid_using_Folder_Monitoring.py
        ```
        If you run the script without any additional arguments, it will monitor the default folder `C:\kim`.

    *   **Option B: Specify a custom folder path:**
        Use the `--folder` (or `-f`) command-line argument to specify a different folder:
        ```bash
        python KIM_Centroid_using_Folder_Monitoring.py --folder "D:\DICOM_Files\Input"
        ```
        Replace `"D:\DICOM_Files\Input"` with the actual path to your desired folder. If the path contains spaces, enclose it in quotes.

3.  **Operation:**
    -   Once running, the script will print a message indicating which folder it is monitoring (e.g., "Monitoring folder: D:\DICOM_Files\Input").
    -   It will then wait for new files to be created in that folder.
    -   When an RTSTRUCT and an RTPLAN file appear, the script will attempt to process them.
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

## Creating an Executable (Optional)

For easier distribution and execution on computers that may not have Python or the necessary packages installed, you can create a standalone executable from the script. One common tool for this is PyInstaller.

This section provides basic instructions on how to use PyInstaller.

### 1. Install PyInstaller

If you don't have PyInstaller installed, you can install it using pip. Open your terminal or command prompt and run:

```bash
pip install pyinstaller
```

### 2. Build the Executable

Once PyInstaller is installed, you can use it to build the executable.

1.  Open your terminal or command prompt.
2.  Navigate to the directory where `KIM_Centroid_using_Folder_Monitoring.py` is located.
3.  Run the following command to create a single-file executable:

    ```bash
    pyinstaller --onefile KIM_Centroid_using_Folder_Monitoring.py
    ```
    -   The `--onefile` option bundles everything into a single executable file.
    -   You can also add `--name YourAppName` before `--onefile` to specify a name for your executable (e.g., `pyinstaller --name DICOMMonitor --onefile KIM_Centroid_using_Folder_Monitoring.py`).
    -   For a GUI-less console application like this script, you might also consider adding the `--noconsole` or `--windowed` option if you were creating a GUI app, but for this script, you want the console to see the logs. If you want to hide the console for a background process (though logs would be hidden), you could use `pyinstaller --onefile --windowed KIM_Centroid_using_Folder_Monitoring.py` or `pyinstaller --onefile --noconsole KIM_Centroid_using_Folder_Monitoring.py`. However, for this script, seeing the console output is important, so `--onefile` by itself is usually best.

4.  After PyInstaller finishes, you will find a `dist` subdirectory in your current directory. Inside `dist`, you'll find the executable file (e.g., `KIM_Centroid_using_Folder_Monitoring.exe` on Windows, or `KIM_Centroid_using_Folder_Monitoring` on macOS/Linux).

5.  This executable can then be copied to other machines and run without needing a Python installation or the specific packages.
```

### 3. Important Considerations

-   **Antivirus Software:** Executables created by PyInstaller, especially single-file executables, are sometimes flagged as suspicious by antivirus software. This is often a false positive due to the way PyInstaller bundles the application. If this happens, you may need to add an exception for the executable in your antivirus program.
-   **File Paths:** If your script relies on relative paths for external files (which this script doesn't heavily, beyond the output/backup folders derived from `folder_to_watch`), be aware that the executable's working directory might behave differently. For this script, since `folder_to_watch` is an absolute path, it should generally be fine.
-   **Testing:** Always test the generated executable on a clean machine (or a virtual machine) that mimics the target environment to ensure it works as expected.
-   **Executable Size:** Single-file executables can be relatively large because they bundle a Python interpreter and necessary libraries.
-   **Build Time:** The first time you build, PyInstaller might take some time as it analyzes dependencies. Subsequent builds can be faster.
```
