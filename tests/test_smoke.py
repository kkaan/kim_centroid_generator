"""
Smoke tests for KIM Centroid Generator

Basic tests to ensure core functionality works.
These run quickly and catch major breakages.
"""

import sys
import os
import pytest
import numpy as np

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestImports:
    """Test that all required modules can be imported"""

    def test_import_main_module(self):
        """Main Python file imports without errors"""
        import KIM_Centroid_using_Folder_Monitoring
        assert KIM_Centroid_using_Folder_Monitoring is not None

    def test_import_pydicom(self):
        """pydicom library is available"""
        import pydicom
        assert pydicom is not None

    def test_import_numpy(self):
        """numpy library is available"""
        import numpy
        assert numpy is not None

    def test_import_watchdog(self):
        """watchdog library is available"""
        import watchdog
        assert watchdog is not None


class TestDICOMHandler:
    """Test DICOMHandler class initialization"""

    def test_dicom_handler_init(self):
        """DICOMHandler can be instantiated"""
        from KIM_Centroid_using_Folder_Monitoring import DICOMHandler

        # Create handler with dummy file paths
        handler = DICOMHandler(
            "dummy_struct.dcm",
            "dummy_plan.dcm",
            enable_interactive=False
        )

        assert handler is not None
        assert handler.rtstruct_file == "dummy_struct.dcm"
        assert handler.rtplan_file == "dummy_plan.dcm"
        assert handler.interactive_mode is False

    def test_centroid_calculation(self):
        """Centroid calculation works correctly"""
        from KIM_Centroid_using_Folder_Monitoring import DICOMHandler

        handler = DICOMHandler("dummy1.dcm", "dummy2.dcm")

        # Test with simple points
        points = np.array([
            [0, 0, 0],
            [10, 0, 0],
            [10, 10, 0],
            [0, 10, 0]
        ])

        centroid = handler.calculate_centroid(points)

        # Centroid should be at (5, 5, 0)
        assert centroid[0] == 5.0
        assert centroid[1] == 5.0
        assert centroid[2] == 0.0

    def test_convert_to_cm(self):
        """Coordinate conversion from mm to cm works"""
        from KIM_Centroid_using_Folder_Monitoring import DICOMHandler

        handler = DICOMHandler("dummy1.dcm", "dummy2.dcm")

        # Test conversion
        assert handler.convert_to_cm(100) == 10.0
        assert handler.convert_to_cm(50) == 5.0
        assert handler.convert_to_cm(0) == 0.0
        assert handler.convert_to_cm(-100) == -10.0


class TestEventHandler:
    """Test DICOMEventHandler class"""

    def test_event_handler_init(self):
        """DICOMEventHandler can be instantiated"""
        from KIM_Centroid_using_Folder_Monitoring import DICOMEventHandler

        handler = DICOMEventHandler(enable_interactive=False)

        assert handler is not None
        assert handler.interactive_mode is False
        assert isinstance(handler.files_detected, dict)
        assert len(handler.files_detected) == 0


class TestUtilityFunctions:
    """Test utility functions"""

    def test_prompt_for_interactive_mode_function_exists(self):
        """Interactive mode prompt function exists"""
        from KIM_Centroid_using_Folder_Monitoring import prompt_for_interactive_mode

        assert prompt_for_interactive_mode is not None
        assert callable(prompt_for_interactive_mode)


class TestFileOperations:
    """Test file-related operations"""

    def test_main_script_file_exists(self):
        """Main Python script file exists"""
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "KIM_Centroid_using_Folder_Monitoring.py"
        )
        assert os.path.exists(script_path)

    def test_spec_file_exists(self):
        """PyInstaller spec file exists"""
        spec_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "KIM_Centroid_using_Folder_Monitoring.spec"
        )
        assert os.path.exists(spec_path)

    def test_requirements_file_exists(self):
        """requirements.txt exists"""
        req_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "requirements.txt"
        )
        assert os.path.exists(req_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
