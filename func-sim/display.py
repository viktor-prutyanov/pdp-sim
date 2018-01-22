from memory import Memory
from math import sin, cos
import tkinter as tk
import random

class Display:
    WIDTH  = 256
    HEIGHT = 256

    def __init__(self, top, memory):
        self.memory = memory

        # @brief draw bitmap image
        canvas = tk.Canvas(top, width=Display.WIDTH, height=Display.HEIGHT, bg="#000000")
        canvas.pack()
        self.img = tk.PhotoImage(width=Display.WIDTH, height=Display.HEIGHT)
        canvas.create_image(0, 0, image = self.img, anchor=tk.NW)

    def display_sin(self):
        for x in range(4 * Display.WIDTH):
            y = int(Display.HEIGHT/2 + Display.HEIGHT/4 * sin(x/80.0))
            self.img.put("#ffffff", (x//4,y))

    def display_random(self):
        colors = [[random.randint(0,255) for i in range(0,3)] for j in range(0, Display.WIDTH * Display.HEIGHT)]
        row = 0; col = 0
        for color in colors:
           self.img.put('#%02x%02x%02x' % tuple(color),(row,col))
           col += 1
           if col == Display.WIDTH:
               row +=1; col = 0

    def display_vram(self):
        colors = []
        for word in self.memory.get_vram_range():
            for bit in self.get_bitmap(word):
                if not bit:
                    colors.append("#000000")
                else:
                    colors.append("#ffffff")

        row = 0; col = 0
        for color in colors:
           self.img.put(color, (row,col))
           col += 1
           if col == Display.WIDTH:
               row +=1; col = 0

    def get_bitmap(self, word):
        for i in range(0, 16):
            yield (word & (0x1 << i)) >> i
