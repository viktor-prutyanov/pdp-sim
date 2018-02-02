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

def update_clock():
    clock = core.clock * int(ex_m_entry.get()) + core.memory.clock * int(mem_m_entry.get())
    if core.memory.cache is not None:
        clock += core.memory.cache.clock * int(cache_m_entry.get())
    clock_entry['text'] = "{}".format(clock)

def update_counters():
    if core.memory.cache is not None:
        cache_hit_entry['text'] = "{:4.2f}%".format(core.memory.cache.get_hit_rate() * 100)

def update():
    last_instr_str = core.step()
    trace_lb.insert(core.step_cnt, last_instr_str)
    update_regs()
    update_clock()
    update_counters()

def run(event):
    if run_button['state'] == 'disabled':
        return
    while not core.is_halted:
        update()
        
    step_button['state'] = 'disabled'
    run_button['state'] = 'disabled'

def step(event):
    if step_button['state'] == 'disabled':
        return
    update()

    if core.is_halted:
        step_button['state'] = 'disabled'
        run_button['state'] = 'disabled'

def select_cache_type():
    if cache_type.get() == "fa":
        cache_size_entry['state'] = 'normal'
        cache_hit_entry['state'] = 'normal'
        core.memory.set_cache_type(1, int(cache_size_entry.get()))
    elif cache_type.get() == "dm":
        cache_size_entry['state'] = 'normal'
        cache_hit_entry['state'] = 'normal'
        core.memory.set_cache_type(2, int(cache_size_entry.get()))
    else:
        cache_size_entry['state'] = 'disabled'
        cache_hit_entry['state'] = 'disabled'
        core.memory.set_cache_type(0, 0)

def reset(event):
    core.reset()
    update_regs()
    update_clock()
    core.memory.load_font(core.memory.RAM)
    display.display_vram(0)
    trace_lb.delete(0, tk.END)
    select_cache_type()

    step_button['state'] = 'normal'
    run_button['state'] = 'normal'

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print("usage: {} file.bin".format(sys.argv[0]))
        sys.exit()

    filename = sys.argv[1]

    core = Core(filename, os.path.getsize(filename) // 2)

    top = tk.Tk()
    
    cache_type = tk.StringVar()
    cache_type.set("no")
    
    #
    #   Frame with all buttons and counters
    #
    left_frame = tk.Frame(top, bg='#4682b4', bd=5)

    buttons_frame = tk.Frame(left_frame, bd=6)
    step_button = tk.Button(buttons_frame, text="Step", width=15)
    step_button.bind("<Button-1>", step)
    step_button.pack()

    run_button = tk.Button(buttons_frame, text="Run", width=15)
    run_button.bind("<Button-1>", run)
    run_button.pack()
    
    reset_button = tk.Button(buttons_frame, text="Reset", width=15)
    reset_button.bind("<Button-1>", reset)
    reset_button.pack()
    buttons_frame.pack(side='top')

    reg_labels = []
    reg_entries = []
    reg_frames = []
    reg_n = 0
    for reg in core.regfile.regs:
        reg_frames.append(tk.Frame(left_frame, bg='#ee3b3b', bd=4))
        reg_labels.append(tk.Label(reg_frames[reg_n], text="R{}".format(reg_n), width=8))
        reg_labels[reg_n].pack(side='left')
        reg_entries.append(tk.Label(reg_frames[reg_n], bg='white', width=10))
        reg_entries[reg_n].pack(side='right')
        reg_frames[reg_n].pack()
        reg_n = reg_n + 1
    
    z_frame = tk.Frame(left_frame, bg='#ee3b3b', bd=4)
    z_label = tk.Label(z_frame, text="Z", width=8)
    z_label.pack(side='left')
    z_entry = tk.Label(z_frame, bg='white', width=10)
    z_entry.pack(side='right')
    z_frame.pack()

    clock_frame = tk.Frame(left_frame, bg='#ee3b3b', bd=4)
    clock_label = tk.Label(clock_frame, text="CLOCK", width=8)
    clock_label.pack(side='left')
    clock_entry = tk.Label(clock_frame, bg='white', width=10)
    clock_entry.pack(side='right')
    clock_frame.pack()

    cache_frame = tk.Frame(left_frame, bd=4)
    no_cache_rb = tk.Radiobutton(cache_frame, text="No cache",
        variable=cache_type, value="no", command=select_cache_type)
    no_cache_rb.pack(anchor=tk.W)
    fa_cache_rb = tk.Radiobutton(cache_frame, text="Fully associative",
        variable=cache_type, value="fa", command=select_cache_type)
    fa_cache_rb.pack(anchor=tk.W)
    dm_cache_rb = tk.Radiobutton(cache_frame, text="Direct mapped",
        variable=cache_type, value="dm", command=select_cache_type)
    dm_cache_rb.pack(anchor=tk.W)
    cache_size_frame = tk.Frame(cache_frame)
    cache_size_label = tk.Label(cache_size_frame, text="Length", width=8)
    cache_size_label.pack(side='left')
    cache_size_entry = tk.Entry(cache_size_frame, bd=0, bg='white', width=10)
    cache_size_entry.insert(0, "64")
    cache_size_entry.bind('<Return>', (lambda _: select_cache_type()))
    cache_size_entry.pack(side='right')
    cache_size_frame.pack()
    cache_hit_frame = tk.Frame(cache_frame)
    cache_hit_label = tk.Label(cache_hit_frame, text="Hit rate", width=8)
    cache_hit_label.pack(side='left')
    cache_hit_entry = tk.Label(cache_hit_frame, bd=0, bg='white', width=10)
    cache_hit_entry.pack(side='right')
    cache_hit_frame.pack()
    cache_frame.pack(side='bottom')
    
    ex_m_frame = tk.Frame(left_frame)
    ex_m_label = tk.Label(ex_m_frame, text="Core latency", width=15)
    ex_m_label.pack(side='left')
    ex_m_entry = tk.Entry(ex_m_frame, bd=0, bg='white', width=4)
    ex_m_entry.insert(0, "2")
    ex_m_entry.pack(side='right')
    ex_m_frame.pack()
    
    cache_m_frame = tk.Frame(left_frame)
    cache_m_label = tk.Label(cache_m_frame, text="Cache latency", width=15)
    cache_m_label.pack(side='left')
    cache_m_entry = tk.Entry(cache_m_frame, bd=0, bg='white', width=4)
    cache_m_entry.insert(0, "1")
    cache_m_entry.pack(side='right')
    cache_m_frame.pack()
    
    mem_m_frame = tk.Frame(left_frame)
    mem_m_label = tk.Label(mem_m_frame, text="Memory latency", width=15)
    mem_m_label.pack(side='left')
    mem_m_entry = tk.Entry(mem_m_frame, bd=0, bg='white', width=4)
    mem_m_entry.insert(0, "10")
    mem_m_entry.pack(side='right')
    mem_m_frame.pack()
    
    left_frame.pack(side='left', fill=tk.Y)
   
    #
    #   Frame with display and trace window
    #
    right_frame = tk.Frame(top, bg='#4682b4', bd=4)
    
    display = Display(right_frame, core.memory)
    core.memory.load_font(core.memory.RAM)
    core.memory.set_display_handler(display.display_vram)

    trace_frame = tk.Frame(right_frame)
    trace_label = tk.Label(trace_frame, text="Instruction trace", width=25)
    trace_label.pack(side='top')
    trace_lb = tk.Listbox(trace_frame, height=33, bg='white', width=25)
    trace_lb.pack(side='bottom')
    trace_frame.pack(side='right')
    
    right_frame.pack(side='right')
    
    update_regs()
    update_clock()
    select_cache_type()
    
    top.mainloop()
