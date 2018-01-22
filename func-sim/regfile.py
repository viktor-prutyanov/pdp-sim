from array import array

class RegFile:
    def __init__(self, init_pc):
        self.regs = array('H', [0] * 8)
        self.c = False
        self.v = False
        self.z = False
        self.n = False
        self.t = False
        self.regs[7] = init_pc

    def __getitem__(self, key):
        print("RegFile: R{0} = 0x{1:04X}".format(key, self.regs[key]))
        return self.regs[key]
    
    def __setitem__(self, key, value):
        print("RegFile: R{0} <- 0x{1:04X}".format(key, value))
        self.regs[key] = value

    def get_pc(self):
        return self.regs[7]

    def set_pc(self, val):
        self.regs[7] = val
        return val

    def get_sp(self):
        return self.regs[6]

    def set_sp(self, val):
        self.regs[6] = val

    def set_z(self, val):
        if (val == 0):
            self.z = True
        else:
            self.z = False 
