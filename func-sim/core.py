from memory import Memory
from regfile import RegFile
from enum import Enum

class InstrType(Enum):
    ZeroOp = 0
    OneOp = 1
    TwoOp = 2
    Branch = 3
    Error = -1

class Core:
    def __init__(self, filename, length):
        self.regfile = RegFile()
        self.memory = Memory(filename, length) 
        self.is_running = False
    
    def decode(self, word):
        instrs = [
        #     Name     Mask   Shift CheckVal    Type              Handler
            ('halt',  0xFFFF,   0,  0x0000, InstrType.ZeroOp,   self.execute_halt),
            ('nop',   0xFFFF,   0,  0x00A0, InstrType.ZeroOp,   self.execute_nop),
            ('clr',   0xEFC0,   6,  0o0050, InstrType.OneOp,    self.execute_nop),
            ('inc',   0xEFC0,   6,  0o0052, InstrType.OneOp,    self.execute_nop),
            ('dec',   0xEFC0,   6,  0o0053, InstrType.OneOp,    self.execute_nop),
            ('asr',   0xEFC0,   6,  0o0062, InstrType.OneOp,    self.execute_nop),
            ('asl',   0xEFC0,   6,  0o0063, InstrType.OneOp,    self.execute_nop),
            ]
        
        for instr in instrs:
            if ((word & instr[1]) >> instr[2]) == instr[3]:
                if instr[4] == InstrType.ZeroOp:
                    self.instr = {'type': instr[4], 'name': instr[0], 'execute': instr[5]}
                elif instr[4] == InstrType.OneOp:
                    self.instr = {'type': instr[4], 'name': instr[0], 'execute': instr[5], 'addr': (word & 0o77)}
                else:
                    self.instr = None

                return
    
        self.instr = None

    def set_next_pc(self):
        pc = self.regfile.get_pc()
        self.regfile.set_pc(pc + 1)

    def execute_nop(self):
        self.set_next_pc()
    
    def execute_halt(self):
        self.is_running = False
        self.set_next_pc()

    def execute(self):
        self.instr['execute']()

    def run(self):
        self.is_running = True

        while True:
            pc = self.regfile.get_pc()
            self.decode(self.memory.read(pc))
            print(self.instr)
            self.execute()
            
            if not self.is_running:
                return
