from memory import Memory
from regfile import RegFile
from enum import Enum

class InstrType(Enum):
    ZeroOp = 0
    OneOp = 1
    TwoOp = 2
    Branch = 3
    Error = -1

class Mode(Enum):
    Reg = 0
    RegDef = 1
    AutoIncr = 2
    AutoIncrDef = 3
    Index = 6
    IndexDef = 7

class ModePC(Enum):
    Immediate = 2
    Absolute = 3
    Relative = 6
    RelativeDef = 7

class Core:
    def __init__(self, filename, length):
        self.regfile = RegFile(Memory.ROM)
        self.memory = Memory(filename, length)
        self.is_halted = False

    def get_src(self, byte):
        mode = (byte & 0o70) >> 3
        reg = byte & 0o7
        get_by_addr = lambda addr: self.memory.read(addr)

        if reg != 7: # 111b
            print(mode)
            if mode == Mode.Reg:
                return self.regfile[reg]
            elif mode == Mode.RegDef:
                return get_by_addr(self.regfile[reg])
            elif mode == Mode.AutoIncr:
                res = get_by_addr(self.regfile[reg])
                self.regfile[reg] += 2
                return res
            elif mode == Mode.AutoIncrDef:
                res = get_by_addr(get_addr(self.regfile[reg]))
                self.regfile[reg] += 2
                return res
            elif mode == Mode.Index:
                self.set_next_pc()
                offset = memory.read(self.get_cur_pc())
                return get_by_addr((offset + self.regfile[reg]))
        else:
            print(mode)
            if mode == ModePC.Immediate:
                print(mode)
                self.set_next_pc()
                res = memory.read(self.get_cur_pc())
                print(res)
                return res
            elif mode == ModePC.Absolute:
                self.set_next_pc()
                return get_addr(memory.read(self.get_cur_pc()))


    def set_dst(self, byte, value):
        mode = (byte & 0o70) >> 3
        reg = byte & 0o7
        set_addr = lambda addr, word: self.memory.write(addr, word)

        if reg != 7:
            if mode == Mode.Reg:
                self.regfile[reg] = value
            elif mode == Mode.RegDef:
                set_addr(self.regfile[reg], value)
            elif mode == Mode.AutoIncr:
                set_addr(self.regfile[reg], value)
                self.regfile[reg] += 2
            elif mode == Mode.AutoIncrDef:
                set_addr(self.memory.read(self.regfile[reg]), value)
                self.regfile[reg] += 2
        else:
            if mode == ModePC.Absolute:
                self.set_next_pc()
                return set_addr(memory.read(self.get_cur_pc()), value)

        return

    def decode(self, word):
        print(word)
        instrs = [
        #     Name     Mask   Shift CheckVal    Type              Handler
            ('halt',  0xFFFF,   0,  0x0000, InstrType.ZeroOp,   self.ex_halt),
            ('nop',   0xFFFF,   0,  0x00A0, InstrType.ZeroOp,   self.ex_nop),
            ('clr',   0xEFC0,   6,  0o0050, InstrType.OneOp,    self.ex_nop),
            ('inc',   0xEFC0,   6,  0o0052, InstrType.OneOp,    self.ex_inc),
            ('dec',   0xEFC0,   6,  0o0053, InstrType.OneOp,    self.ex_dec),
            ('asr',   0xEFC0,   6,  0o0062, InstrType.OneOp,    self.ex_asr),
            ('asl',   0xEFC0,   6,  0o0063, InstrType.OneOp,    self.ex_asl),
            ('mov',   0xF000,   12, 0o0001, InstrType.TwoOp,    self.ex_mov),
            ]

        for instr in instrs:
            if ((word & instr[1]) >> instr[2]) == instr[3]:
                if instr[4] == InstrType.ZeroOp:
                    self.instr = {'type': instr[4], 'name': instr[0], 'execute': instr[5]}
                elif instr[4] == InstrType.OneOp:
                    self.instr = {'type': instr[4], 'name': instr[0], 'execute': instr[5], 'addr': (word & 0o77)}
                elif instr[4] == InstrType.TwoOp:
                    self.instr = {'type': instr[4], 'name': instr[0], 'execute': instr[5], 'src': (word & 0o7700) >> 6, 'dst': (word & 0o77)}
                else:
                    self.instr = None

                return

        self.instr = None

    def set_next_pc(self):
        pc = self.regfile.get_pc()
        self.regfile.set_pc(pc + 2)

    def get_cur_pc(self):
        return self.regfile.get_pc()

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

    def ex_mov(self, instr):
        self.set_dst(instr['dst'], self.get_src(instr['src']))
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
