from memory import Memory
from regfile import RegFile

class Core:
    def __init__(self, filename, length):
        self.regfile = RegFile()
        self.memory = Memory(filename, length) 

    def run(self):
        pc = 0
        while (pc < self.memory.length):
            r = self.memory.read(pc)
            pc = self.regfile.set_pc(pc + 1)
