#!/usr/bin/python3

from core import Core
import sys
import os
   
if (len(sys.argv) != 2):
    print("usage: {} file.bin".format(sys.argv[0]))
    sys.exit()

filename = sys.argv[1]

core = Core(filename, os.path.getsize(filename) // 2)
core.run()
