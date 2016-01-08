#!/usr/bin/env python3
"""Script to set up the project.

Usage:
This script is invoked without any command-line arguments, and can be invoked from any directory.
However, the script should be in the top-level directory of the project.
For example, in the terminal:
    $ ./setup.py
"""

import os # File paths
import shutil # File operations

# Parameters
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
EXTERNAL_DIR_NAME = 'ext'
NANPY_CONFIG_FILE_NAME = 'nanpy-firmware-config.h'
NANPY_FIRMWARE_DIR_NAME = 'nanpy-firmware'

def configure_nanpy_firmware():
    """Copies the firmware configuration file into the nanpy-firmware submodule."""
    ext_dir = os.path.join(ROOT_DIR, EXTERNAL_DIR_NAME)
    config_source_path = os.path.join(ext_dir, NANPY_CONFIG_FILE_NAME)
    config_target_path = os.path.join(ext_dir, NANPY_FIRMWARE_DIR_NAME, 'Nanpy', 'cfg.h')
    shutil.copyfile(config_source_path, config_target_path)
    relative_nanpy_dir = os.path.join(EXTERNAL_DIR_NAME, NANPY_FIRMWARE_DIR_NAME, 'Nanpy')
    print("The nanpy-firmware submodule has been configured. Now copy the "
          "{} directory into your Arduino \"sketchbook\" directory, "
          "open the Nanpy sketchbook project in your Arduino IDE, "
          "and upload it to your Arduino.".format(relative_nanpy_dir))

if __name__ == '__main__':
    configure_nanpy_firmware()

