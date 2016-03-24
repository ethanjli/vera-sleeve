# vera-sleeve
The Venous Return Assist Leg Sleeve (VERA Sleeve) is a wearable device for management of the chronic leg problems that patients with post-thrombotic syndrome experience following a deep venous thrombosis. This device is being developed as a project for the two-quarter-long course series BIOE 141A: *Senior Capstone Biodesign* at Stanford University in the 2015-2016 academic year.

## Contents
This repository contains unit testing code for various subsystems of the test fixtures we will use in developing the device. This repository will also contain code to control the device. Here are the subdirectories:
* The `doc/` subdirectory will contain project documentation.
* The `ext/` subdirectory contains external code to support the device.
* The `verasleeve/` subdirectory contains program modules.
  * The `tests` subdirectory contains test programs.
    * The `arduino` subdirectory contains firmware tests, i.e. tests to be uploaded to the Arduino board.

## Contributors
* Ethan Li
* Alaina Shumate
* Preston Lim

## Dependencies
Some unit tests are designed for execution with the Arduino IDE and its Serial Monitor and Serial Plotter utilities. All other code is written for Python 3.x, with the following libraries:
* [Numpy](http://www.numpy.org/) for signal processing.
* [Nanpy](https://nanpy.github.io/) for serial communication with the Arduino.
* [Pykka](https://www.pykka.org/) for concurrency based on the Actor model.
* [PyQt4](https://riverbankcomputing.com/software/pyqt/intro) for graphical interfaces.
* [PyQtGraph](http://www.pyqtgraph.org/) for plotting in graphical interfaces.

## Setup
Install the required libraries using your preferred method. Then clone this repository, using the `--recursive` flag so that submodules are also cloned:
```sh
git clone --recursive git@github.com:lietk12/vera-sleeve.git
```

Then run the `setup.py` script and follow the instructions printed by that script to upload the Nanpy firmware to your Arduino.

## Running
### Tests
Tests in the `verasleeve/tests/arduino` subdirectory should be opened from the Arduino IDE and uploaded. Tests in the `verasleeve/tests` subdirectory must be run from the root directory of the package (i.e. the directory containing this README file), and can be run as follows:
```sh
python -m verasleeve.tests.name_of_test_to_run
```
For example, to run the `blink` test:
```sh
python -m verasleeve.tests.blink
```
Note that you may need to replace `python` with the executable name of python 3 on your distribution. On Arch Linux, this is just `python`, but on other distributions, this may be something like `python3`.

### Leg Model Test Fixture Monitor
The panel to monitor sensor data from the leg model should be run from the root directory of the package, and can be run as follows:
```sh
python -m verasleeve.leg_monitor
```
This will open a window. You should press the connect button to connect to the Arduino on the test fixture. If the connection is successful, the program will immediately begin streaming sensor data onto the display plots and labels. You can pause (and reset) and resume data streaming with the corresponding toolbar buttons. You can also save a screenshot of the window with the corresponding toolbar button, though you may prefer to save an individual plot by right-clicking on it to access the PyQtGraph-provied contextual menu. Finally, you can toggle whether to show only the noise-filtered sensor signals or also to show the raw signal and the min/max signals (which correspond to the min and max values displayed in text labels).

### Sleeve Control Panel
The panel to drive contractions of the VERA sleeve should be run from the root directory of the package, and can be run as follows:
```sh
python -m verasleeve.sleeve_panel
```
This will open a window. You should press the connect button to connect to the Arduino on the VERA sleeve. If the connection is successful, the program will immediately begin driving contraction patterns on the VERA sleeve. You can adjust parameters, and you can also pause and unpause the contraction pattern. Note that, if you also want to run the leg model test fixture monitor, you may need to run that program and connect to the test fixture's Arduino before running the sleeve control panel program and connecting to the VERA sleeve's Arduino.
