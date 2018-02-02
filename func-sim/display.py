from memory import Memory
from math import sin, cos
import tkinter as tk
import random

class Display:
    WIDTH  = 512
    HEIGHT = 512

    SYM_HEIGHT = 8
    SYM_WIDTH = 8

    def __init__(self, top, memory):
        self.memory = memory

        # @brief draw bitmap image
        self.canvas = tk.Canvas(top, width=Display.WIDTH, height=Display.HEIGHT, bg='black')
        self.canvas.pack(side='left')
        self.img = tk.PhotoImage(width=Display.WIDTH, height=Display.HEIGHT)
        self.canvas.create_image(0, 0, image = self.img, anchor=tk.NW)

    def display_vram(self, offset):
        colors = []
        for word in self.memory.get_vram_range():
            for bit in self.get_bitmap(word):
                if not bit:
                    colors.append("#000000")
                else:
                    colors.append("#ffffff")

        pos = 0
        full_offset = offset * Display.WIDTH * Display.SYM_HEIGHT
        for height_block in range(0, Display.HEIGHT // Display.SYM_HEIGHT - offset):
            for width_block in range(0, Display.WIDTH // Display.SYM_WIDTH):
                for row in range(height_block * Display.SYM_HEIGHT, (height_block + 1) * Display.SYM_HEIGHT):
                    for col in range(width_block * Display.SYM_WIDTH, (width_block + 1) * Display.SYM_WIDTH):
                        self.img.put(colors[pos + full_offset], (col,row))
                        pos += 1

    def get_bitmap(self, word):
        for i in range(0, 16):
            yield (word & (0x1 << i)) >> i
