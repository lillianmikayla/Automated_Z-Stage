import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("3d Powder Bed Printer Configuration")
root.geometry('600x420+50+50')

# gui display var

moveVar = tk.StringVar(value="")
posVar = tk.StringVar(value="0.000 mm")
lowerAmountVar = tk.StringVar(value="0.01")

homedVar = tk.StringVar(value="No")
faultVar = tk.StringVar(value="None")
connVar = tk.StringVar(value="Disconnected")

# fake firmware sate (repalce with real controller state?)

connected = False        # replace: True when serial port opens
homed = False            # replace: Set when firmware confirms homing
busy = False             # replace: Based on firmware motion status
fault = "None"           # replace: From firmware ERROR messages
z_pos_mm = 0.0           # replace: Updated only from firmware Z: reports

Z_MIN = -200.0           # replace: real travel limits from hardware
Z_MAX = 0.0

# ui update function

def update_ui():
    connVar.set("Connected" if connected else "Disconnected")
    homedVar.set("Yes" if homed else "No")
    faultVar.set(fault)
    posVar.set(f"{z_pos_mm:.3f} mm")

# simulates recieving serial data

def fake_rx(line):
    """
    REPLACE THIS ENTIRE FUNCTION with:
        def handle_serial_line(line):
            parse real firmware responses here
    """

    global homed, fault, z_pos_mm, busy

    if line == "ok":
        moveVar.set("ok")

    elif line.startswith("Z:"):
        # REPLACE: this will parse real serial line from firmware
        try:
            z_pos_mm = float(line.split(":", 1)[1])
        except:
            return
        update_ui()

    elif line == "HOMED":
        # REPLACE: firmware will send something indicating homing success
        homed = True
        update_ui()

    elif line.startswith("ERROR:"):
        # REPLACE: firmware error parsing
        fault = line.split(":", 1)[1]
        busy = False
        update_ui()
        moveVar.set("fault")

    elif line == "BUSY":
        busy = True
        moveVar.set("moving...")

    elif line == "IDLE":
        busy = False

# sending command

def fake_send(cmd):
    """
    REPLACE THIS FUNCTION with:

        def send_cmd(cmd):
            ser.write((cmd + "\\n").encode())

    """

    # remove this call and let firmware respond via serial later
    fake_firmware_handle(cmd)


#this simulates the firmware stuff
# DELETE THIS ENTIRE SECTION WHEN HARDWARE IS READ

def fake_firmware_handle(cmd):
    global connected, homed, busy, fault, z_pos_mm

    if not connected:
        fake_rx("ERROR:NOT_CONNECTED")
        return

    if busy and cmd != "M112":
        fake_rx("ERROR:BUSY")
        return

    cmd = cmd.strip()

    #home command
    if cmd == "G28":
        busy = True
        fake_rx("BUSY")

        def finish_home():
            global busy, homed, fault, z_pos_mm
            busy = False
            fault = "None"
            homed = True
            z_pos_mm = 0.0
            fake_rx("ok")
            fake_rx("Z:0.000")
            fake_rx("HOMED")
            fake_rx("IDLE")

        #replace and firmware will perform homing
        root.after(400, finish_home)
        return

    #position 
    if cmd == "M114":
        fake_rx(f"Z:{z_pos_mm:.3f}")
        return

    #stop
    if cmd == "M112":
        busy = False
        fault = "ESTOP"
        fake_rx("ok")
        fake_rx("ERROR:ESTOP")
        return

    #move command
    if cmd.startswith("G0"):
        if fault != "None":
            fake_rx("ERROR:FAULT_ACTIVE")
            return
        if not homed:
            fake_rx("ERROR:NOT_HOMED")
            return

        parts = cmd.split()
        z_part = None
        for p in parts:
            if p.startswith("Z"):
                z_part = p
                break

        if z_part is None:
            fake_rx("ERROR:BAD_CMD")
            return

        try:
            dz = float(z_part[1:])
        except:
            fake_rx("ERROR:BAD_Z")
            return

        new_z = z_pos_mm + dz

        if new_z < Z_MIN:
            fault = "LIMIT_LOW"
            fake_rx("ERROR:LIMIT_LOW")
            return

        if new_z > Z_MAX:
            fault = "LIMIT_HIGH"
            fake_rx("ERROR:LIMIT_HIGH")
            return

        busy = True
        fake_rx("BUSY")

        def finish_move():
            global busy, z_pos_mm
            z_pos_mm = new_z
            fake_rx("ok")
            fake_rx(f"Z:{z_pos_mm:.3f}")
            fake_rx("IDLE")

        # replace and firmware will move motor and send real updates
        root.after(300, finish_move)
        return

    fake_rx("ERROR:UNKNOWN_CMD")


#gui button handlers (don't replace?)
def on_connect_toggle():
    global connected, homed, busy, fault, z_pos_mm

    #replace with open/close serial port here
    connected = not connected

    if not connected:
        homed = False
        busy = False
        fault = "None"
        z_pos_mm = 0.0

    update_ui()

def on_home():
    fake_send("G28")  #replace with send_cmd("G28")

def on_lower():
    try:
        amt = float(lowerAmountVar.get())
    except:
        moveVar.set("invalid amount")
        return

    if amt <= 0:
        moveVar.set("amount must be > 0")
        return

    fake_send(f"G0 Z{-amt:.3f}")  #replace with send_cmd(...)

def on_report():
    fake_send("M114")  #replace with send_cmd("M114")

def on_stop():
    fake_send("M112")  # replace with send_cmd("M112")


# UI LAYOUT
btnConnect = ttk.Button(root, text="Connect/Disconnect", command=on_connect_toggle)
btnHome = ttk.Button(root, text="Home", command=on_home)
btnLower = ttk.Button(root, text="Lower Z-stage", command=on_lower)
btnReport = ttk.Button(root, text="Report Position", command=on_report)
btnStop = ttk.Button(root, text="STOP", command=on_stop)

btnConnect.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
btnHome.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
btnLower.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)

tk.Label(root, text="Lower amount (mm):").grid(row=2, column=0, columnspan=2)
ttk.Entry(root, textvariable=lowerAmountVar).grid(row=3, column=0, columnspan=2, sticky="ew", padx=8, pady=(0,8))

btnReport.grid(row=4, column=0, sticky="nsew", padx=8, pady=8)
btnStop.grid(row=4, column=1, sticky="nsew", padx=8, pady=8)

tk.Label(root, textvariable=connVar).grid(row=5, column=0)
tk.Label(root, textvariable=homedVar).grid(row=5, column=1)

ttk.Entry(root, textvariable=posVar, state="readonly").grid(row=6, column=0, sticky="ew", padx=8)
ttk.Entry(root, textvariable=faultVar, state="readonly").grid(row=6, column=1, sticky="ew", padx=8)
ttk.Entry(root, textvariable=moveVar, state="readonly").grid(row=7, column=0, columnspan=2, sticky="ew", padx=8, pady=(0,8))

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

update_ui()
root.mainloop()
