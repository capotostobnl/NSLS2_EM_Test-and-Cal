# #flake8: noqa E501
# pylint: disable=broad-except
# *****************************************************************************
"""This module produces generic, reusable class for generation and management
of project directory structures.

M. Capotosto
8/29/2025
NSLS-II Diagnostics and Instrumentation"""

# *****************************************************************************
# ******IMPORTS******
import os
from datetime import datetime

# *****************************************************************************

# *****************************************************************************
# ******CONSTANTS******

# *****************************************************************************


# *************************************************************************
# ******Initialize Date/Time Names for Test Instance******
# ******Create directory structures for Test Data Storage******

class ProjectDirectoryManager:
    """Manages the directory and file path creation"""
    def __init__(self, project_name, root_directory="Test_Data"):
        """Initializes project name, directory"""
        self.project_name = project_name
        self.root_directory = root_directory
        self._dir_time_formatted = None

    def _get_current_datetime(self):
        """Helper method to get formatted date/time"""
        dir_create_time = datetime.now()
        self._dir_time_formatted = \
            dir_create_time.strftime("%m-%d-%y_%H-%M-%S")
        report_date_formatted = dir_create_time.strftime("%m/%d/%y")
        report_time_formatted = dir_create_time.strftime("%I:%M %p")

        return report_date_formatted, report_time_formatted

    def generate_paths(self, serial_number):
        """
        Generates and returns the full paths for the report and raw data dirs.
        """
        report_date_formatted, report_time_formatted = \
            self._get_current_datetime()

        # Construct the paths using instance variables
        test_instance_dir = os.path.join(
            self.root_directory,
            f"{self.project_name}{serial_number}-{self._dir_time_formatted}"
        )
        report_path = os.path.join(test_instance_dir, f"{self.project_name}"
                                   f"{serial_number}_Report.pdf")
        raw_data_path = os.path.join(test_instance_dir, "raw_data")

        return report_path, raw_data_path, report_date_formatted, \
            report_time_formatted

    def create_directories(self, serial_number):
        """Creates the directories for the test instance."""
        report_path, raw_data_path, _, _ = self.generate_paths(serial_number)

        try:
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            os.makedirs(raw_data_path, exist_ok=True)
            print(f"Directories created for {self.project_name}-"
                  f"{serial_number}.")
            print(f"Report path: {report_path}")
            print(f"Raw data path: {raw_data_path}")
            return report_path, raw_data_path
        except Exception as e:
            print(f"An error occurred while creating directories: {e}")
            return None, None

# *************************************************************************
