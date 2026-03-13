import serial
import time

PORT = "/dev/cu.usbmodem31101"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

print("Connected")

while True:
    cmd = input("Move (mm): ").strip()

    if cmd.lower() == "exit":
        break

    ser.write((cmd + "\n").encode())
    time.sleep(.5)

    while ser.in_waiting:
        print(ser.readline().decode(errors="ignore").strip())

ser.close()
