from array import array
from cache import CacheFA, CacheDM
from enum import Enum
import tkinter as tk
import random

class Memory:
    """
    Memmory map:
    -------------
    | RAM  16Kb |
    -------------
    | VRAM 32Kb |
    -------------
    | ROM  15Kb |
    -------------
    | I/O  1Kb  |
    -------------
    """

    RAM  = 0x0000
    VRAM = 0x4000
    ROM  = 0xC000
    IO   = 0xFC00

    NoCache = 0
    FullyAssociative = 1
    DirectMapped = 2

    memory_size = 64 * 1024 # 64 Kb

    def __init__(self, filename, length):
        self.data = array('H', [0] * (Memory.memory_size // 2))
        rom = array('H', [])
        self.clock = 0
        self.cache = None
        self.use_cache = False

        # @brief load bin to ROM
        with open(filename, 'rb') as f:
            rom.fromfile(f, length)
            cur_addr = Memory.ROM
            for word in rom:
                self.data[cur_addr // 2] = word
                cur_addr += 2

        _, self.length = self.data.buffer_info()

    def set_cache_type(self, cache_type, length):
        if cache_type == Memory.FullyAssociative:
            self.cache = CacheFA(length, self.__write, self.__read)
            self.use_cache = True
            print("Cache enabled, fully associative, length = ", length)
        elif cache_type == Memory.DirectMapped:
            self.cache = CacheDM(length, self.__write, self.__read)
            self.use_cache = True
            print("Cache enabled, direct-mapped, length = ", length)
        else:
            self.cache = None
            self.use_cache = False
            print("Cache disabled")

    def reset(self):
        self.clock = 0
        for i in range(Memory.ROM // 2):
            self.data[i] = 0
        if self.cache is not None:
            self.cache.reset()

    def __read(self, word_addr):
        word = self.data[word_addr]
        print("Memory : read  0x{0:04x} =  0x{1:04x}".format(word_addr * 2, word))
        self.clock += 1
        return word

    def read(self, addr):
        if self.use_cache:
            word = self.cache.read(addr // 2)
        else:
            word = self.__read(addr // 2)
        return word

    def __write(self, word_addr, word):
        print("Memory : write 0x{0:04x} <- 0x{1:04x}".format(word_addr * 2, word))
        self.data[word_addr] = word
        self.clock += 1

    def __io_write(self, addr, word):
        if (addr == 0xFC00):
            print("I/O    : display <- {}".format(word))
            self.display_handler(word)
            self.clock += 1
        else:
            print("I/O    : ERROR")

    def write(self, addr, word):
        if (addr >= self.IO):
            self.__io_write(addr, word)
        else:
            if self.use_cache:
                self.cache.write(addr // 2, word)
            else:
                self.__write(addr // 2, word)

    def set_display_handler(self, func):
        self.display_handler = func

    def get_vram_range(self):
        for idx in range(Memory.VRAM // 2, Memory.ROM // 2):
            yield self.data[idx]

    def load_font(self, addr):
        img = tk.PhotoImage(file="font.ppm")
        for block_y in range(16):
            for block_x in range(16):
                for word in range(4):
                    pix_word = 0x0000
                    for bit in range(16):
                        pix = img.get(block_x * 8 + bit % 8, block_y * 8 + word * 2 + bit // 8)
                        if pix[0] == 0:
                            pix_word = pix_word >> 1
                        else:
                            pix_word = (pix_word >> 1) | 0x8000
                    idx = addr // 2 + (block_y * 16 + block_x) * 4 + word
                    self.data[idx] = pix_word
