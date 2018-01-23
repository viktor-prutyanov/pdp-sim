#!/usr/bin/python3

from core import Core
from display import Display
import sys
import os
import tkinter as tk
import time

def update_z():
    if (core.regfile.z):
        z_entry['text'] = '1'
    else:
        z_entry['text'] = '0'

def update_regs():
    reg_n = 0
    for reg in core.regfile.regs:
        reg_entries[reg_n]['text'] = "0x{0:04X}".format(reg)
        reg_n = reg_n + 1

    update_z()

def run(event):
    if run_button['state'] == 'disabled':
        return
    core.run()
    update_regs()
    if core.is_halted:
        step_button['state'] = 'disabled'
        run_button['state'] = 'disabled'

def step(event):
    if step_button['state'] == 'disabled':
        return
    last_instr_str = core.step()
    lb.insert(core.step_cnt, last_instr_str)
    update_regs()
    if core.is_halted:
        step_button['state'] = 'disabled'
        run_button['state'] = 'disabled'

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print("usage: {} file.bin".format(sys.argv[0]))
        sys.exit()

    filename = sys.argv[1]

    core = Core(filename, os.path.getsize(filename) // 2)

    top = tk.Tk()

    display = Display(top, core.memory)
    core.memory.fill_vram_with_line()
    core.memory.set_display_handler(display.display_vram)

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
        reg_labels[reg_n].pack(side='bottom')
        reg_entries.append(tk.Label(top, bg='white'))
        reg_entries[reg_n].pack(side='bottom')
        reg_n = reg_n + 1
        
    z_label = tk.Label(top, text="Z")
    z_label.pack(side='bottom')
    z_entry = tk.Label(top, bg='white')
    z_entry.pack(side='bottom')

    update_regs()

    lb = tk.Listbox(top, height=50)
    lb.pack(side='right')

    top.mainloop()
