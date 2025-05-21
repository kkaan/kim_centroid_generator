import os
import numpy as np
import pydicom
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class DICOMHandler:
    def __init__(self, rtstruct_file, rtplan_file):
        self.rtstruct_file = rtstruct_file
        self.rtplan_file = rtplan_file
        self.rtstruct = None
        self.rtplan = None

    def load_files(self):
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
        print("Available structures in RT Structure file:")
        structure_names = []
        for roi in self.rtstruct.StructureSetROISequence:
            structure_name = roi.ROIName.strip().lower()  # Convert to lowercase for case-insensitive matching
            print(f"Structure: {structure_name}")
            structure_names.append(structure_name)
        return structure_names

    def get_structure_contours(self, dataset, structure_name):
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
        return np.mean(points, axis=0)

    def convert_to_cm(self, value_in_mm):
        return value_in_mm / 10.0

    def get_isocenter_from_rtplan(self, dataset):
        print("Retrieving isocenter from RT Plan.")
        for beam in dataset.BeamSequence:
            if hasattr(beam, 'ControlPointSequence'):
                for control_point in beam.ControlPointSequence:
                    if hasattr(control_point, 'IsocenterPosition'):
                        return np.array(control_point.IsocenterPosition)
        print("No isocenter data found in RT Plan.")
        return None

    def get_beam_ids(self, dataset):
        beam_ids = []
        for beam in dataset.BeamSequence:
            beam_ids.append(beam.BeamName)
        return beam_ids

    def process_dicom_files(self):
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
        destination_file = os.path.join(destination_dir, os.path.basename(source_file))

        if os.path.exists(destination_file):
            os.remove(destination_file)

        shutil.move(source_file, destination_dir)
        print(f"Moved {source_file} to {destination_file}")

class DICOMEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.files_detected = {}

    def on_created(self, event):
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