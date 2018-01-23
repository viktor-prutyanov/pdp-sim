from array import array
from enum import Enum
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

    memory_size = 64 * 1024 # 64 Kb

    def __init__(self, filename, length):
        self.data = array('H', [0] * (Memory.memory_size // 2))
        rom = array('H', [])

        # @brief load bin to ROM
        with open(filename, 'rb') as f:
            rom.fromfile(f, length)
            cur_addr = Memory.ROM
            for word in rom:
                self.data[cur_addr // 2] = word
                cur_addr += 2

        _, self.length = self.data.buffer_info()

    def read(self, addr):
        word = self.data[addr // 2]
        print("Memory : read  0x{0:04x} =  0x{1:04x}".format(addr, word))
        return word

    def write(self, addr, word):
        if (addr == 0xFC00):
            print("I/O    : display <- {}".format(word))
            self.display_handler(word)
        else:
            print("Memory : write 0x{0:04x} <- 0x{1:04x}".format(addr, word))
            self.data[addr // 2] = word

    def set_display_handler(self, func):
        self.display_handler = func

    def get_vram_range(self):
        for idx in range(Memory.VRAM // 2, Memory.ROM // 2):
            yield self.data[idx]

    def fill_vram(self):
        for idx in range(Memory.VRAM // 2, Memory.ROM // 2):
            self.data[idx] = random.randint(0, 255)

    def fill_vram_with_sharp(self):
        for block in range(Memory.VRAM // 8, Memory.ROM // 8):
            pos = block * 4
            self.data[pos] = 0x2424
            self.data[pos + 1] = 0xFF24
            self.data[pos + 2] = 0x24FF
            self.data[pos + 3] = 0x2424

    def fill_vram_with_line(self):
        for block in range(Memory.VRAM // 32, Memory.ROM // 32):
            pos = block * 16
            self.data[pos] = 0xFFFF
            self.data[pos + 1] = 0xFFFF
            self.data[pos + 2] = 0xFFFF
            self.data[pos + 3] = 0xFFFF
            self.data[pos + 4] = 0x0000
            self.data[pos + 5] = 0x0000
            self.data[pos + 6] = 0x0000
            self.data[pos + 7] = 0x0000
            self.data[pos + 8] = 0x1818
            self.data[pos + 9] = 0x1818
            self.data[pos + 10] = 0x1818
            self.data[pos + 11] = 0x1818
            self.data[pos + 12] = 0x1818
            self.data[pos + 13] = 0x1818
            self.data[pos + 14] = 0x1818
            self.data[pos + 15] = 0x1818

