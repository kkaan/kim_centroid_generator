# Test Plan: KIM Centroid Generator
## Interactive Mode Feature Testing

**Branch:** `allow-terminal-interactions`
**Application:** KIM_Centroid_using_Folder_Monitoring.py
**Purpose:** Validate all functionality before building executable

---

## Pre-Test Setup

### 1. Environment Preparation
```bash
# Ensure dependencies are installed
pip install -r requirements.txt

# Verify Python environment
python --version  # Should work with Python 3.x
```

### 2. Directory Structure
```
C:\kim\                    # Main monitoring folder
C:\kim\backup\             # Auto-created backup folder
C:\test-data\              # Your test files location
C:\test-results\           # Store test outputs for comparison
```

### 3. Test Data Requirements
- RTSTRUCT files with various structure naming conventions
- Matching RTPLAN files
- Known correct centroid output files for validation
- Malformed DICOM files for error handling tests

---

## Test Categories

## Category 1: Basic Functionality Tests

### Test 1.1: Standard File Processing (Non-Interactive)
**Objective:** Verify basic centroid calculation with default seed structures

**Priority:** HIGH

**Test Data Needed:**
- RTSTRUCT file with standard structures (seed1, seed2, seed3 or au1, au2, au3)
- Matching RTPLAN file (same Patient ID)
- Known correct centroid output file

**Steps:**
1. Start application in non-interactive mode:
   ```bash
   python KIM_Centroid_using_Folder_Monitoring.py --folder C:\kim
   # Choose "n" when prompted for interactive mode
   ```
2. Copy test RTSTRUCT and RTPLAN files to `C:\kim\`
3. Wait for processing to complete (watch console output)
4. Verify output files created

**Expected Results:**
- Console shows: "Detected file: [path]" for each file
- Console shows: "File [path] identified with Modality: RTSTRUCT" and "RTPLAN"
- Console shows: "Patient IDs match"
- Console shows: "Found [structure] with ROINumber: [N]" for each structure
- Console shows: "Calculated centroid for [structure]: [coordinates]"
- Output folder created: `C:\kim\{PatientID}_BeamID_{Beam1}_{Beam2}\`
- Output file created: `Centroid_{PatientID}_BeamID_{Beam1}_{Beam2}.txt`
- Both DICOM files moved to `C:\kim\backup\`
- Original monitoring folder empty (except backup subfolder)

**Validation Checklist:**
- [ ] Files detected and identified correctly
- [ ] Patient ID verified between RTSTRUCT and RTPLAN
- [ ] All expected structures found
- [ ] Centroids calculated
- [ ] Output folder created with correct naming
- [ ] Output file created
- [ ] Files moved to backup
- [ ] Output matches known good file

**Output File Validation:**
```bash
# Compare your output with known good output
fc C:\kim\{PatientID}_BeamID_{Beam1}_{Beam2}\Centroid_*.txt C:\test-data\known_centroid_output.txt
```

**What to Check in Output:**
- Line 1: Patient ID matches expected
- Line 2: Patient Name matches (^ replaced with ,)
- Structure lines: Name, X, Y, Z coordinates in cm (2 decimal places)
- Isocenter line: Present and in correct format
- Centroid coordinates match known values (±0.01 cm tolerance for floating-point)

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Date Tested: __________
Tester: __________
Actual Output Location: __________
Issues Found: __________
```

---

### Test 1.2: Case-Insensitive Structure Name Matching
**Objective:** Verify structure name matching works with various capitalizations

**Priority:** MEDIUM

**Test Variations:**
| Variation | Structure Names in DICOM | Expected Result |
|-----------|-------------------------|-----------------|
| A | "Seed1", "Seed2", "Seed3" | All found |
| B | "SEED1", "SEED2", "SEED3" | All found |
| C | "seed1", "seed2", "seed3" | All found |
| D | "sEeD1", "SeEd2", "sEEd3" | All found |
| E | "Au1", "Au2", "Au3" | All found |
| F | "AU1", "AU2", "AU3" | All found |

**Steps:**
1. For each variation, prepare RTSTRUCT with specified structure names
2. Run application in non-interactive mode
3. Copy files to monitoring folder
4. Verify all structures found and processed

**Expected:** All variations should be found and processed correctly

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Variations Tested: __________
Any Failed: __________
```

---

### Test 1.3: Flexible Naming Convention (With Spaces)
**Objective:** Verify both "seed1" and "seed 1" (with space) formats work

**Priority:** MEDIUM

**Test Data Variations:**
- Structures: "seed 1", "seed 2", "seed 3" (with spaces)
- Structures: "au 1", "au 2", "au 3" (with spaces)
- Mixed: "seed1", "seed 2", "au 3"

**Steps:**
1. Prepare RTSTRUCT files with space-separated names
2. Run application in non-interactive mode
3. Verify all structures found

**Expected:** All structures found and processed regardless of space presence

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Test Data Used: __________
Structures Found: __________
```

---

## Category 2: Interactive Mode Tests

### Test 2.1: Interactive Mode - Custom Structure Selection
**Objective:** Test user selection of non-standard structures

**Priority:** HIGH (Core new feature)

**Test Data:** RTSTRUCT with structures NOT matching defaults
- Example: "Marker_A", "Marker_B", "GTV", "PTV"

**Steps:**
1. Start in interactive mode:
   ```bash
   python KIM_Centroid_using_Folder_Monitoring.py --interactive
   ```
2. Copy test files to monitoring folder
3. Wait for prompt showing available structures
4. Enter selection: "1,2,3" (select first three structures)
5. Verify processing continues

**Expected:**
- Console shows: "No default structures found. Attempting interactive structure selection..."
- Prompt displays numbered list of all available structures
- User input accepted
- Console shows: "Selected structures: [list]"
- Console shows: "Processing user-selected structure: [name]" for each
- Output file created with selected structures
- Structure names in output use title case of original names

**Validation:**
- [ ] Prompt appeared when no defaults found
- [ ] All structures listed with numbers
- [ ] User input accepted
- [ ] Only selected structures processed
- [ ] Output file created
- [ ] Structure names preserved correctly

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Structures in Test File: __________
User Selection: __________
Structures in Output: __________
```

---

### Test 2.2: Interactive Mode - Select All
**Objective:** Verify "all" option works

**Priority:** MEDIUM

**Test Data:** RTSTRUCT with multiple non-standard structures

**Steps:**
1. Start in interactive mode
2. Copy test files to monitoring folder
3. When prompted, type "all"
4. Press Enter

**Expected:**
- Console shows: "Selected all [N] structures"
- All structures processed
- Output file contains all structures

**Validation:**
- [ ] "all" option accepted
- [ ] All structures processed
- [ ] Output contains all structures

**Result:** [ ] PASS  [ ] FAIL

---

### Test 2.3: Interactive Mode - Skip File
**Objective:** Verify "skip" option works

**Priority:** MEDIUM

**Steps:**
1. Start in interactive mode
2. Copy test files to monitoring folder
3. When prompted, type "skip"
4. Press Enter

**Expected:**
- Console shows: "Skipping this file pair..."
- Console shows: "User chose to skip this file pair."
- No output file created
- Application continues monitoring
- Files moved to backup folder

**Validation:**
- [ ] Skip message displayed
- [ ] No output file created
- [ ] Application still running
- [ ] Files moved to backup
- [ ] Can process next file pair

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Files moved to backup: YES / NO
Application continued monitoring: YES / NO
```

---

### Test 2.4: Interactive Mode - Invalid Input Handling
**Objective:** Test error handling for bad user input

**Priority:** HIGH (Robustness)

**Invalid Inputs to Test:**
| Input | Type of Error | Expected Behavior |
|-------|--------------|-------------------|
| "0" | Out of range (too low) | Error message, re-prompt |
| "99" | Out of range (too high) | Error message, re-prompt |
| "-1" | Negative number | Error message, re-prompt |
| "abc" | Non-numeric | Error message, re-prompt |
| "1-3" | Wrong format | Error message, re-prompt |
| "1 2 3" | Wrong separator | Error message, re-prompt |
| "" | Empty input | Error message, re-prompt |

**Steps:**
1. Start interactive mode
2. Copy test files
3. At prompt, enter each invalid input
4. Verify error handling

**Expected for Each:**
- Error message: "Invalid input. Please enter numbers separated by commas, 'all', or 'skip'"
- Prompt appears again
- No crash or hang
- Can enter valid input after error

**Validation:**
- [ ] All invalid inputs rejected
- [ ] Appropriate error messages shown
- [ ] Re-prompt works
- [ ] No crashes
- [ ] Can recover with valid input

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Inputs Tested: __________
Any Unexpected Behaviors: __________
```

---

### Test 2.5: Interactive Mode Startup Prompt
**Objective:** Test startup configuration dialog

**Priority:** HIGH (User experience)

**Test Variations:**

**A. Enable Interactive Mode:**
```bash
python KIM_Centroid_using_Folder_Monitoring.py
# When prompted: Enter "y"
```
Expected: "Interactive mode ENABLED" message

**B. Disable Interactive Mode:**
```bash
python KIM_Centroid_using_Folder_Monitoring.py
# When prompted: Enter "n"
```
Expected: "Interactive mode DISABLED" message

**C. Alternative Yes Inputs:**
Try: "yes", "Y", "YES", "Yes"
Expected: All should enable interactive mode

**D. Alternative No Inputs:**
Try: "no", "N", "NO", "No"
Expected: All should disable interactive mode

**E. Invalid Input:**
Try: "maybe", "1", "true", etc.
Expected: "Please enter 'y' for yes or 'n' for no." and re-prompt

**F. Keyboard Interrupt (Ctrl+C):**
Expected: "Operation cancelled. Defaulting to non-interactive mode."

**G. Command-Line Override:**
```bash
python KIM_Centroid_using_Folder_Monitoring.py --interactive
```
Expected: No prompt, directly to "Interactive mode ENABLED via command line argument."

**Validation:**
- [ ] Prompt appears at startup (without --interactive flag)
- [ ] All yes variations work
- [ ] All no variations work
- [ ] Invalid input handled gracefully
- [ ] Ctrl+C handled gracefully
- [ ] --interactive flag skips prompt

**Result:** [ ] PASS  [ ] FAIL

---

## Category 3: Edge Cases & Error Handling

### Test 3.1: Patient ID Mismatch
**Objective:** Verify rejection of mismatched patient IDs

**Priority:** HIGH (Data integrity)

**Test Data:**
- RTSTRUCT with Patient ID: "PATIENT001"
- RTPLAN with Patient ID: "PATIENT002"

**Steps:**
1. Start application
2. Copy mismatched files to monitoring folder
3. Observe behavior

**Expected:**
- Console shows: "Patient IDs do not match. Structure Patient ID: PATIENT001, Plan Patient ID: PATIENT002"
- No output file created
- Processing stops for this pair
- Application continues monitoring
- Files may or may not be moved to backup (document behavior)

**Validation:**
- [ ] Mismatch detected
- [ ] Error message clear and accurate
- [ ] No output file created
- [ ] Application continues running
- [ ] Files handled appropriately

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Files moved to backup: YES / NO
Error message: __________
```

---

### Test 3.2: Missing Structures
**Objective:** Test behavior when no target structures exist

**Priority:** HIGH

**Test Data:** RTSTRUCT with only clinical structures (e.g., "GTV", "PTV", "Bladder", "Rectum")

**Test A: Non-Interactive Mode**
**Steps:**
1. Run with interactive mode disabled
2. Copy files with no seed/marker structures

**Expected:**
- Console shows attempts to find each possible structure name
- Console shows: "No targetable structures with valid contours were found. Centroid file will not be generated."
- No output file created
- Application continues monitoring
- Files moved to backup

**Validation:**
- [ ] Search attempts logged
- [ ] Appropriate message displayed
- [ ] No output file created
- [ ] Graceful handling

**Test B: Interactive Mode**
**Steps:**
1. Run with interactive mode enabled
2. Copy files with no seed/marker structures

**Expected:**
- Console shows: "No default structures found. Attempting interactive structure selection..."
- Prompt appears showing available structures
- User can select any structure
- Selected structures processed

**Validation:**
- [ ] Interactive prompt appears
- [ ] All structures available for selection
- [ ] Selected structures processed

**Result:** [ ] PASS  [ ] FAIL

---

### Test 3.3: Empty Contour Data
**Objective:** Verify handling of structures with no contour points

**Priority:** MEDIUM

**Test Data:** RTSTRUCT with:
- Structure defined in StructureSetROISequence
- But ContourSequence is empty or missing for that structure

**Steps:**
1. Copy test files
2. Observe handling

**Expected:**
- Console shows: "Structure '[name]' (ROINumber: [N]) found, but its ContourSequence is missing or empty."
- Structure skipped
- Other valid structures still processed
- Output file created if other structures valid

**Validation:**
- [ ] Empty contour detected
- [ ] Warning message displayed
- [ ] Structure skipped
- [ ] Other structures processed
- [ ] No crash

**Result:** [ ] PASS  [ ] FAIL

---

### Test 3.4: Malformed DICOM Files
**Objective:** Test robustness against corrupted files

**Priority:** HIGH (Robustness)

**Test Variations:**

**A. Non-DICOM File:**
- Create text file, rename to .dcm
- Copy to monitoring folder

Expected:
- Error: "Error reading DICOM metadata from [path]: [error]. File may not be a valid DICOM file or is corrupted."
- File skipped, monitoring continues

**B. DICOM Missing Modality Tag:**
- Use DICOM file with Modality tag removed

Expected:
- Warning: "Modality tag missing in [path]. Cannot determine if it's RTSTRUCT or RTPLAN. Skipping file."
- File skipped, monitoring continues

**C. DICOM Missing Required Tags:**
- RTSTRUCT without StructureSetROISequence
- RTPLAN without BeamSequence

Expected:
- Appropriate error messages during processing
- Graceful failure
- Monitoring continues

**Validation:**
- [ ] All malformed files handled gracefully
- [ ] Appropriate error messages
- [ ] No application crashes
- [ ] Monitoring continues after errors

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Test Variations Attempted: __________
Any Crashes: YES / NO
Error Messages Appropriate: YES / NO
```

---

### Test 3.5: Missing Isocenter
**Objective:** Verify handling when RTPLAN lacks isocenter data

**Priority:** MEDIUM

**Test Data:** RTPLAN without IsocenterPosition in ControlPointSequence

**Steps:**
1. Copy RTSTRUCT and RTPLAN without isocenter
2. Observe processing

**Expected:**
- Console shows: "No isocenter data found in RT Plan after checking all beams and control points."
- Output file still created
- Structure centroids calculated normally
- Output file contains: "No isocenter data found."
- Processing completes successfully

**Validation:**
- [ ] Missing isocenter detected
- [ ] Warning message displayed
- [ ] Output file still created
- [ ] Centroids calculated correctly
- [ ] Output shows "No isocenter data found."

**Result:** [ ] PASS  [ ] FAIL

---

### Test 3.6: File Pair Detection
**Objective:** Test detection of RTSTRUCT/RTPLAN pairs

**Priority:** HIGH (Core functionality)

**Test Scenarios:**

**A. RTSTRUCT First:**
1. Copy RTSTRUCT to monitoring folder
2. Wait 5 seconds
3. Copy matching RTPLAN

Expected:
- RTSTRUCT detected and stored
- "Waiting for the corresponding RTSTRUCT/RTPLAN file to complete the pair."
- RTPLAN detected
- "Both RTSTRUCT (...) and RTPLAN (...) files detected. Initiating processing."
- Processing begins

**B. RTPLAN First:**
1. Copy RTPLAN to monitoring folder
2. Wait 5 seconds
3. Copy matching RTSTRUCT

Expected: Same as above, order shouldn't matter

**C. Only RTSTRUCT (Incomplete Pair):**
1. Copy only RTSTRUCT
2. Wait 30 seconds
3. Verify no processing occurs

Expected:
- RTSTRUCT detected
- "Waiting for the corresponding RTSTRUCT/RTPLAN file to complete the pair."
- No processing until RTPLAN arrives

**D. Only RTPLAN (Incomplete Pair):**
Same as C but with RTPLAN

**Validation:**
- [ ] Both file orders work correctly
- [ ] Incomplete pairs don't trigger processing
- [ ] Clear console messages about waiting
- [ ] Processing starts immediately when pair complete

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Order Tested: __________
Wait Time Between Files: __________
Processing Triggered Correctly: YES / NO
```

---

### Test 3.7: File Transfer in Progress
**Objective:** Test wait_for_file_ready() functionality

**Priority:** MEDIUM

**Test Setup:**
- Use large DICOM file (>10MB if possible)
- Or simulate slow network copy

**Steps:**
1. Start copying large file to monitoring folder
2. Observe console messages
3. Let copy complete
4. Verify processing waits

**Expected:**
- File detected immediately: "Detected file: [path]"
- Application waits for file to stabilize
- "Attempting to read DICOM metadata from: [path]" only after file ready
- No errors about file access or incomplete reads

**Validation:**
- [ ] File detected during copy
- [ ] Application waits for stability
- [ ] No premature read attempts
- [ ] Processing succeeds after copy complete

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
File Size Used: __________
Copy Duration: __________
Wait Functionality Worked: YES / NO
```

---

### Test 3.8: Existing Output File Overwrite
**Objective:** Verify overwrite behavior for existing output files

**Priority:** MEDIUM

**Steps:**
1. Manually create output folder: `C:\kim\TEST001_BeamID_Beam1_Beam2\`
2. Create output file: `Centroid_TEST001_BeamID_Beam1_Beam2.txt` with dummy content
3. Copy matching DICOM files that will generate same output
4. Observe behavior

**Expected:**
- Console shows: "Output file [path] already exists. It will be overwritten."
- Console shows: "Successfully removed existing file: [path]"
- New file created with correct content
- No errors
- Old content replaced

**Validation:**
- [ ] Existing file detected
- [ ] Warning message displayed
- [ ] Old file removed
- [ ] New file created
- [ ] No errors during overwrite

**Result:** [ ] PASS  [ ] FAIL

---

## Category 4: File Management Tests

### Test 4.1: Output Directory Creation
**Objective:** Verify patient-specific folder creation

**Priority:** MEDIUM

**Test Scenarios:**

**A. New Directory:**
Patient ID: "TEST001", Beam IDs: "Beam1", "Beam2"
Expected folder: `C:\kim\TEST001_BeamID_Beam1_Beam2\`

**B. Existing Directory:**
Pre-create the folder, then process files
Expected: No error, uses existing folder

**C. Multiple Beams:**
Patient with 3+ beams in RTPLAN
Expected: Uses first two beam IDs in folder name

**D. Insufficient Beams:**
Patient with only 1 beam or no beams
Expected: Simplified folder name (just Patient ID)

**Validation:**
- [ ] Folder created with correct naming
- [ ] Console shows: "Successfully created output directory: [path]"
- [ ] Existing folders handled gracefully
- [ ] Beam ID variations handled correctly

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Test Scenarios Completed: __________
Folder Naming Correct: YES / NO
```

---

### Test 4.2: Backup File Movement
**Objective:** Verify files moved to backup after processing

**Priority:** HIGH (Data management)

**Steps:**
1. Process a complete file pair
2. Check monitoring folder
3. Check backup folder

**Expected:**
- Console shows: "Moved [RTSTRUCT_path] to [backup_path]"
- Console shows: "Moved [RTPLAN_path] to [backup_path]"
- Console shows: "Moved DICOM files to C:\kim\backup"
- Both files present in `C:\kim\backup\`
- Both files removed from `C:\kim\`
- Monitoring folder empty (except output folder and backup subfolder)

**Test Existing File in Backup:**
1. Manually place file with same name in backup folder
2. Process files that will generate same filename
3. Verify overwrite

Expected:
- Existing backup file overwritten
- No error
- New file in backup

**Validation:**
- [ ] Files moved correctly
- [ ] Original location cleared
- [ ] Backup folder contains files
- [ ] Existing backups overwritten cleanly

**Result:** [ ] PASS  [ ] FAIL

---

### Test 4.3: Beam ID Handling
**Objective:** Test output naming with various beam configurations

**Priority:** LOW

**Test Scenarios:**

| Beams in RTPLAN | Expected Folder Name | Expected File Name |
|-----------------|---------------------|-------------------|
| 2+ beams | `{PatientID}_BeamID_{Beam1}_{Beam2}` | `Centroid_{PatientID}_BeamID_{Beam1}_{Beam2}.txt` |
| 1 beam | `{PatientID}` | `Centroid_{PatientID}.txt` |
| 0 beams | `{PatientID}` | `Centroid_{PatientID}.txt` |

**Expected for <2 Beams:**
- Console shows: "Warning: Less than two Beam IDs found. Output filename will be simplified."
- Simplified naming used
- Processing completes successfully

**Validation:**
- [ ] 2+ beams: Full naming
- [ ] <2 beams: Simplified naming
- [ ] Warning message for <2 beams
- [ ] All scenarios process correctly

**Result:** [ ] PASS  [ ] FAIL

---

## Category 5: Command-Line Interface Tests

### Test 5.1: Custom Folder Argument
**Objective:** Verify --folder argument works

**Priority:** MEDIUM

**Steps:**
1. Create custom monitoring folder: `C:\test-dicom\`
2. Run with custom folder:
   ```bash
   python KIM_Centroid_using_Folder_Monitoring.py --folder C:\test-dicom
   ```
3. Verify application monitors correct folder

**Expected:**
- Console shows: "Initializing DICOM monitoring script for folder: C:\test-dicom"
- Console shows: "Monitoring folder: C:\test-dicom"
- Files copied to `C:\test-dicom` are detected
- Files in `C:\kim` are NOT detected
- Output folder created in `C:\test-dicom`
- Backup folder created as `C:\test-dicom\backup\`

**Validation:**
- [ ] Custom folder monitored
- [ ] Correct folder shown in console
- [ ] Files detected in custom location
- [ ] Output/backup in custom location
- [ ] Default folder not monitored

**Result:** [ ] PASS  [ ] FAIL

---

### Test 5.2: Combined Arguments
**Objective:** Test multiple arguments together

**Priority:** MEDIUM

**Command:**
```bash
python KIM_Centroid_using_Folder_Monitoring.py --folder C:\test-dicom --interactive
```

**Expected:**
- Custom folder monitored
- Interactive mode enabled (no startup prompt)
- Console shows both settings acknowledged
- Both features work correctly together

**Validation:**
- [ ] Custom folder used
- [ ] Interactive mode enabled
- [ ] No startup prompt
- [ ] Both features functional

**Result:** [ ] PASS  [ ] FAIL

---

### Test 5.3: Help Display
**Objective:** Verify help text is clear and accurate

**Priority:** LOW

**Command:**
```bash
python KIM_Centroid_using_Folder_Monitoring.py --help
```

**Expected Output Should Include:**
- Script description
- `-f`, `--folder` argument description and default
- `-i`, `--interactive` argument description
- Usage examples (optional but helpful)

**Validation:**
- [ ] Help text displays
- [ ] All arguments documented
- [ ] Descriptions clear
- [ ] Defaults shown

**Result:** [ ] PASS  [ ] FAIL

---

## Category 6: Output Validation Tests

### Test 6.1: Output File Format
**Objective:** Verify correct output structure and formatting

**Priority:** HIGH

**Expected Format:**
```
{PatientID}
{PatientName}
{StructureName}, X= {X:.2f}, Y= {Y:.2f}, Z= {Z:.2f}
{StructureName}, X= {X:.2f}, Y= {Y:.2f}, Z= {Z:.2f}
...
Isocenter (cm), X= {X:.2f}, Y= {Y:.2f}, Z= {Z:.2f}
```

**Format Validation Checklist:**
- [ ] Patient ID on line 1 (exact match)
- [ ] Patient Name on line 2 (^ character replaced with ,)
- [ ] Each structure on separate line
- [ ] Structure name in title case
- [ ] Format: `{Name}, X= {value}, Y= {value}, Z= {value}`
- [ ] Values in centimeters (not millimeters)
- [ ] Exactly 2 decimal places (e.g., "10.25" not "10.2" or "10.250")
- [ ] Isocenter line last (or "No isocenter data found.")
- [ ] No extra blank lines
- [ ] No trailing whitespace

**Example Valid Output:**
```
TEST001
Doe, John
Seed1, X= 10.25, Y= 20.50, Z= 30.75
Seed2, X= 11.00, Y= 21.25, Z= 31.50
Au 1, X= 12.50, Y= 22.00, Z= 32.25
Isocenter (cm), X= 0.00, Y= 0.00, Z= 0.00
```

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Sample Output:
__________
```

---

### Test 6.2: Coordinate Conversion Accuracy
**Objective:** Verify mm to cm conversion is correct

**Priority:** HIGH (Data accuracy)

**Manual Calculation Test:**

If DICOM coordinates are:
- Seed1: (100.0, 200.5, 300.75) mm
- Isocenter: (1234.5, 2345.67, 3456.789) mm

Expected output:
- Seed1: (10.00, 20.05, 30.08) cm  [note: 30.075 rounds to 30.08]
- Isocenter: (123.45, 234.57, 345.68) cm

**Validation Method:**
1. Read raw DICOM coordinates using pydicom viewer or tool
2. Manually calculate conversion: mm / 10.0
3. Round to 2 decimal places
4. Compare with output file

**Test Cases:**
| DICOM (mm) | Expected (cm) | Actual (cm) | Match |
|------------|---------------|-------------|-------|
| 0.0 | 0.00 | | [ ] |
| 100.0 | 10.00 | | [ ] |
| 123.45 | 12.35 | | [ ] |
| 999.99 | 100.00 | | [ ] |
| -50.0 | -5.00 | | [ ] |

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Conversion Formula Verified: YES / NO
All Test Cases Match: YES / NO
```

---

### Test 6.3: Structure Name Formatting
**Objective:** Verify title case formatting in output

**Priority:** LOW

**Test Cases:**

| DICOM Structure Name | Expected Output Name |
|---------------------|---------------------|
| "seed1" | "Seed1" |
| "SEED1" | "Seed1" |
| "au 2" | "Au 2" |
| "AU 2" | "Au 2" |
| "marker_a" | "Marker_A" |
| "gold marker" | "Gold Marker" |
| "GTV" | "Gtv" |

**Steps:**
1. For each test case, create RTSTRUCT with specified name
2. Process files
3. Check output file name formatting

**Validation:**
- [ ] All names properly title-cased
- [ ] Spaces preserved
- [ ] Underscores preserved
- [ ] Consistent formatting

**Result:** [ ] PASS  [ ] FAIL

---

## Category 7: Long-Running & Stability Tests

### Test 7.1: Continuous Monitoring
**Objective:** Verify application runs continuously without degradation

**Priority:** MEDIUM

**Duration:** 1+ hours

**Steps:**
1. Start application
2. Process multiple file pairs over time (at least 5 pairs)
3. Wait idle periods between pairs (at least 10 minutes)
4. Monitor system resources (Task Manager)

**Expected:**
- All files processed correctly throughout test
- No memory leaks (memory usage stable)
- No performance degradation
- Continues monitoring after each pair
- Console output remains responsive
- Application doesn't hang or freeze

**Monitoring Checklist:**
- [ ] Start memory usage: ______ MB
- [ ] Memory after 30 min: ______ MB
- [ ] Memory after 60 min: ______ MB
- [ ] CPU usage remains low when idle
- [ ] All file pairs processed successfully
- [ ] No errors or warnings over time
- [ ] Application responsive throughout

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Test Duration: __________
File Pairs Processed: __________
Memory Stable: YES / NO
Any Issues: __________
```

---

### Test 7.2: Keyboard Interrupt (Ctrl+C)
**Objective:** Test graceful shutdown

**Priority:** MEDIUM

**Test Scenarios:**

**A. Interrupt During Idle Monitoring:**
1. Start application
2. Wait until monitoring (no active processing)
3. Press Ctrl+C

Expected:
- Clean shutdown
- Observer stopped
- No error traceback
- Application exits immediately

**B. Interrupt During Processing:**
1. Start application
2. Copy files to trigger processing
3. Press Ctrl+C during processing

Expected:
- Processing stops
- Clean shutdown or completes current operation
- Application exits
- Document behavior (immediate vs. graceful completion)

**Validation:**
- [ ] Ctrl+C recognized
- [ ] Clean exit
- [ ] No error traceback
- [ ] No zombie processes
- [ ] Behavior documented

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Interrupt Timing: IDLE / PROCESSING
Exit Clean: YES / NO
Behavior: __________
```

---

## Category 8: Regression Tests

### Test 8.1: Non-Interactive Mode Matches Main Branch
**Objective:** Verify backward compatibility with main branch

**Priority:** HIGH

**Requirements:**
- Same test data used on both branches
- Known good output from main branch

**Steps:**
1. Checkout main branch:
   ```bash
   git checkout main
   ```
2. Run test with standard seed structures:
   ```bash
   python KIM_Centroid_using_Folder_Monitoring.py --folder C:\kim
   ```
3. Save output file as `main_branch_output.txt`
4. Checkout allow-terminal-interactions branch:
   ```bash
   git checkout allow-terminal-interactions
   ```
5. Run same test in non-interactive mode:
   ```bash
   python KIM_Centroid_using_Folder_Monitoring.py --folder C:\kim
   # Choose "n" for interactive mode
   ```
6. Compare outputs:
   ```bash
   fc main_branch_output.txt {new_output}.txt
   ```

**Expected:**
- Identical output files (byte-for-byte match)
- Same console messages (except interactive mode prompt)
- Same processing behavior
- Same file handling

**Validation:**
- [ ] Output files identical
- [ ] Processing behavior identical
- [ ] No regressions introduced
- [ ] Console output similar (except new prompt)

**Result:** [ ] PASS  [ ] FAIL

**Notes:**
```
Differences Found: __________
Acceptable Differences: __________
Regressions: YES / NO
```

---

## Test Execution Tracking

### Quick Checklist

```
BASIC FUNCTIONALITY:
[ ] Test 1.1: Standard File Processing
[ ] Test 1.2: Case-Insensitive Matching
[ ] Test 1.3: Flexible Naming Convention

INTERACTIVE MODE:
[ ] Test 2.1: Interactive Custom Selection
[ ] Test 2.2: Interactive Select All
[ ] Test 2.3: Interactive Skip File
[ ] Test 2.4: Interactive Invalid Input
[ ] Test 2.5: Interactive Startup Prompt

EDGE CASES & ERROR HANDLING:
[ ] Test 3.1: Patient ID Mismatch
[ ] Test 3.2: Missing Structures
[ ] Test 3.3: Empty Contour Data
[ ] Test 3.4: Malformed DICOM Files
[ ] Test 3.5: Missing Isocenter
[ ] Test 3.6: File Pair Detection
[ ] Test 3.7: File Transfer in Progress
[ ] Test 3.8: Existing Output File

FILE MANAGEMENT:
[ ] Test 4.1: Output Directory Creation
[ ] Test 4.2: Backup File Movement
[ ] Test 4.3: Beam ID Handling

COMMAND-LINE INTERFACE:
[ ] Test 5.1: Custom Folder Argument
[ ] Test 5.2: Combined Arguments
[ ] Test 5.3: Help Display

OUTPUT VALIDATION:
[ ] Test 6.1: Output File Format
[ ] Test 6.2: Coordinate Conversion
[ ] Test 6.3: Structure Name Formatting

STABILITY:
[ ] Test 7.1: Continuous Monitoring
[ ] Test 7.2: Keyboard Interrupt

REGRESSION:
[ ] Test 8.1: Non-Interactive Mode Unchanged
```

---

## Test Summary Template

```
=============================================================================
TEST EXECUTION SUMMARY
=============================================================================

Date: __________
Tester: __________
Branch: allow-terminal-interactions
Commit Hash: __________
Python Version: __________

Environment:
- OS: Windows __________
- Dependencies: Installed from requirements.txt

Test Results Overview:
- Total Tests Planned: 26
- Tests Executed: ____
- Tests Passed: ____
- Tests Failed: ____
- Tests Skipped: ____
- Pass Rate: _____%

Critical Issues Found:
1. __________
2. __________

Medium Priority Issues:
1. __________
2. __________

Minor Issues:
1. __________
2. __________

Recommendation:
[ ] READY FOR EXECUTABLE BUILD
[ ] REQUIRES FIXES BEFORE BUILD
[ ] REQUIRES ADDITIONAL TESTING

Notes:
__________

Tester Signature: __________
Date: __________
=============================================================================
```

---

## Quick Test Script Template

For documenting each test execution:

```
=============================================================================
TEST ID: [e.g., Test 1.1]
TEST NAME: [e.g., Standard File Processing]
=============================================================================

Date: __________
Tester: __________
Branch: allow-terminal-interactions
Commit: __________

TEST DATA USED:
- RTSTRUCT File: __________
- RTPLAN File: __________
- Known Good Output: __________

STEPS EXECUTED:
1. __________
2. __________
3. __________

EXPECTED RESULTS:
- __________
- __________

ACTUAL RESULTS:
- __________
- __________

RESULT: [ ] PASS  [ ] FAIL

EVIDENCE:
- Console Output: [attach or paste]
- Output File Location: __________
- Screenshots: [if applicable]

ISSUES FOUND:
- __________

NOTES:
- __________

=============================================================================
```

---

## Testing Tips

1. **Test Data Organization:**
   - Keep original test files in `C:\test-data\original\`
   - Copy to monitoring folder for each test
   - Preserve originals (never move from test-data)

2. **Clean Between Tests:**
   - Clear `C:\kim\` (except test files being copied)
   - Clear `C:\kim\backup\` or start with empty backup
   - Delete previous output folders

3. **Console Output:**
   - Save console output for each test
   - Use: `python script.py > test_output.log 2>&1`
   - Or copy/paste from terminal to file

4. **Known Good Outputs:**
   - Validate at least one known good output manually first
   - Use this as baseline for all comparisons
   - Document how known good output was verified

5. **Systematic Approach:**
   - Complete all tests in one category before moving to next
   - Document as you go (don't rely on memory)
   - Take breaks between test categories

6. **Issue Tracking:**
   - Document every unexpected behavior
   - Include steps to reproduce
   - Assign priority (Critical/High/Medium/Low)

7. **Version Control:**
   - Note commit hash for tested version
   - If bugs found and fixed, retest affected areas

---

## Pre-Executable Build Checklist

Before building the executable, ensure:

```
MUST PASS:
[ ] Test 1.1: Standard Processing
[ ] Test 2.1: Interactive Custom Selection
[ ] Test 2.5: Interactive Startup Prompt
[ ] Test 3.1: Patient ID Mismatch
[ ] Test 3.4: Malformed DICOM Files
[ ] Test 3.6: File Pair Detection
[ ] Test 4.2: Backup File Movement
[ ] Test 6.1: Output File Format
[ ] Test 6.2: Coordinate Conversion
[ ] Test 8.1: Regression Test

SHOULD PASS (or document known issues):
[ ] All other tests
[ ] No critical or high-priority bugs
[ ] All known issues documented

DOCUMENTATION:
[ ] Test summary completed
[ ] Issues documented with severity
[ ] Known limitations documented
[ ] User guide updated (if needed)
```

---

## End of Test Plan

**Document Version:** 1.0
**Last Updated:** [Date]
**Author:** [Name]

For questions or clarifications about this test plan, refer to:
- Source code: `KIM_Centroid_using_Folder_Monitoring.py`
- Project documentation: `CLAUDE.md`
- Version control: Git branch `allow-terminal-interactions`
