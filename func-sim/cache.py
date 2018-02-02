from array import array
from math import log

#
#   Fully associative write-through LRU cache 
#

class CacheFA:
    def __init__(self, length, direct_write, direct_read):
        self.direct_write = direct_write
        self.direct_read = direct_read
       
        self.tags = array('H', [0] * length)
        self.v_array = array('B', [0] * length)
        self.data = array('Q', [0] * length)
        self.recent = array('B', [0] * length)
        self.length = length
        
        self.total_cnt = 0
        self.miss_cnt = 0
        self.clock = 0

    def reset(self):
        for i in range(self.length):
            self.tags[i] = 0
            self.v_array[i] = 0
            self.data[i] = 0
            self.recent[i] = 0
      
        self.total_cnt = 0
        self.miss_cnt = 0
        self.clock = 0

    def get_hit_rate(self):
        if self.total_cnt != 0:
            return 1.0 - self.miss_cnt / self.total_cnt
        else:
            return 0.0

    def mk_miss(self, tag, offset, n):
        self.miss_cnt += 1
        print("Cache:   read miss tag = 0x{0:04X}, offset = 0x{1:1X}, n = {2}".format(tag, offset, n))
        self.data[n] = 0
        self.tags[n] = tag
        for i in range(4):
            word = self.direct_read(tag + i)
            if i == offset:
                w = word
            self.data[n] = self.data[n] | (word << i * 16)
        self.v_array[n] = 1
        self.recent[n] = 1
        return w

    def read(self, addr):
        tag = addr & 0xFFFC
        offset = addr & 0x3
        word_offset = offset * 16

        self.total_cnt += 1
        
        print(self.tags)
        print("Cache:   read at 0x{0:04X}".format(addr))

        for n in range(self.length):
            if ((self.tags[n] == tag) and (self.v_array[n] == 1)):
                self.clock += 1
                print("Cache:   read hit tag = 0x{0:04X}, offset = 0x{1:1X}".format(tag, offset))
                if self.recent[n] != 255:
                    self.recent[n] += 1
                else:
                    self.recent[n] = 255
                return (self.data[n] & (0xFFFF << word_offset)) >> word_offset

        for n in range(self.length):
            if self.v_array[n] == 0:
                return self.mk_miss(tag, offset, n)

        min_recent = 256 
        min_n = 0
        for n in range(self.length):
            if self.recent[n] < min_recent:
                min_recent = self.recent[n]
                min_n = n 

        return self.mk_miss(tag, offset, min_n)

    def write(self, addr, word):
        tag = addr & 0xFFFC
        offset = addr & 0x3
        word_offset = offset * 16

        for n in range(self.length):
            if (self.tags[n] == tag) and (self.v_array[n] == 1):
                self.data[n] = (self.data[n] & ((0x000000000000FFFF << word_offset) ^ 0x0)) | (word << word_offset)
        
        self.direct_write(addr, word)

#
#   Direct mapped write-through cache 
#

class CacheDM:
    def __init__(self, length, direct_write, direct_read):
        self.direct_write = direct_write
        self.direct_read = direct_read

        self.log_length = int(log(length, 2))
        self.length = 2 ** self.log_length
       
        self.tags = array('H', [0] * self.length)
        self.v_array = array('B', [0] * self.length)
        self.data = array('Q', [0] * self.length)
        
        self.total_cnt = 0
        self.miss_cnt = 0
        self.clock = 0

    def reset(self):
        for i in range(self.length):
            self.tags[i] = 0
            self.v_array[i] = 0
            self.data[i] = 0
      
        self.total_cnt = 0
        self.miss_cnt = 0
        self.clock = 0

    def get_hit_rate(self):
        if self.total_cnt != 0:
            return 1.0 - self.miss_cnt / self.total_cnt
        else:
            return 0.0

    def mk_miss(self, addr):
        offset = addr & 0x3
        s = (addr & ((self.length - 1) << 2)) >> 2
        tag = addr >> (self.log_length + 2)
        
        self.miss_cnt += 1
        print("Cache:   read miss tag = 0x{0:04X}, offset = 0x{1:1X}, set = 0x{2:04X}".format(tag, offset, s))
        self.data[s] = 0
        self.tags[s] = tag
        for i in range(4):
            word = self.direct_read((addr & 0xFFFC) + i)
            if i == offset:
                w = word
            self.data[s] = self.data[s] | (word << i * 16)
        self.v_array[s] = 1
        return w

    def read(self, addr):
        offset = addr & 0x3
        s = (addr & ((self.length - 1) << 2)) >> 2
        tag = addr >> (self.log_length + 2)
        word_offset = offset * 16

        self.total_cnt += 1
        self.clock += 1

        print(self.tags)
        print("Cache:   read at 0x{0:04X}".format(addr))

        if (self.tags[s] == tag) and (self.v_array[s] == 1):
            print("Cache:   read hit tag = 0x{0:04X}, offset = 0x{1:1X}, set = 0x{2:04X}".format(tag, offset, s))
            return (self.data[s] & (0xFFFF << word_offset)) >> word_offset
        else:
            return self.mk_miss(addr)

    def write(self, addr, word):
        offset = addr & 0x3
        s = (addr & ((self.length - 1) << 2)) >> 2
        tag = addr >> (self.log_length + 2)
        word_offset = offset * 16

        if (self.tags[s] == tag) and (self.v_array[s] == 1):
            self.data[s] = (self.data[s] & ((0x000000000000FFFF << word_offset) ^ 0x0)) | (word << word_offset)
        
        self.direct_write(addr, word)
