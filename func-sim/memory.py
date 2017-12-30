from array import array

class Memory:
    def __init__(self, length):
        self.data = array('H', [0] * length)

    def read(self, addr):
        word = self.data[addr]
        print("read from {0:#04x} = {1:#04x}".format(addr, word))
        return word

    def write(self, addr, word):
        print("write {0:#04x} to {1:#04x}".format(addr, word))
        self.data[addr] = word
