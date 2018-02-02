from memory import Memory
from regfile import RegFile
from enum import IntEnum

class InstrType(IntEnum):
    ZeroOp = 0
    OneOp = 1
    TwoOp = 2
    Branch = 3
    OneAndAHalf = 4
    Jsr = 5
    Rts = 6
    Error = -1

class Mode(IntEnum):
    Reg = 0
    RegDef = 1
    AutoIncr = 2
    AutoIncrDef = 3
    Index = 6
    IndexDef = 7

class ModePC(IntEnum):
    Immediate = 2
    Absolute = 3
    Relative = 6
    RelativeDef = 7

def byte_get_num(byte):
    if (byte & 0x80):
        print(byte)
        return -((byte ^ 0xFF))
    else:
        return byte

def addr_to_str(a):
    mode = (a & 0o70) >> 3
    reg = a & 0o7
    
    if reg != 7:
        if mode == Mode.Reg:
            return "R{}".format(reg)
        elif mode == Mode.RegDef:
            return "(R{})".format(reg)
        elif mode == Mode.AutoIncr:
            return "(R{})+".format(reg)
        else:
            return "[INV]"
    else:
        if mode == ModePC.Immediate:
            return "$imm"
        else:
            return "[INV]"


class Core:
    def __init__(self, filename, length):
        self.regfile = RegFile(Memory.ROM)
        self.memory = Memory(filename, length)
        self.is_halted = False
        self.step_cnt = 0
        self.clock = 0
        self.last_instr_string = ""

    def reset(self):
        self.regfile.reset()
        self.memory.reset()
        self.is_halted = False
        self.step_cnt = 0
        self.clock = 0
        self.last_instr_string = ""

    def get_by_addr(self, addr, b):
        res = self.memory.read(addr)
        if b:
            if addr % 2 == 0:
                return res & 0x00FF
            else:
                return (res & 0xFF00) >> 8
        else:
            return res
    
    def set_addr(self, addr, val, b):
        if b:
            word = self.memory.read(addr)
            if addr % 2 == 0:
                word = (word & 0xFF00) | (val & 0x00FF)
            else:
                word = (word & 0x00FF) | ((val & 0x00FF) << 8)
        else:
            self.memory.write(addr, val)

    def get_src(self, byte, b):
        mode = (byte & 0o70) >> 3
        reg = byte & 0o7

        print("mode = ", mode)
        if reg != 7: # 111b
            if mode == Mode.Reg:
                return self.regfile[reg]
            elif mode == Mode.RegDef:
                addr = self.regfile[reg]
                return self.get_by_addr(addr, b)
            elif mode == Mode.AutoIncr:
                res = self.get_by_addr(self.regfile[reg], b)
                if b:
                    self.regfile[reg] += 1
                else:
                    self.regfile[reg] += 2
                return res
            elif mode == Mode.AutoIncrDef:
                res = self.get_by_addr(get_addr(self.regfile[reg]), b)
                if b:
                    self.regfile[reg] += 1
                else:
                    self.regfile[reg] += 2
                return res
            elif mode == Mode.Index:
                self.set_next_pc()
                offset = self.memory.read(self.get_cur_pc())
                return self.get_by_addr((offset + self.regfile[reg]), b)
        else:
            if mode == ModePC.Immediate:
                self.set_next_pc()
                res = self.memory.read(self.get_cur_pc())
                return res
            elif mode == ModePC.Absolute:
                self.set_next_pc()
                return get_addr(self.memory.read(self.get_cur_pc()))

    def set_dst(self, byte, value, b):
        mode = (byte & 0o70) >> 3
        reg = byte & 0o7

        if reg != 7:
            if mode == Mode.Reg:
                self.regfile[reg] = value
            elif mode == Mode.RegDef:
                self.set_addr(self.regfile[reg], value, b)
            elif mode == Mode.AutoIncr:
                self.set_addr(self.regfile[reg], value, b)
                if b:
                    self.regfile[reg] += 1
                else:
                    self.regfile[reg] += 2
            elif mode == Mode.AutoIncrDef:
                self.set_addr(self.memory.read(self.regfile[reg]), value, b)
                if b:
                    self.regfile[reg] += 1
                else:
                    self.regfile[reg] += 2
        else:
            if mode == ModePC.Absolute:
                self.set_next_pc()
                return self.set_addr(memory.read(self.get_cur_pc()), value, b)

        return

    def decode(self, word):
        instrs = [
        #     Name     Mask   Shift CheckVal    Type                    Handler
            ('halt',  0xFFFF,   0,  0x0000, InstrType.ZeroOp,       self.ex_halt),
            ('nop',   0xFFFF,   0,  0x00A0, InstrType.ZeroOp,       self.ex_nop),
            ('clr',   0xEFC0,   6,  0o0050, InstrType.OneOp,        self.ex_clr),
            ('tst',   0xEFC0,   6,  0o0057, InstrType.OneOp,        self.ex_tst),
            ('tstb',  0xEFC0,   6,  0o1057, InstrType.OneOp,        self.ex_tstb),
            ('inc',   0xEFC0,   6,  0o0052, InstrType.OneOp,        self.ex_inc),
            ('dec',   0xEFC0,   6,  0o0053, InstrType.OneOp,        self.ex_dec),
            ('asr',   0xEFC0,   6,  0o0062, InstrType.OneOp,        self.ex_asr),
            ('asl',   0xEFC0,   6,  0o0063, InstrType.OneOp,        self.ex_asl),
            ('mov',   0xF000,   12, 0o0001, InstrType.TwoOp,        self.ex_mov),
            ('movb',  0xF000,   12, 0o0011, InstrType.TwoOp,        self.ex_movb),
            ('cmp',   0xF000,   12, 0o0002, InstrType.TwoOp,        self.ex_cmp),
            ('cmpb',  0xF000,   12, 0o0012, InstrType.TwoOp,        self.ex_cmpb),
            ('sub',   0xF000,   12, 0o0016, InstrType.TwoOp,        self.ex_sub),
            ('add',   0xF000,   12, 0o0006, InstrType.TwoOp,        self.ex_add),
            ('br',    0xFF00,   8,  0x0001, InstrType.Branch,       self.ex_br),
            ('bne',   0xFF00,   8,  0x0002, InstrType.Branch,       self.ex_bne),
            ('beq',   0xFF00,   8,  0x0003, InstrType.Branch,       self.ex_beq),
            ('ash',   0xFE00,   9,  0o0072, InstrType.OneAndAHalf,  self.ex_ash),
            ('jsr',   0xFE00,   9,  0o0004, InstrType.Jsr,          self.ex_jsr),
            ('rts',   0xFFF8,   3,  0o0020, InstrType.Rts,          self.ex_rts)
        ]

        for instr in instrs:
            if ((word & instr[1]) >> instr[2]) == instr[3]:
                if instr[4] == InstrType.ZeroOp:
                    self.instr = {'type': instr[4], 'name': instr[0], 'execute': instr[5],
                            'str': instr[0]}
                    string = instr[0]
                elif instr[4] == InstrType.OneOp:
                    string = "{} {}".format(instr[0], addr_to_str((word & 0o77)))
                    self.instr = {'type': instr[4], 'name': instr[0], 'execute': instr[5], 
                            'addr': (word & 0o77), 'str': string}
                elif instr[4] == InstrType.TwoOp:
                    src = (word & 0o7700) >> 6
                    dst = (word & 0o77)
                    string = "{} {} {}".format(instr[0], addr_to_str(src), addr_to_str(dst))
                    self.instr = {'type': instr[4], 'name': instr[0], 'execute': instr[5], 
                            'src': src, 'dst': dst, 'str': string}
                elif instr[4] == InstrType.OneAndAHalf:
                    reg = (word & 0o700) >> 6
                    addr = (word & 0o77)
                    string = "{} {} {}".format(instr[0], addr_to_str(reg), addr_to_str(addr))
                    self.instr = {'type': instr[4], 'name': instr[0], 'execute': instr[5], 
                            'reg': reg, 'addr': addr, 'str': string}
                elif instr[4] == InstrType.Branch:
                    offset = byte_get_num(word & 0x00FF)
                    string = "{} {}".format(instr[0], offset)
                    self.instr = {'type': instr[4], 'name': instr[0], 'execute': instr[5],
                            'offset': offset, 'str': string}
                elif instr[4] == InstrType.Jsr:
                    reg = (word & 0o700) >> 6
                    addr = (word & 0o77)
                    string = "{} {} {}".format(instr[0], addr_to_str(reg), addr_to_str(addr))
                    self.instr = {'type': instr[4], 'name': instr[0], 'execute': instr[5], 
                            'reg': reg, 'addr': addr, 'str': string}
                elif instr[4] == InstrType.Rts:
                    reg = word & 0o7
                    string = "{} {}".format(instr[0], addr_to_str(reg))
                    self.instr = {'type': instr[4], 'name': instr[0], 'execute': instr[5], 
                            'reg': reg, 'str': string}
                else:
                    string = "[INV INSTR]"
                    self.instr = None

                self.last_instr_string = "[0x{0:04X}] {1}".format(self.regfile.get_pc(), string)
                return

            string = "[INV INSTR]"
            self.instr = None
            self.last_instr_string = string

    def set_z_flag(self, val):
        if (val == 0):
            self.regfile.z = True
        else:
            self.regfile.z = False

    def set_flag_value_scheme(self, val):
        self.set_z_flag(val)

    def set_next_pc(self):
        pc = self.regfile.get_pc()
        self.regfile.set_pc(pc + 2)

    def get_cur_pc(self):
        return self.regfile.get_pc()

    def ex_nop(self, instr):
        self.set_next_pc()
    
    def ex_clr(self, instr):
        self.set_dst(instr['addr'], 0, False)
        self.set_flag_value_scheme(self, 0)
        self.set_next_pc()

    def ex_halt(self, instr):
        self.is_halted = True
        self.set_next_pc()
    
    def ex_tst(self, instr):
        val = self.get_src(instr['addr'], False)
        self.set_z_flag(val)
        self.set_next_pc()
    
    def ex_tstb(self, instr):
        val = self.get_src(instr['addr'], True)
        self.set_z_flag(val)
        self.set_next_pc()

    def ex_inc(self, instr):
        val = self.get_src(instr['addr'], False)
        if val != 0xFFFF:
            val += 1
        else:
            val = 0
        self.set_flag_value_scheme(val)
        self.set_dst(instr['addr'], val, False)
        self.set_next_pc()

    def ex_dec(self, instr):
        val = self.get_src(instr['addr'], False)
        if val == 0:
            val = 0xFFFF
        else:
            val -= 1
        self.set_flag_value_scheme(val)
        self.set_dst(instr['addr'], val, False)
        self.set_next_pc()

    def ex_asr(self, instr):
        val = self.regfile.regs[instr['addr']]
        self.regfile.regs[instr['addr']] = val >> 1
        self.set_flag_value_scheme(val)
        self.set_next_pc()

    def ex_asl(self, instr):
        val = self.regfile.regs[instr['addr']]
        self.regfile.regs[instr['addr']] = val << 1
        self.set_flag_value_scheme(val)
        self.set_next_pc()
    
    def ex_cmp(self, instr):
        src = self.get_src(instr['src'], False)
        dst = self.get_src(instr['dst'], False)
        val = dst - src
        self.set_flag_value_scheme(val)
        self.set_next_pc()
    
    def ex_add(self, instr):
        src = self.get_src(instr['src'], False)
        dst = self.get_src(instr['dst'], False)
        val = dst + src
        self.set_flag_value_scheme(val)
        self.set_next_pc()
    
    def ex_sub(self, instr):
        src = self.get_src(instr['src'], False)
        dst = self.get_src(instr['dst'], False)
        val = dst - src
        self.set_flag_value_scheme(val)
        self.set_next_pc()

    def ex_ash(self, instr):
        addr = self.get_src(instr['addr'], False) & 0o77
        val = self.get_src(instr['reg'], False)
        if addr & 0o40:
            val >>= (addr ^ 0o77) + 1
        else:
            val <<= addr
        self.set_dst(instr['reg'], val, False)
        self.set_next_pc()

    def ex_jsr(self, instr):
        addr = self.get_src(instr['addr'], False)
        r = self.regfile[instr['reg']]
        self.regfile.set_sp(self.regfile.get_sp() - 2)
        self.memory.write(self.regfile.get_sp(), r)
        self.set_next_pc()
        self.regfile[instr['reg']] = self.regfile.get_pc()
        self.regfile.set_pc(addr)

    def ex_rts(self, instr):
        r = self.regfile[instr['reg']]
        self.regfile.set_pc(r)
        sp = self.regfile.get_sp()
        self.regfile[instr['reg']] = self.memory.read(sp)
        self.regfile.set_sp(sp + 2)
    
    def ex_cmpb(self, instr):
        src = self.get_src(instr['src'], True)
        dst = self.get_src(instr['dst'], True)
        self.set_flag_value_scheme(dst - src)
        self.set_next_pc()

    def ex_mov(self, instr):
        val = self.get_src(instr['src'], False)
        self.set_dst(instr['dst'], val, False)
        self.set_next_pc()
    
    def ex_movb(self, instr):
        val = self.get_src(instr['src'], True)
        self.set_dst(instr['dst'], val, True)
        self.set_next_pc()
    
    def ex_br(self, instr):
        self.regfile.set_pc(self.regfile.get_pc() + 2 * instr['offset'])

    def ex_bne(self, instr):
        self.set_next_pc()
        if not self.regfile.z:
            self.regfile.set_pc(self.regfile.get_pc() + 2 * instr['offset'])
            print("BRANCH TAKEN")
        self.regfile.z = False
    
    def ex_beq(self, instr):
        self.set_next_pc()
        if (self.regfile.z):
            self.regfile.set_pc(self.regfile.get_pc() + 2 * instr['offset'])
            print("BRANCH TAKEN")
        self.regfile.z = False

    def execute(self):
        self.instr['execute'](self.instr)
        self.clock += 1

    def step(self):
        pc = self.regfile.get_pc()
        self.decode(self.memory.read(pc))
        print(self.instr)
        self.execute()
        self.step_cnt += 1
        return self.last_instr_string

    def run(self):
        while not self.is_halted:
            self.step()
