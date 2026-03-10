import serial
import time

PORT = "/dev/cu.usbmodem31101"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)

time.sleep(2)  # Arduino resets when serial opens

print("Connected to Arduino")

while True:
    cmd = input("Enter G-code: ")

    if cmd.lower() == "exit":
        break

    ser.write((cmd + "\n").encode())

    # read Arduino response
    time.sleep(0.1)
    while ser.in_waiting:
        response = ser.readline().decode(errors="ignore").strip()
        print(response)

ser.close()
