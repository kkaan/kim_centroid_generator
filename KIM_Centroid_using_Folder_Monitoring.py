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

class DICOMHandler:
    """
    Handles the loading, processing, and analysis of DICOM RTSTRUCT and RTPLAN files.
    This includes extracting structure contour data, calculating centroids,
    and retrieving isocenter information.
    """
    def __init__(self, rtstruct_file, rtplan_file):
        """
        Initializes the DICOMHandler with paths to RTSTRUCT and RTPLAN files.

        :param rtstruct_file: Path to the RTSTRUCT DICOM file.
        :param rtplan_file: Path to the RTPLAN DICOM file.
        """
        self.rtstruct_file = rtstruct_file
        self.rtplan_file = rtplan_file
        self.rtstruct = None
        self.rtplan = None

    def load_files(self):
        """
        Loads the RTSTRUCT and RTPLAN DICOM files specified during initialization.

        Sets the `self.rtstruct` and `self.rtplan` attributes.

        :return: True if both files are loaded successfully, False otherwise.
        """
        try:
            self.rtstruct = pydicom.dcmread(self.rtstruct_file, force=True)
            print(f"Loaded RT Structure file: {self.rtstruct_file}")
        except Exception as e:
            print(f"Error reading RT Structure file {self.rtstruct_file}: {e}")
            return False
        
        try:
            self.rtplan = pydicom.dcmread(self.rtplan_file, force=True)
            print(f"Loaded RT Plan file: {self.rtplan_file}")
        except Exception as e:
            print(f"Error reading RT Plan file {self.rtplan_file}: {e}")
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
        target_name = structure_name.strip().lower()  # Convert to lowercase for case-insensitive matching
        
        for roi in dataset.StructureSetROISequence:
            roi_name = roi.ROIName.strip().lower()  # Compare with lowercase names
            if roi_name == target_name:
                roi_number = roi.ROINumber
                print(f"Found {structure_name} with ROINumber: {roi_number}")
                break
        else:
            print(f"{structure_name} not found in StructureSetROISequence.")
            return None

        for roi_contour in dataset.ROIContourSequence:
            if roi_contour.ReferencedROINumber == roi_number:
                contours = []
                for contour_item in roi_contour.ContourSequence:
                    contours.append(np.array(contour_item.ContourData).reshape((-1, 3)))
                if contours:
                    print(f"Found contours for {structure_name}")
                    return np.concatenate(contours, axis=0)
                else:
                    print(f"No contours found for {structure_name}")
                    return None
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
        for beam in dataset.BeamSequence:
            if hasattr(beam, 'ControlPointSequence'):
                for control_point in beam.ControlPointSequence:
                    if hasattr(control_point, 'IsocenterPosition'):
                        return np.array(control_point.IsocenterPosition)
        print("No isocenter data found in RT Plan.")
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

        print(f"Processing files for Patient ID: {patient_id_struct}")

        structure_names = self.list_structure_names()

        # Define possible structure names (case-insensitive)
        possible_structure_names = []
        for i in range(1, 4):
            possible_structure_names.append(f"seed{i}".lower())      # e.g., "seed1"
            possible_structure_names.append(f"seed {i}".lower())     # e.g., "seed 1"
            possible_structure_names.append(f"au{i}".lower())        # e.g., "au1"
            possible_structure_names.append(f"au {i}".lower())       # e.g., "au 1"

        centroids = []
        all_structures_found = False

        # Loop through all possible structure names (case-insensitive)
        for structure in possible_structure_names:
            if structure in structure_names:
                points = self.get_structure_contours(self.rtstruct, structure)
                if points is not None:
                    centroid = self.calculate_centroid(points)
                    centroids.append(centroid)
                    all_structures_found = True
                else:
                    print(f"No points found for {structure}.")
            else:
                print(f"{structure} is not available in StructureSetROISequence.")

        if not all_structures_found:
            print("No structures found or no contours found. Centroid file will not be generated.")
            return

        isocenter = self.get_isocenter_from_rtplan(self.rtplan)
        beam_ids = self.get_beam_ids(self.rtplan)

        # Construct the output folder name using patient ID and Beam IDs
        if len(beam_ids) >= 2:
            output_folder_name = f"{patient_id_struct}_BeamID_{beam_ids[0]}_{beam_ids[1]}"
        else:
            output_folder_name = patient_id_struct  # Fallback if fewer than 2 beams are found

        output_directory = os.path.join(r"C:\kim", output_folder_name)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Construct the output file name
        output_file = os.path.join(output_directory, f"Centroid_{patient_id_struct}_BeamID_{beam_ids[0]}_{beam_ids[1]}.txt")

        # Overwrite the output file if it exists
        if os.path.exists(output_file):
            os.remove(output_file)

        with open(output_file, "w") as f:
            f.write(f"{patient_id_struct}\n")
            f.write(f"{patient_name}\n")
            
            for i, centroid in enumerate(centroids):
                f.write(f"Seed {i + 1}, X= {self.convert_to_cm(centroid[0]):.2f}, Y= {self.convert_to_cm(centroid[1]):.2f}, Z= {self.convert_to_cm(centroid[2]):.2f}\n")
            
            if isocenter is not None:
                f.write(f"Isocenter (cm), X= {self.convert_to_cm(isocenter[0]):.2f}, Y= {self.convert_to_cm(isocenter[1]):.2f}, Z= {self.convert_to_cm(isocenter[2]):.2f}\n")
            else:
                f.write("No isocenter data found.\n")

        print(f"Output written to {output_file}")

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

class DICOMEventHandler(FileSystemEventHandler):
    """
    Handles file system events, specifically the creation of new files.
    It checks for DICOM RTSTRUCT and RTPLAN files and triggers processing
    when both are detected.
    """
    def __init__(self):
        """
        Initializes the DICOMEventHandler.

        Sets up an empty dictionary `self.files_detected` to keep track
        of detected RTSTRUCT and RTPLAN files.
        """
        self.files_detected = {}

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
        try:
            dicom_file = pydicom.dcmread(event.src_path, force=True)
        except Exception as e:
            print(f"Error reading DICOM file {event.src_path}: {e}")
            return

        modality = dicom_file.Modality
        
        if modality == "RTSTRUCT":
            self.files_detected["structure"] = event.src_path
        elif modality == "RTPLAN":
            self.files_detected["plan"] = event.src_path
        
        if "structure" in self.files_detected and "plan" in self.files_detected:
            print("Both files detected, processing...")
            rtstruct_file = self.files_detected["structure"]
            rtplan_file = self.files_detected["plan"]

            handler = DICOMHandler(rtstruct_file, rtplan_file)
            if handler.load_files():
                handler.process_dicom_files()

def start_monitoring(folder_to_watch):
    """
    Initializes and starts the file system observer to monitor the specified folder.

    The observer listens for new DICOM files and uses `DICOMEventHandler`
    to process them. This function runs indefinitely until interrupted
    (e.g., by KeyboardInterrupt).

    :param folder_to_watch: The path to the folder that should be monitored.
    :type folder_to_watch: str
    """
    monitoring_path = r"C:\kim"
    print(f"Monitoring folder: {monitoring_path}")
    event_handler = DICOMEventHandler()
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
    folder_to_watch = r"C:\kim"  # Folder to monitor
    start_monitoring(folder_to_watch)