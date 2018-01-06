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
        self.is_halted = False
    
    def decode(self, word):
        instrs = [
        #     Name     Mask   Shift CheckVal    Type              Handler
            ('halt',  0xFFFF,   0,  0x0000, InstrType.ZeroOp,   self.ex_halt),
            ('nop',   0xFFFF,   0,  0x00A0, InstrType.ZeroOp,   self.ex_nop),
            ('clr',   0xEFC0,   6,  0o0050, InstrType.OneOp,    self.ex_nop),
            ('inc',   0xEFC0,   6,  0o0052, InstrType.OneOp,    self.ex_inc),
            ('dec',   0xEFC0,   6,  0o0053, InstrType.OneOp,    self.ex_dec),
            ('asr',   0xEFC0,   6,  0o0062, InstrType.OneOp,    self.ex_asr),
            ('asl',   0xEFC0,   6,  0o0063, InstrType.OneOp,    self.ex_asl),
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

    def ex_nop(self, instr):
        self.set_next_pc()
    
    def ex_halt(self, instr):
        self.is_halted = True
        self.set_next_pc()

    def ex_inc(self, instr):
        self.regfile.regs[instr['addr']] += 1
        self.set_next_pc()
    
    def ex_dec(self, instr):
        val = self.regfile.regs[instr['addr']]
        if val == 0:
            self.regfile.regs[instr['addr']] = 0xFFFF
        else:
            self.regfile.regs[instr['addr']] -= 1
        self.set_next_pc()
    
    def ex_asr(self, instr):
        self.regfile.regs[instr['addr']] <<= 1
        self.set_next_pc()
    
    def ex_asl(self, instr):
        self.regfile.regs[instr['addr']] >>= 1
        self.set_next_pc()

    def execute(self):
        self.instr['execute'](self.instr)

    def step(self):
        pc = self.regfile.get_pc()
        self.decode(self.memory.read(pc))
        print(self.instr)
        self.execute()

    def run(self):
        while not self.is_halted:
            self.step()
