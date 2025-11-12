#!/usr/bin/env python3
"""
Script to extract isocenter coordinates from RTPLAN DICOM files.
Extracts IsocenterPosition from BeamSequence -> ControlPointSequence[0] -> IsocenterPosition
and converts from mm to cm with 2 decimal places.
"""

import pydicom
import os
from pathlib import Path

def extract_isocenter_coordinates(rtplan_path):
    """
    Extract isocenter coordinates from RTPLAN DICOM file.
    
    Args:
        rtplan_path: Path to the RTPLAN DICOM file
        
    Returns:
        tuple: (patient_id, formatted_coordinates) or (None, error_message)
    """
    try:
        # Read DICOM file
        ds = pydicom.dcmread(rtplan_path, force=True)
        
        # Get Patient ID
        patient_id = getattr(ds, 'PatientID', 'Unknown')
        
        # Extract isocenter position from BeamSequence
        if not hasattr(ds, 'BeamSequence') or len(ds.BeamSequence) == 0:
            return None, f"No BeamSequence found in {rtplan_path}"
            
        beam = ds.BeamSequence[0]  # First beam
        
        if not hasattr(beam, 'ControlPointSequence') or len(beam.ControlPointSequence) == 0:
            return None, f"No ControlPointSequence found in first beam of {rtplan_path}"
            
        control_point = beam.ControlPointSequence[0]  # First control point
        
        if not hasattr(control_point, 'IsocenterPosition'):
            return None, f"No IsocenterPosition found in first control point of {rtplan_path}"
            
        # Get isocenter position (in mm)
        isocenter_mm = control_point.IsocenterPosition
        
        if len(isocenter_mm) != 3:
            return None, f"Invalid IsocenterPosition format in {rtplan_path}: {isocenter_mm}"
        
        # Convert from mm to cm and round to 2 decimal places
        x_cm = round(float(isocenter_mm[0]) / 10, 2)
        y_cm = round(float(isocenter_mm[1]) / 10, 2)
        z_cm = round(float(isocenter_mm[2]) / 10, 2)
        
        # Format coordinates
        formatted_coords = f"X={x_cm:.2f}, Y={y_cm:.2f}, Z={z_cm:.2f}"
        
        return patient_id, formatted_coords
        
    except Exception as e:
        return None, f"Error processing {rtplan_path}: {str(e)}"

def main():
    """Main function to process all RTPLAN files."""
    
    # Ask user for test set folder path
    print("Isocenter Extraction Tool")
    print("=" * 25)
    test_set_folder = input("Please enter the path to the test set folder: ").strip()
    
    # Remove quotes if user included them
    if test_set_folder.startswith('"') and test_set_folder.endswith('"'):
        test_set_folder = test_set_folder[1:-1]
    
    # Validate the test set folder exists
    if not os.path.exists(test_set_folder):
        print(f"ERROR: Test set folder not found - {test_set_folder}")
        return
    
    if not os.path.isdir(test_set_folder):
        print(f"ERROR: Path is not a directory - {test_set_folder}")
        return
    
    # Find all patient folders in the test set directory
    patient_folders = []
    try:
        for item in os.listdir(test_set_folder):
            item_path = os.path.join(test_set_folder, item)
            if os.path.isdir(item_path):
                patient_folders.append(item)
    except Exception as e:
        print(f"ERROR: Cannot read test set folder - {e}")
        return
    
    if not patient_folders:
        print(f"ERROR: No patient folders found in {test_set_folder}")
        return
    
    patient_folders.sort()  # Sort folders alphabetically
    print(f"\nFound {len(patient_folders)} patient folders: {', '.join(patient_folders)}")
    print()
    
    print("Extracting Patient Data from RTPLAN and Centroid Files")
    print("=" * 60)
    print()
    
    results = []
    
    for folder_name in patient_folders:
        folder_path = os.path.join(test_set_folder, folder_name)
        
        print(f"Processing {folder_name}...")
        
        # Look for RTPLAN file (RP.dcm or any .dcm file)
        rtplan_path = None
        for filename in os.listdir(folder_path):
            if filename.lower() == 'rp.dcm' or (filename.lower().endswith('.dcm') and 'plan' in filename.lower()):
                rtplan_path = os.path.join(folder_path, filename)
                break
        
        if not rtplan_path:
            # Look for any .dcm file as fallback
            for filename in os.listdir(folder_path):
                if filename.lower().endswith('.dcm'):
                    rtplan_path = os.path.join(folder_path, filename)
                    break
        
        if not rtplan_path:
            print(f"  ERROR: No RTPLAN (.dcm) file found in {folder_path}")
            continue
        
        # Extract isocenter coordinates and patient ID from RTPLAN
        rtplan_patient_id, isocenter_coords = extract_isocenter_coordinates(rtplan_path)
        
        if rtplan_patient_id is None:
            print(f"  ERROR: {isocenter_coords}")
            continue
        
        # Find centroid file in the patient folder (any .txt file containing 'centroid')
        centroid_patient_id = "Unknown"
        centroid_coords = "Unknown"
        centroid_file = None
        
        try:
            for filename in os.listdir(folder_path):
                if filename.lower().endswith('.txt') and 'centroid' in filename.lower():
                    centroid_file = os.path.join(folder_path, filename)
                    break
        except Exception as e:
            print(f"  ERROR accessing folder {folder_path}: {e}")
        
        if centroid_file and os.path.exists(centroid_file):
            try:
                with open(centroid_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        centroid_patient_id = lines[0].strip()
                        # Look for the Centroid line (usually last line)
                        for line in lines:
                            if "Centroid (cm)" in line:
                                # Extract coordinates from line like "Centroid (cm) , X= -0.36, Y= 11.00 , Z=-2.70"
                                parts = line.split(',')
                                if len(parts) >= 3:
                                    x_part = parts[1].strip().replace('X=', '').strip()
                                    y_part = parts[2].strip().replace('Y=', '').strip()
                                    z_part = parts[3].strip().replace('Z=', '').strip()
                                    centroid_coords = f"X={x_part}, Y={y_part}, Z={z_part}"
                                break
                print(f"  Found centroid file: {os.path.basename(centroid_file)}")
            except Exception as e:
                print(f"  ERROR reading centroid file: {e}")
        else:
            print(f"  WARNING: No centroid file found in {folder_path}")
        
        print(f"  Folder: {folder_name}")
        print(f"  RTPLAN Patient ID: {rtplan_patient_id}")
        print(f"  Centroid Patient ID: {centroid_patient_id}")
        print(f"  Isocenter: {isocenter_coords}")
        print(f"  Centroid: {centroid_coords}")
        
        results.append({
            'folder': folder_name,
            'rtplan_patient_id': rtplan_patient_id,
            'centroid_patient_id': centroid_patient_id,
            'isocenter': isocenter_coords,
            'centroid': centroid_coords
        })
        
        print()
    
    # Summary Table
    print("DETAILED COMPARISON TABLE")
    print("=" * 120)
    print(f"{'Folder':<10} {'RTPLAN PatientID':<16} {'Centroid PatientID':<17} {'Isocenter (cm)':<25} {'Centroid (cm)':<25} {'Match':<6}")
    print("-" * 120)
    
    def normalize_coordinates(coord_str):
        """Normalize coordinate string for comparison by removing extra spaces and standardizing format."""
        if coord_str == "Unknown":
            return coord_str
        # Extract X, Y, Z values and reformat consistently
        try:
            parts = coord_str.split(',')
            if len(parts) >= 3:
                x_val = parts[0].split('=')[1].strip()
                y_val = parts[1].split('=')[1].strip() 
                z_val = parts[2].split('=')[1].strip()
                return f"X={x_val}, Y={y_val}, Z={z_val}"
        except:
            pass
        return coord_str
    
    for result in results:
        norm_iso = normalize_coordinates(result['isocenter'])
        norm_cent = normalize_coordinates(result['centroid'])
        match = "YES" if norm_iso == norm_cent else "NO"
        print(f"{result['folder']:<10} {result['rtplan_patient_id']:<16} {result['centroid_patient_id']:<17} {result['isocenter']:<25} {result['centroid']:<25} {match:<6}")
    
    # Write summary to file
    output_file = os.path.join(test_set_folder, "detailed_comparison.txt")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("DETAILED COMPARISON TABLE\n")
            f.write("=" * 120 + "\n")
            f.write(f"{'Folder':<10} {'RTPLAN PatientID':<16} {'Centroid PatientID':<17} {'Isocenter (cm)':<25} {'Centroid (cm)':<25} {'Match':<6}\n")
            f.write("-" * 120 + "\n")
            
            for result in results:
                norm_iso = normalize_coordinates(result['isocenter'])
                norm_cent = normalize_coordinates(result['centroid'])
                match = "YES" if norm_iso == norm_cent else "NO"
                f.write(f"{result['folder']:<10} {result['rtplan_patient_id']:<16} {result['centroid_patient_id']:<17} {result['isocenter']:<25} {result['centroid']:<25} {match:<6}\n")
        
        print(f"\nDetailed comparison saved to: {output_file}")
    except Exception as e:
        print(f"\nERROR saving comparison file: {e}")

if __name__ == "__main__":
    main()