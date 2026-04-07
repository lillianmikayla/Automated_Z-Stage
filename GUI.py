import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import time

root = tk.Tk()
root.title("3d Powder Bed Printer Configuration")
root.geometry('600x420+50+50')

# serial settings: replace with hardware settings later
SERIAL_PORT = None 
BAUD_RATE = 115200
READ_INTERVAL_MS = 50  # how often to check for new serial data

# gui display var

moveVar = tk.StringVar(value="")
posVar = tk.StringVar(value="0.000 mm")
lowerAmountVar = tk.StringVar(value="0.01")
raiseAmountVar = tk.StringVar(value="0.01")

homedVar = tk.StringVar(value="Homed status")
faultVar = tk.StringVar(value="None")
connVar = tk.StringVar(value="Disconnected")
portVar = tk.StringVar()



# controller state 

ser = None
connected = False
homed = False
busy = False
fault = "None"
z_pos_mm = 0.0

# read serial 

def read_serial():
    global ser

    if ser is not None:
        try:
            while ser.in_waiting:
                line = ser.readline().decode(errors="ignore").strip()
                if line:
                    handle_serial_line(line)
        except Exception as e:
            print("Serial read error:", e)

    root.after(READ_INTERVAL_MS, read_serial)

# ui update function

def update_ui():
    connVar.set("Connected" if connected else "Disconnected")
    homedVar.set("True" if homed else "False")
    faultVar.set(fault)
    posVar.set(f"{z_pos_mm:.3f} mm")



# handle lines recieved from serial data

def handle_serial_line(line):
    global homed, fault, z_pos_mm, busy

    print("RX:", line)

    # temporary: if firmware just echoes back command received
    if line.startswith("COMMAND_RECEIVED:"):
        moveVar.set(line)
        return

    if line == "ok":
        moveVar.set("ok")

    elif line.startswith("Z:"):
        try:
            z_pos_mm = float(line.split(":", 1)[1])
            update_ui()
        except ValueError:
            moveVar.set("bad z msg")

    elif line == "HOMED":
        homed = True
        fault = "None"
        update_ui()
        moveVar.set("homed")

    elif line.startswith("ERROR:"):
        fault = line.split(":", 1)[1]
        busy = False
        update_ui()
        moveVar.set("fault")

    elif line == "BUSY":
        busy = True
        moveVar.set("moving...")

    elif line == "IDLE":
        busy = False
        moveVar.set("idle")

    else:
        # for now, show any unrecognized text in the movement box
        moveVar.set(line)

# sending command

def send_cmd(cmd):
    global ser

    if ser is None:
        moveVar.set("not connected")
        return

    try:
        print("TX:", cmd)
        ser.write((cmd + "\n").encode())
    except Exception as e:
        print("Serial write error:", e)
        moveVar.set("send failed")



def refresh_ports():
    ports = serial.tools.list_ports.comports()
    port_list = [f"{p.device} - {p.description}" for p in ports]

    portDropdown["values"] = port_list

    if port_list:
        portDropdown.current(0)
    else:
        portVar.set("")      



#gui button handlers (don't replace?)
def on_connect_toggle():
    global ser, connected, homed, busy, fault, z_pos_mm

    if ser is None:
        try:
            selection = portVar.get()
            if not selection:
                moveVar.set("no port selected")
                return
            port = selection.split(" - ")[0]

            ser = serial.Serial(port, BAUD_RATE, timeout=0.1)
            print("Connected to", port)

            time.sleep(0.5)  #many Arduino-style boards reset on connect
            connected = True
            moveVar.set("connected")
            print("Connected to", port)
        except Exception as e:
            print("Connect error:", e)
            moveVar.set("connect failed")
            ser = None
            connected = False
    else:
        try:
            ser.close()
        except:
            pass

        ser = None
        connected = False
        homed = False
        busy = False
        fault = "None"
        z_pos_mm = 0.0
        moveVar.set("disconnected")

    update_ui()

def on_home():
    send_cmd("G28")  

def on_lower():
    try:
        amt = float(lowerAmountVar.get())
    except:
        moveVar.set("invalid amount")
        return

    send_cmd(f"{amt:.3f}") 

def on_raise():
    try:
        amt = float(raiseAmountVar.get())
    except:
        moveVar.set("invalid amount")
        return

    send_cmd(f"{-amt:.3f}")

def on_report():
    send_cmd("M114")  

def on_stop():
    send_cmd("M112") 


#UI LAYOUT

btnConnect = ttk.Button(root, text="Connect/Disconnect", command=on_connect_toggle)
btnHome = ttk.Button(root, text="Home", command=on_home)
btnLower = ttk.Button(root, text="Lower Z-stage", command=on_lower)
btnReport = ttk.Button(root, text="Report Position", command=on_report)
btnStop = ttk.Button(root, text="STOP", command=on_stop)
btnRaise = ttk.Button(root, text="Raise Z-stage", command=on_raise)

btnConnect.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
btnHome.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
btnLower.grid(row=3, column=1, sticky="nsew", padx=8, pady=8)
btnRaise.grid(row=3, column=0, sticky="nsew", padx=8, pady=8)

#drop down menu

tk.Label(root, text="Serial Port:").grid(row=0, column=0, padx=8, pady=4)

portDropdown = ttk.Combobox(root, textvariable=portVar, state="readonly")
portDropdown.grid(row=0, column=1, padx=8, pady=4, sticky="ew")

btnRefreshPorts = ttk.Button(root, text="Refresh Ports", command=refresh_ports)
btnRefreshPorts.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=4)


tk.Label(root, text="Raise amount (mm):").grid(row=5, column=0, columnspan=2)
ttk.Entry(root, textvariable=raiseAmountVar).grid(row=6, column=0, columnspan=2, sticky="ew", padx=8, pady=(0,8))

tk.Label(root, text="Lower amount (mm):").grid(row=7, column=0, columnspan=2)
ttk.Entry(root, textvariable=lowerAmountVar).grid(row=8, column=0, columnspan=2, sticky="ew", padx=8, pady=(0,8))

#status indicator stuff below the functions



statusFrame = ttk.LabelFrame(root, text="System Status")
statusFrame.grid(row=9, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

#connection status
tk.Label(statusFrame, text="Connection:").grid(row=0, column=0, sticky="w", padx=4, pady=2)
tk.Label(statusFrame, textvariable=connVar).grid(row=0, column=1, sticky="w", padx=4, pady=2)

#homed status
tk.Label(statusFrame, text="Homed:").grid(row=1, column=0, sticky="w", padx=4, pady=2)
tk.Label(statusFrame, textvariable=homedVar).grid(row=1, column=1, sticky="w", padx=4, pady=2)

#current position
tk.Label(statusFrame, text="Z Position:").grid(row=2, column=0, sticky="w", padx=4, pady=2)
tk.Label(statusFrame, textvariable=posVar).grid(row=2, column=1, sticky="w", padx=4, pady=2)

#fault state
tk.Label(statusFrame, text="Fault:").grid(row=3, column=0, sticky="w", padx=4, pady=2)
tk.Label(statusFrame, textvariable=faultVar).grid(row=3, column=1, sticky="w", padx=4, pady=2)

#motion / command feedback
tk.Label(statusFrame, text="Status:").grid(row=4, column=0, sticky="w", padx=4, pady=2)
tk.Label(statusFrame, textvariable=moveVar).grid(row=4, column=1, sticky="w", padx=4, pady=2)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)


update_ui()
root.after(READ_INTERVAL_MS, read_serial)
refresh_ports()
root.mainloop()
