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
* [Matplotlib](https://matplotlib.org) for some tests. If you're not running any tests, you don't need it.

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
