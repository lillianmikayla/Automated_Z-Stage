# Automated_Z-Stage
Capstone project, automated z stage for powder based 3D printing.

Desc:  
GUI.exe - Full GUI to be run as an executable, has all dependencies included.  
GUI.py - Python code for the GUI  
Hardware.c - Arduino firmware written in C. Already loaded onto microcontroller. Contains pin mappings between motor driver and microcontroller in comments.   
NEMA23_Full_Datasheet.pdf - Data sheet for NEMA23 closed loop stepper motor.   
CL57T.pdf - Datasheet for closed loop motor driver.  
Wiring Diagram for Closed Loop Stepper Motor.pdf - Wiring diagram for motor to motor driver and power supply.  

How to run:  
Download GUI.exe and move onto desktop, connect to microcontroller via USB Serial. Ensure power supply is on.  

Note: If alarms are detected on GUI, refer to CL57T.pdf data sheet for more information on the malfunction.  
