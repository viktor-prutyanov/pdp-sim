#!/usr/bin/python3

from core import Core
from math import sin
import sys
import os
import tkinter as tk

def update_regs():
    reg_n = 0
    for reg in core.regfile.regs:
        reg_entries[reg_n]['text'] = "0x{0:04X}".format(reg)
        reg_n = reg_n + 1

def run(event):
    core.run()
    update_regs()
    if core.is_halted:
        step_button['state'] = 'disabled'
        run_button['state'] = 'disabled'

def step(event):
    core.step()
    update_regs()
    if core.is_halted:
        step_button['state'] = 'disabled'
        run_button['state'] = 'disabled'


class Display:
    WIDTH  = 256
    HEIGHT = 256

    def __init__(self, top):
        # @brief draw bitmap image
        WIDTH, HEIGHT = 256, 256

        canvas = tk.Canvas(top, width=WIDTH, height=HEIGHT, bg="#000000")
        canvas.pack()
        img = tk.PhotoImage(width=WIDTH, height=HEIGHT)
        canvas.create_image((WIDTH/2, HEIGHT/2), image=img, state="normal")

        for x in range(4 * WIDTH):
            y = int(HEIGHT/2 + HEIGHT/4 * sin(x/80.0))
            img.put("#ffffff", (x//4,y))

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print("usage: {} file.bin".format(sys.argv[0]))
        sys.exit()

    filename = sys.argv[1]

    core = Core(filename, os.path.getsize(filename) // 2)

    top = tk.Tk()

    display = Display(top)

    step_button = tk.Button(top, text="Step")
    step_button.bind("<Button-1>", step)
    step_button.pack()

    run_button = tk.Button(top, text="Run")
    run_button.bind("<Button-1>", run)
    run_button.pack()

    reg_labels = []
    reg_entries = []
    reg_n = 0
    for reg in core.regfile.regs:
        reg_labels.append(tk.Label(top, text="R{}".format(reg_n)))
        reg_labels[reg_n].pack()
        reg_entries.append(tk.Label(top, bg='white'))
        reg_entries[reg_n].pack()
        reg_n = reg_n + 1

    update_regs()

    top.mainloop()