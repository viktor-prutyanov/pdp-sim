from array import array

class Memory:
    def __init__(self, filename, length):
        self.data = array('H', [])
        with open(filename, 'rb') as f:
            self.data.fromfile(f, length)
            
        _, self.length = self.data.buffer_info()

    def read(self, addr):
        word = self.data[addr]
        print("read from 0x{0:04x} = 0x{1:04x}".format(addr, word))
        return word

    def write(self, addr, word):
        print("write 0x{0:04x} to 0x{1:04x}".format(addr, word))
        self.data[addr] = word
