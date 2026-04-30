# Automated Z-Stage

Capstone Project – Automated Z-axis stage for powder-based 3D printing

---

## Overview

This project implements an automated Z-axis stage controlled through a graphical user interface (GUI). The system integrates a closed-loop stepper motor, motor driver, and microcontroller to achieve precise vertical motion for powder-based 3D printing applications.

---

## Project Structure

* **GUI.exe**
  Standalone GUI application (all dependencies included)
* **GUI.py**
  Python source code for the GUI
* **Hardware.c**
  Microcontroller firmware (Arduino Mega 2560)
  Contains motor control logic and pin mappings
* **NEMA23_Full_Datasheet.pdf**
  Datasheet for the closed-loop stepper motor
* **CL57T.pdf**
  Datasheet for the motor driver
* **Wiring Diagram for Closed Loop Stepper Motor.pdf**
  Complete wiring diagram for system connections
* **Motor&Encoder_Wiring.png**
  Datasheet for wiring color

---

## System Requirements

* Windows OS (for GUI.exe)
* USB port for microcontroller connection
* External power supply for motor driver
* Arduino Mega 2560 

---

## Hardware Setup

1. Connect the NEMA23 stepper motor to the CL57T motor driver
2. Connect the motor driver to the external power supply
3. Connect the driver to the Arduino (see pin mapping below)
4. Connect the Arduino to your computer via USB
5. Verify all wiring using the provided wiring diagram PDF
6. Ensure all grounds are shared between components

---

## Pin Mapping (Arduino Mega 2560 ↔ CL57T Driver)

### Control Signals

| Arduino Pin | Driver Signal     | Description       |
| ----------- | ----------------- | ----------------- |
| Pin 9       | PULS+             | Step pulse input  |
| Pin 8       | DIR+              | Direction control |
| Pin 7       | ENA+              | Enable signal     |
| GND         | PULS−, DIR−, ENA− | Common ground     |

### Alarm Signal

| Arduino Pin | Driver Signal | Description              |
| ----------- | ------------- | ------------------------ |
| Pin 5       | ALM+          | Alarm signal from driver |
| GND         | ALM−          | Common ground            |

### Encoder Feedback (Y-Split from Motor)

| Arduino Pin | Signal      | Description             |
| ----------- | ----------- | ----------------------- |
| Pin 3       | A+          | Encoder channel A       |
| Pin 2       | B+          | Encoder channel B       |
| GND         | Encoder GND | Shared ground reference |

**Notes:**

* Encoder signals are split (Y-connection) between the motor driver and Arduino.
* Encoder A− and B− remain connected only to the motor driver.
* **Encoder ground MUST be shared between the motor driver and Arduino** to ensure proper signal reference.
* All system grounds (power supply, driver, Arduino, encoder).
* Refer to *Wiring Diagram for Closed Loop Stepper Motor.pdf* for full connection details.

---

## Software Setup

### Run Executable 

1. Download **GUI.exe**
2. Place it on your desktop or desired location
3. Double-click to launch

## How to Run the System

1. Turn on the motor driver power supply
2. Connect the Arduino to your computer via USB
3. Launch the GUI
4. Select the correct serial (COM) port
5. Enable the motor (if required)
6. Use GUI controls to move the Z-stage

---

## GUI Features

* Manual Z-axis movement control
* Serial communication with microcontroller
* Real-time system interaction
* Alarm/error display from motor driver

---

## Notes

* Ensure the motor driver power supply is turned ON before running the system.
* Verify the correct serial (COM) port is selected in the GUI.
* All grounds (Arduino, driver, encoder, and power supply) must be shared.
* If the motor does not move, check wiring connections and enable signal.
* The hardware firmware (**Hardware.c**) may need to be reloaded onto the Arduino Mega 2560 before operation.
* If alarms are detected in the GUI, refer to **CL57T.pdf** for detailed error codes and troubleshooting information.
  
---
