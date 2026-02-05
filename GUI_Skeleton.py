import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("3d Powder Bed Printer Configuration")
root.geometry('600x400+50+50')

def lowerZStage():
    moveVar.set("success")
    posVar.set('5mm')

def resetZStage():
    moveVar.set("")
    posVar.set("")

button1 = ttk.Button(root, text="Lower Z-stage", command=lowerZStage)
button2 = ttk.Button(root, text="Reset Z-stage", command=resetZStage)

#Labels above each output entry
mvmtLabel = tk.Label(root, text="Movement was a")
posLabel = tk.Label(root, text="Current Z-position:")

moveVar = tk.StringVar(value="")
posVar = tk.StringVar(value="")

mvmtBox = ttk.Entry(root, textvariable=moveVar, state='readonly', justify='center', width=20)
posBox = ttk.Entry(root, textvariable=posVar, state='readonly', justify='center', width=20)

#Layout
button1.grid(row=0, column=0, sticky='nsew', padx=8, pady=8)
button2.grid(row=0, column=1, sticky='nsew', padx=8, pady=8)
mvmtLabel.grid(row=1, column=0, sticky='s', padx=6, pady=(4,0))
posLabel.grid(row=1, column=1, sticky='s', padx=6, pady=(4,0))
mvmtBox.grid(row=2, column=0, sticky='n', padx=6, pady=(0,8))
posBox.grid(row=2, column=1, sticky='n', padx=6, pady=(0,8))

#Configure grid weights
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()