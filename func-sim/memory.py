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
        print("read from 0x{0:04x} = 0x{1:04x}".format(addr, word))
        return word

    def write(self, addr, word):
        print("write 0x{0:04x} to 0x{1:04x}".format(addr, word))
        self.data[addr // 2] = word

    def get_vram_range(self):
        for idx in range(Memory.VRAM // 2, Memory.ROM // 2):
            yield self.data[idx]

    def fill_vram(self):
        for idx in range(Memory.VRAM // 2, Memory.ROM // 2):
            self.data[idx] = random.randint(0, 255)