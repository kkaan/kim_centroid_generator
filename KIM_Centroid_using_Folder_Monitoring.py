"""
Monitors a folder for DICOM RTSTRUCT and RTPLAN files, processes them to
calculate centroids of specified structures (e.g., seeds, gold markers),
and saves the results to a text file.

Author: KRM
Company: GenesisCare
"""
import os
import numpy as np
import pydicom
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import argparse

def wait_for_file_ready(path, timeout=30, interval=0.5, stable_checks=2):
    end = time.time() + timeout
    last_size = -1
    stable = 0
    while time.time() < end:
        try:
            size = os.path.getsize(path)
            with open(path, "rb"):
                pass  # open succeeded
            if size == last_size:
                stable += 1
                if stable >= stable_checks:
                    return True
            else:
                stable = 0
                last_size = size
        except (PermissionError, FileNotFoundError, OSError):
            pass
        time.sleep(interval)
    return False

class DICOMHandler:
    """
    Handles the loading, processing, and analysis of DICOM RTSTRUCT and RTPLAN files.
    This includes extracting structure contour data, calculating centroids,
    and retrieving isocenter information.
    """
    def __init__(self, rtstruct_file, rtplan_file, interactive_mode=False):
        """
        Initializes the DICOMHandler with paths to RTSTRUCT and RTPLAN files.

        :param rtstruct_file: Path to the RTSTRUCT DICOM file.
        :param rtplan_file: Path to the RTPLAN DICOM file.
        :param interactive_mode: Whether to enable interactive structure selection.
        """
        self.rtstruct_file = rtstruct_file
        self.rtplan_file = rtplan_file
        self.rtstruct = None
        self.rtplan = None
        self.interactive_mode = interactive_mode

    def load_files(self):
        """
        Loads the RTSTRUCT and RTPLAN DICOM files specified during initialization.

        Sets the `self.rtstruct` and `self.rtplan` attributes.

        :return: True if both files are loaded successfully, False otherwise.
        """
        # Load RTSTRUCT file
        print(f"Attempting to load RT Structure file: {self.rtstruct_file}")
        try:
            self.rtstruct = pydicom.dcmread(self.rtstruct_file, force=True)
            print(f"Successfully loaded RT Structure file: {self.rtstruct_file}")
        except FileNotFoundError:
            print(f"Error: RT Structure file not found at {self.rtstruct_file}")
            return False
        except pydicom.errors.InvalidDicomError:
            print(f"Error: RT Structure file {self.rtstruct_file} is not a valid DICOM file or is corrupted.")
            return False
        except Exception as e:
            print(f"Unexpected error reading RT Structure file {self.rtstruct_file}: {e}")
            return False
        
        # Load RTPLAN file
        print(f"Attempting to load RT Plan file: {self.rtplan_file}")
        try:
            self.rtplan = pydicom.dcmread(self.rtplan_file, force=True)
            print(f"Successfully loaded RT Plan file: {self.rtplan_file}")
        except FileNotFoundError:
            print(f"Error: RT Plan file not found at {self.rtplan_file}")
            return False
        except pydicom.errors.InvalidDicomError:
            print(f"Error: RT Plan file {self.rtplan_file} is not a valid DICOM file or is corrupted.")
            return False
        except Exception as e:
            print(f"Unexpected error reading RT Plan file {self.rtplan_file}: {e}")
            return False
        
        return True

    def list_structure_names(self):
        """
        Lists all structure names found in the loaded RTSTRUCT file.

        Prints the available structure names and returns them as a list.
        Names are converted to lowercase for consistent matching.

        :return: A list of structure names (lowercase strings).
        """
        print("Available structures in RT Structure file:")
        structure_names = []
        for roi in self.rtstruct.StructureSetROISequence:
            structure_name = roi.ROIName.strip().lower()  # Convert to lowercase for case-insensitive matching
            print(f"Structure: {structure_name}")
            structure_names.append(structure_name)
        return structure_names

    def get_structure_contours(self, dataset, structure_name):
        """
        Retrieves the contour points for a specified structure from a DICOM dataset.

        :param dataset: The DICOM dataset (e.g., RTSTRUCT) to search within.
        :param structure_name: The name of the structure to find (case-insensitive).
        :return: A NumPy array of contour points (Nx3) if found, otherwise None.
        """
        print(f"Getting contours for: {structure_name}")
        target_name = structure_name.strip().lower()
        roi_number = -1  # Initialize roi_number to an invalid value

        try:
            # Find the ROI number for the given structure name
            found_roi = False
            if not hasattr(dataset, 'StructureSetROISequence'):
                print(f"Error: StructureSetROISequence not found in the dataset for {structure_name}.")
                return None
            for roi in dataset.StructureSetROISequence:
                if not hasattr(roi, 'ROIName') or not hasattr(roi, 'ROINumber'):
                    print(f"Warning: Skipping an ROI in StructureSetROISequence due to missing ROIName or ROINumber for {structure_name}.")
                    continue
                roi_name = roi.ROIName.strip().lower()
                if roi_name == target_name:
                    roi_number = roi.ROINumber
                    print(f"Found {structure_name} with ROINumber: {roi_number}")
                    found_roi = True
                    break
            if not found_roi:
                print(f"Structure '{structure_name}' not found in StructureSetROISequence.")
                return None
        except AttributeError as e:
            print(f"Error accessing StructureSetROISequence for {structure_name}: {e}. DICOM structure may be incomplete or malformed.")
            return None
        except Exception as e:
            print(f"Unexpected error while searching for {structure_name} in StructureSetROISequence: {e}")
            return None

        try:
            # Extract contour data using the found ROI number
            if not hasattr(dataset, 'ROIContourSequence'):
                print(f"Error: ROIContourSequence not found in the dataset for {structure_name} (ROINumber: {roi_number}).")
                return None
            for roi_contour in dataset.ROIContourSequence:
                if not hasattr(roi_contour, 'ReferencedROINumber') or not hasattr(roi_contour, 'ContourSequence'):
                    print(f"Warning: Skipping an ROI in ROIContourSequence due to missing ReferencedROINumber or ContourSequence for {structure_name} (ROINumber: {roi_number}).")
                    continue
                if roi_contour.ReferencedROINumber == roi_number:
                    contours = []
                    if not roi_contour.ContourSequence: # Check if ContourSequence is present and not empty
                        print(f"Structure '{structure_name}' (ROINumber: {roi_number}) found, but its ContourSequence is missing or empty.")
                        return None
                    for contour_item in roi_contour.ContourSequence:
                        if not hasattr(contour_item, 'ContourData') or not contour_item.ContourData:
                            print(f"Warning: Skipping a contour item for {structure_name} (ROINumber: {roi_number}) due to missing or empty ContourData.")
                            continue
                        try:
                            contour_points = np.array(contour_item.ContourData).reshape((-1, 3))
                            contours.append(contour_points)
                        except Exception as e_reshape: # More specific error for reshape
                            print(f"Error reshaping ContourData for {structure_name} (ROINumber: {roi_number}): {e_reshape}. Data might be malformed.")
                            # Decide if you want to skip this contour_item or return None for the whole structure
                            # For now, let's be strict and return None for the structure if any part is bad
                            return None 
                    if contours:
                        print(f"Successfully extracted contours for {structure_name} (ROINumber: {roi_number})")
                        return np.concatenate(contours, axis=0)
                    else:
                        print(f"Structure '{structure_name}' (ROINumber: {roi_number}) found, but no valid contour data could be extracted.")
                        return None
            
            print(f"Contour data for ROINumber {roi_number} (Structure: '{structure_name}') not found in ROIContourSequence.")
            return None
        except AttributeError as e:
            print(f"Error accessing ROIContourSequence or its elements for {structure_name} (ROINumber: {roi_number}): {e}. DICOM structure may be incomplete or malformed.")
            return None
        except Exception as e:
            print(f"Unexpected error while extracting contours for {structure_name} (ROINumber: {roi_number}): {e}")
            return None

    def calculate_centroid(self, points):
        """
        Calculates the centroid (geometric center) of a set of 3D points.

        :param points: A NumPy array of 3D points (Nx3).
        :return: A NumPy array representing the centroid (X, Y, Z).
        """
        return np.mean(points, axis=0)

    def convert_to_cm(self, value_in_mm):
        """
        Converts a value from millimeters to centimeters.

        :param value_in_mm: The value in millimeters.
        :return: The value converted to centimeters.
        """
        return value_in_mm / 10.0

    def get_isocenter_from_rtplan(self, dataset):
        """
        Retrieves the isocenter position from an RTPLAN DICOM dataset.

        It iterates through beams and control points to find the IsocenterPosition.

        :param dataset: The RTPLAN DICOM dataset.
        :return: A NumPy array of the isocenter position (X, Y, Z) if found, otherwise None.
        """
        print("Retrieving isocenter from RT Plan.")
        try:
            if not hasattr(dataset, 'BeamSequence') or not dataset.BeamSequence:
                print("Error: No BeamSequence found in RT Plan or BeamSequence is empty.")
                return None

            for i, beam in enumerate(dataset.BeamSequence):
                beam_identifier = beam.BeamName if hasattr(beam, 'BeamName') else f"Beam {i+1} (Number: {beam.BeamNumber})" if hasattr(beam, 'BeamNumber') else f"Beam at index {i}"
                
                if not hasattr(beam, 'ControlPointSequence') or not beam.ControlPointSequence:
                    print(f"Warning: ControlPointSequence missing or empty for {beam_identifier}.")
                    continue  # Try next beam

                for j, control_point in enumerate(beam.ControlPointSequence):
                    if not hasattr(control_point, 'IsocenterPosition'):
                        # This might be too verbose if many control points lack it, but for now, let's log it.
                        # Consider logging only once per beam if IsocenterPosition is consistently missing.
                        print(f"Warning: IsocenterPosition missing in a control point for {beam_identifier}, ControlPointIndex {j}.")
                        continue # Try next control point
                    
                    # IsocenterPosition found
                    try:
                        isocenter_position = np.array(control_point.IsocenterPosition)
                        print(f"Successfully retrieved IsocenterPosition from {beam_identifier}, ControlPointIndex {j}: {isocenter_position}")
                        return isocenter_position
                    except Exception as e_np: # Catch errors during np.array conversion
                        print(f"Error converting IsocenterPosition to NumPy array for {beam_identifier}, ControlPointIndex {j}: {e_np}. Data might be malformed.")
                        # Depending on policy, you might want to return None here or try other control points/beams.
                        # For now, if one is malformed, we'll assume it's critical for this beam.
                        continue # Or return None if one bad apple spoils the bunch. For now, try next.

        except AttributeError as e:
            print(f"Error: A DICOM tag is missing or attribute name is incorrect while accessing RT Plan data: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error while retrieving isocenter from RT Plan: {e}")
            return None
        
        # If loop completes without returning, no isocenter was found
        print("No isocenter data found in RT Plan after checking all beams and control points.")
        return None

    def get_beam_ids(self, dataset):
        """
        Retrieves a list of Beam IDs (BeamName) from an RTPLAN DICOM dataset.

        :param dataset: The RTPLAN DICOM dataset.
        :return: A list of BeamName strings.
        """
        beam_ids = []
        for beam in dataset.BeamSequence:
            beam_ids.append(beam.BeamName)
        return beam_ids

    def process_dicom_files(self):
        """
        Processes the loaded RTSTRUCT and RTPLAN files.

        This method orchestrates the extraction of structure centroids,
        isocenter information, and generates an output text file with these details.
        It also handles patient ID verification and file backup.
        """
        if self.rtstruct is None or self.rtplan is None:
            print("RT Structure or RT Plan not loaded properly.")
            return
        
        patient_id_struct = self.rtstruct.PatientID
        patient_id_plan = self.rtplan.PatientID
        patient_name = str(self.rtstruct.PatientName).replace("^", ",")

        if patient_id_struct != patient_id_plan:
            print(f"Patient IDs do not match. Structure Patient ID: {patient_id_struct}, Plan Patient ID: {patient_id_plan}")
            return

        print(f"Processing Patient ID: {patient_id_struct}, Patient Name: {patient_name}")

        structure_names = self.list_structure_names() # This method already prints available structures

        # Define possible structure names (case-insensitive)
        possible_structure_names = []
        for i in range(1, 4):
            possible_structure_names.append(f"seed{i}".lower())      # e.g., "seed1"
            possible_structure_names.append(f"seed {i}".lower())     # e.g., "seed 1"
            possible_structure_names.append(f"au{i}".lower())        # e.g., "au1"
            possible_structure_names.append(f"au {i}".lower())       # e.g., "au 1"

        structure_centroids = []  # List of tuples: (structure_name, centroid)
        all_structures_found = False

        print("\nStarting structure processing loop...")
        # Loop through all possible structure names (case-insensitive)
        for structure in possible_structure_names:
            print(f"Attempting to find structure: {structure}")
            if structure in structure_names:
                print(f"Structure '{structure}' found in DICOM list of ROIs. Attempting to retrieve contours.")
                points = self.get_structure_contours(self.rtstruct, structure)
                if points is not None:
                    print(f"Successfully retrieved contour points for {structure}. Calculating centroid.")
                    centroid = self.calculate_centroid(points)
                    print(f"Calculated centroid for {structure}: {centroid}")
                    structure_centroids.append((structure, centroid))
                    all_structures_found = True
                else:
                    # get_structure_contours already prints detailed messages if points are None
                    print(f"Could not retrieve contour points for {structure}. It will be skipped.")
            else:
                print(f"Structure '{structure}' is not listed in the available ROIs from StructureSetROISequence.")
        
        print("Finished structure processing loop.")

        # If no default structures found and interactive mode is enabled, prompt user
        if not all_structures_found and self.interactive_mode:
            print("No default structures found. Attempting interactive structure selection...")
            custom_structures = self.prompt_for_custom_structures(structure_names)
            
            if custom_structures is None:
                print("User chose to skip this file pair.")
                return
            
            print(f"Processing {len(custom_structures)} user-selected structures...")
            # Process custom selected structures
            for structure in custom_structures:
                print(f"Processing user-selected structure: {structure}")
                points = self.get_structure_contours(self.rtstruct, structure)
                if points is not None:
                    print(f"Successfully retrieved contour points for {structure}. Calculating centroid.")
                    centroid = self.calculate_centroid(points)
                    print(f"Calculated centroid for {structure}: {centroid}")
                    structure_centroids.append((structure, centroid))
                    all_structures_found = True
                else:
                    print(f"Could not retrieve contour points for {structure}. It will be skipped.")

        if not all_structures_found:
            print("No targetable structures with valid contours were found. Centroid file will not be generated.")
            return

        # Isocenter retrieval
        print("Attempting to retrieve isocenter.") # get_isocenter_from_rtplan also prints "Retrieving isocenter from RT Plan."
        isocenter = self.get_isocenter_from_rtplan(self.rtplan)
        if isocenter is not None:
            print(f"Isocenter retrieved: {isocenter}")
        else:
            print("Isocenter not found or could not be retrieved. It will not be included in the output.")

        beam_ids = self.get_beam_ids(self.rtplan) # Assuming get_beam_ids is robust or doesn't need extensive logging here

        # Construct the output folder name using patient ID and Beam IDs
        if len(beam_ids) >= 2:
            output_folder_name = f"{patient_id_struct}_BeamID_{beam_ids[0]}_{beam_ids[1]}"
        else:
            output_folder_name = patient_id_struct  # Fallback if fewer than 2 beams are found

        output_directory = os.path.join(r"C:\kim", output_folder_name)
        print(f"Constructing output folder: {output_folder_name}") # Log before makedirs
        if not os.path.exists(output_directory):
            try:
                os.makedirs(output_directory)
                print(f"Successfully created output directory: {output_directory}")
            except OSError as e:
                print(f"Error creating output directory {output_directory}: {e}. Cannot proceed with file writing.")
                return # Cannot write file if directory creation fails

        # Construct the output file name
        output_file_name_part = f"Centroid_{patient_id_struct}"
        if len(beam_ids) >= 2: # Ensure beam_ids were actually found and are sufficient
             output_file_name_part += f"_BeamID_{beam_ids[0]}_{beam_ids[1]}"
        else:
             print("Warning: Less than two Beam IDs found. Output filename will be simplified.")
        output_file_name_part += ".txt"
        output_file = os.path.join(output_directory, output_file_name_part)


        # Overwrite the output file if it exists
        if os.path.exists(output_file):
            print(f"Output file {output_file} already exists. It will be overwritten.")
            try:
                os.remove(output_file)
                print(f"Successfully removed existing file: {output_file}")
            except OSError as e:
                print(f"Error removing existing file {output_file}: {e}. Attempting to write anyway...")


        print(f"Saving output to file: {output_file}")
        try:
            with open(output_file, "w") as f:
                f.write(f"{patient_id_struct}\n")
                f.write(f"{patient_name}\n")
                
                for structure_name, centroid in structure_centroids:
                    # Capitalize the structure name for cleaner output
                    display_name = structure_name.title()
                    f.write(f"{display_name}, X= {self.convert_to_cm(centroid[0]):.2f}, Y= {self.convert_to_cm(centroid[1]):.2f}, Z= {self.convert_to_cm(centroid[2]):.2f}\n")
                
                if isocenter is not None:
                    f.write(f"Isocenter (cm), X= {self.convert_to_cm(isocenter[0]):.2f}, Y= {self.convert_to_cm(isocenter[1]):.2f}, Z= {self.convert_to_cm(isocenter[2]):.2f}\n")
                else:
                    f.write("No isocenter data found.\n") # Consistent with earlier logging
            print(f"Successfully wrote output file: {output_file}")
        except IOError as e:
            print(f"Error writing output file {output_file}: {e}. Please check permissions or disk space.")
            # Depending on desired behavior, could return here or allow backup to proceed
            # For now, allow backup to proceed as per original structure

        backup_directory = os.path.join(r"C:\kim", "backup")
        os.makedirs(backup_directory, exist_ok=True)

        self.move_and_overwrite(self.rtstruct_file, backup_directory)
        self.move_and_overwrite(self.rtplan_file, backup_directory)

        print(f"Moved DICOM files to {backup_directory}")

    def move_and_overwrite(self, source_file, destination_dir):
        """
        Moves a source file to a destination directory, overwriting if it exists.

        :param source_file: The path to the source file to be moved.
        :param destination_dir: The path to the destination directory.
        """
        destination_file = os.path.join(destination_dir, os.path.basename(source_file))

        if os.path.exists(destination_file):
            os.remove(destination_file)

        shutil.move(source_file, destination_dir)
        print(f"Moved {source_file} to {destination_file}")

    def prompt_for_custom_structures(self, available_structures):
        """
        Prompts the user to select custom structure names from available structures.
        
        :param available_structures: List of available structure names from DICOM file
        :return: List of selected structure names, or None if user cancels
        """
        print("\n" + "="*60)
        print("No default seed/marker structures found!")
        print("Available structures in this DICOM file:")
        print("="*60)
        
        for i, structure in enumerate(available_structures, 1):
            print(f"{i:2d}. {structure}")
        
        print("\nPlease select structures to process:")
        print("- Enter numbers separated by commas (e.g., 1,3,5)")
        print("- Enter 'all' to select all structures")
        print("- Enter 'skip' to skip this file pair")
        print("="*60)
        
        while True:
            try:
                user_input = input("Your selection: ").strip().lower()
                
                if user_input == 'skip':
                    print("Skipping this file pair...")
                    return None
                
                if user_input == 'all':
                    print(f"Selected all {len(available_structures)} structures")
                    return available_structures.copy()
                
                # Parse comma-separated numbers
                selected_indices = []
                for item in user_input.split(','):
                    idx = int(item.strip()) - 1  # Convert to 0-based index
                    if 0 <= idx < len(available_structures):
                        selected_indices.append(idx)
                    else:
                        print(f"Invalid selection: {item.strip()}. Please enter numbers between 1 and {len(available_structures)}")
                        raise ValueError("Invalid selection")
                
                if not selected_indices:
                    print("No valid structures selected. Please try again.")
                    continue
                
                selected_structures = [available_structures[i] for i in selected_indices]
                print(f"Selected structures: {', '.join(selected_structures)}")
                return selected_structures
                
            except (ValueError, IndexError):
                print("Invalid input. Please enter numbers separated by commas, 'all', or 'skip'")
                continue
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                return None

    def validate_structure_selection(self, user_input, available_structures):
        """
        Validates user structure selection input.
        
        :param user_input: User input string
        :param available_structures: List of available structure names
        :return: Tuple of (is_valid, selected_structures_or_error_msg)
        """
        user_input = user_input.strip().lower()
        
        if user_input == 'skip':
            return True, None
        
        if user_input == 'all':
            return True, available_structures.copy()
        
        try:
            selected_indices = []
            for item in user_input.split(','):
                idx = int(item.strip()) - 1
                if 0 <= idx < len(available_structures):
                    selected_indices.append(idx)
                else:
                    return False, f"Invalid selection: {item.strip()}. Must be between 1 and {len(available_structures)}"
            
            if not selected_indices:
                return False, "No valid structures selected"
            
            selected_structures = [available_structures[i] for i in selected_indices]
            return True, selected_structures
            
        except ValueError:
            return False, "Invalid input format. Use numbers separated by commas, 'all', or 'skip'"

def prompt_for_interactive_mode():
    """
    Prompts the user at startup to choose whether to enable interactive mode.
    
    :return: True if user wants interactive mode, False otherwise
    """
    print("\n" + "="*60)
    print("DICOM Centroid Calculator - Startup Configuration")
    print("="*60)
    print("This application monitors folders for DICOM files and calculates")
    print("centroids for seed/marker structures.")
    print()
    print("INTERACTIVE MODE OPTIONS:")
    print("- YES: If default seed names aren't found, you'll be prompted")
    print("       to select custom structures from available options")
    print("- NO:  Only process files with default seed naming conventions")
    print("       (seed1, seed 1, au1, au 1, etc.)")
    print("="*60)
    
    while True:
        try:
            response = input("Enable interactive mode for custom structure selection? (y/n): ").strip().lower()
            
            if response in ['y', 'yes', 'true', '1']:
                print("Interactive mode ENABLED - you'll be prompted for custom structures when needed.")
                return True
            elif response in ['n', 'no', 'false', '0']:
                print("Interactive mode DISABLED - only default seed names will be processed.")
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
                continue
                
        except KeyboardInterrupt:
            print("\nOperation cancelled. Defaulting to non-interactive mode.")
            return False
        except EOFError:
            print("\nInput ended. Defaulting to non-interactive mode.")
            return False

class DICOMEventHandler(FileSystemEventHandler):
    """
    Handles file system events, specifically the creation of new files.
    It checks for DICOM RTSTRUCT and RTPLAN files and triggers processing
    when both are detected.
    """
    def __init__(self, interactive_mode=False):
        """
        Initializes the DICOMEventHandler.

        Sets up an empty dictionary `self.files_detected` to keep track
        of detected RTSTRUCT and RTPLAN files.
        
        :param interactive_mode: Whether to enable interactive structure selection.
        """
        self.files_detected = {}
        self.interactive_mode = interactive_mode

    def on_created(self, event):
        """
        Called when a file or directory is created in the monitored folder.

        Filters for DICOM files (RTSTRUCT and RTPLAN). When both types
        for a patient are detected, it initiates their processing using
        `DICOMHandler`.

        :param event: The event object representing the file system event.
                      Expected to have an `is_directory` attribute and `src_path`.
        :type event: FileSystemEvent
        """
        if event.is_directory:
            return

        print(f"Detected file: {event.src_path}")

        if not wait_for_file_ready(event.src_path):
            print(f"File not ready within timeout, skipping: {event.src_path}")
            return

        print(f"Attempting to read DICOM metadata from: {event.src_path}")
        try:
            dicom_file = pydicom.dcmread(event.src_path, force=True)
        except FileNotFoundError:
            print(f"Error: File not found at {event.src_path} during metadata read attempt. It might have been moved or deleted.")
            return
        except pydicom.errors.InvalidDicomError as e_dicom:
            print(f"Error reading DICOM metadata from {event.src_path}: {e_dicom}. File may not be a valid DICOM file or is corrupted.")
            return
        except Exception as e:
            print(f"Unexpected error reading DICOM metadata from {event.src_path}: {e}")
            return

        try:
            modality = dicom_file.Modality
            if not modality: # Check if modality is None or empty string
                print(f"Warning: Modality tag is present but empty in {event.src_path}. Cannot determine file type. Skipping file.")
                return
        except AttributeError:
            print(f"Warning: Modality tag missing in {event.src_path}. Cannot determine if it's RTSTRUCT or RTPLAN. Skipping file.")
            return
        except Exception as e_modality: # Catch any other error during modality access
            print(f"Unexpected error accessing Modality for {event.src_path}: {e_modality}. Skipping file.")
            return

        print(f"File {event.src_path} identified with Modality: {modality}")
        
        if modality == "RTSTRUCT":
            self.files_detected["structure"] = event.src_path
            print(f"RTSTRUCT file detected and stored: {event.src_path}")
        elif modality == "RTPLAN":
            self.files_detected["plan"] = event.src_path
            print(f"RTPLAN file detected and stored: {event.src_path}")
        else:
            print(f"File {event.src_path} has Modality '{modality}', which is not RTSTRUCT or RTPLAN. Skipping.")
            return # Not a file type we are interested in pairing.
        
        # Check if both files are now detected
        if "structure" in self.files_detected and "plan" in self.files_detected:
            rtstruct_file = self.files_detected["structure"]
            rtplan_file = self.files_detected["plan"]
            print(f"Both RTSTRUCT ({rtstruct_file}) and RTPLAN ({rtplan_file}) files detected. Initiating processing.")

            try:
                handler = DICOMHandler(rtstruct_file, rtplan_file, self.interactive_mode)
                if handler.load_files(): # load_files() now has detailed internal logging
                    handler.process_dicom_files() # process_dicom_files() also has detailed internal logging
                    print(f"Finished processing pair: RTSTRUCT '{rtstruct_file}', RTPLAN '{rtplan_file}'.")
                else:
                    print(f"Failed to load DICOM files for processing (structure: {rtstruct_file}, plan: {rtplan_file}). See previous errors from DICOMHandler.load_files(). Waiting for new files.")
            except Exception as e_process:
                print(f"An unexpected error occurred during the setup or execution of DICOM processing for structure: {rtstruct_file}, plan: {rtplan_file}: {e_process}. Waiting for new files.")
            finally:
                # Always reset detected files for this pair attempt, regardless of success or failure,
                # to allow new attempts if, e.g., a corrected file is dropped or if one part was bad.
                print(f"Resetting detected files for pair: RTSTRUCT '{rtstruct_file}', RTPLAN '{rtplan_file}'. Ready for new detection cycle.")
                self.files_detected.pop("structure", None)
                self.files_detected.pop("plan", None)
        else:
            print("Waiting for the corresponding RTSTRUCT/RTPLAN file to complete the pair.")

    def on_modified(self, event):
        if event.is_directory:
            return
        # Same logic as on_created (wait_for_file_ready + dcmread + modality routing)
        if event.src_path in self.files_detected:
            print(f"Detected modified file: {event.src_path}")
            if not wait_for_file_ready(event.src_path):
                print(f"File not ready within timeout, skipping: {event.src_path}")
                return
            print(f"Attempting to read DICOM metadata from: {event.src_path}")
            try:
                dicom_file = pydicom.dcmread(event.src_path, force=True)
            except FileNotFoundError:
                print(f"Error: File not found at {event.src_path} during metadata read attempt. It might have been moved or deleted.")
                return
            except pydicom.errors.InvalidDicomError as e_dicom:
                print(f"Error reading DICOM metadata from {event.src_path}: {e_dicom}. File may not be a valid DICOM file or is corrupted.")
                return
            except Exception as e:
                print(f"Unexpected error reading DICOM metadata from {event.src_path}: {e}")
                return

            try:
                modality = dicom_file.Modality
                if not modality: # Check if modality is None or empty string
                    print(f"Warning: Modality tag is present but empty in {event.src_path}. Cannot determine file type. Skipping file.")
                    return
            except AttributeError:
                print(f"Warning: Modality tag missing in {event.src_path}. Cannot determine if it's RTSTRUCT or RTPLAN. Skipping file.")
                return
            except Exception as e_modality: # Catch any other error during modality access
                print(f"Unexpected error accessing Modality for {event.src_path}: {e_modality}. Skipping file.")
                return

            print(f"File {event.src_path} identified with Modality: {modality}")
            
            if modality == "RTSTRUCT":
                self.files_detected["structure"] = event.src_path
                print(f"RTSTRUCT file detected and stored: {event.src_path}")
            elif modality == "RTPLAN":
                self.files_detected["plan"] = event.src_path
                print(f"RTPLAN file detected and stored: {event.src_path}")
            else:
                print(f"File {event.src_path} has Modality '{modality}', which is not RTSTRUCT or RTPLAN. Skipping.")
                return # Not a file type we are interested in pairing.
            
            # Check if both files are now detected
            if "structure" in self.files_detected and "plan" in self.files_detected:
                rtstruct_file = self.files_detected["structure"]
                rtplan_file = self.files_detected["plan"]
                print(f"Both RTSTRUCT ({rtstruct_file}) and RTPLAN ({rtplan_file}) files detected. Initiating processing.")

                try:
                    handler = DICOMHandler(rtstruct_file, rtplan_file, self.interactive_mode)
                    if handler.load_files(): # load_files() now has detailed internal logging
                        handler.process_dicom_files() # process_dicom_files() also has detailed internal logging
                        print(f"Finished processing pair: RTSTRUCT '{rtstruct_file}', RTPLAN '{rtplan_file}'.")
                    else:
                        print(f"Failed to load DICOM files for processing (structure: {rtstruct_file}, plan: {rtplan_file}). See previous errors from DICOMHandler.load_files(). Waiting for new files.")
                except Exception as e_process:
                    print(f"An unexpected error occurred during the setup or execution of DICOM processing for structure: {rtstruct_file}, plan: {rtplan_file}: {e_process}. Waiting for new files.")
                finally:
                    # Always reset detected files for this pair attempt, regardless of success or failure,
                    # to allow new attempts if, e.g., a corrected file is dropped or if one part was bad.
                    print(f"Resetting detected files for pair: RTSTRUCT '{rtstruct_file}', RTPLAN '{rtplan_file}'. Ready for new detection cycle.")
                    self.files_detected.pop("structure", None)
                    self.files_detected.pop("plan", None)
            else:
                print("Waiting for the corresponding RTSTRUCT/RTPLAN file to complete the pair.")


def start_monitoring(folder_to_watch, interactive_mode=False):
    """
    Initializes and starts the file system observer to monitor the specified folder.

    The observer listens for new DICOM files and uses `DICOMEventHandler`
    to process them. This function runs indefinitely until interrupted
    (e.g., by KeyboardInterrupt).

    :param folder_to_watch: The path to the folder that should be monitored.
    :type folder_to_watch: str
    :param interactive_mode: Whether to enable interactive structure selection.
    :type interactive_mode: bool
    """
    # Use the folder_to_watch argument passed to the function
    print(f"Monitoring folder: {folder_to_watch}") 
    if interactive_mode:
        print("Interactive mode enabled - will prompt for custom structure names when defaults not found")
    event_handler = DICOMEventHandler(interactive_mode)
    observer = Observer()
    observer.schedule(event_handler, folder_to_watch, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitors a folder for DICOM RTSTRUCT and RTPLAN files and calculates centroids.")
    parser.add_argument(
        "-f", 
        "--folder", 
        type=str, 
        default=r"C:\kim",
        help="Path to the folder to monitor for DICOM files. Default: C:\\kim"
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Enable interactive mode to input custom structure names when defaults are not found"
    )
    args = parser.parse_args()
    folder_to_watch = args.folder
    interactive_mode = args.interactive

    print(f"Initializing DICOM monitoring script for folder: {folder_to_watch}")
    
    # If interactive mode wasn't specified via command line, prompt user at startup
    if not interactive_mode:
        interactive_mode = prompt_for_interactive_mode()
    else:
        print("Interactive mode ENABLED via command line argument.")
    
    try:
        # Note: The start_monitoring function also prints "Monitoring folder: {monitoring_path}"
        # where monitoring_path is currently hardcoded to C:\kim inside it.
        # This will be addressed in the next step if required.
        start_monitoring(folder_to_watch, interactive_mode)
    except Exception as e:
        # This is a last resort catch for unexpected errors in start_monitoring
        # or its setup that weren't KeyboardInterrupt.
        exception_type = type(e).__name__
        print(f"\n---------------------------------------------------------------------")
        print(f"CRITICAL ERROR: A critical unexpected error occurred in the monitoring script.")
        print(f"Error Type: {exception_type}")
        print(f"Error Message: {e}")
        print(f"The monitoring script will now terminate.")
        print(f"---------------------------------------------------------------------")
        # Depending on the deployment, you might want to log this to a file as well.
        # For now, printing to console is the requirement.