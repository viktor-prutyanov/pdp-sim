from array import array

class RegFile:
    def __init__(self):
        self.regs = array('H', [0] * 8)
        self.psw = 0

    def get_pc(self):
        return self.regs[7]
    
    def set_pc(self, val):
        self.regs[7] = val
        return val

    def get_sp(self):
        return self.regs[6]
    
    def set_sp(self, val):
        self.regs[6] = val
