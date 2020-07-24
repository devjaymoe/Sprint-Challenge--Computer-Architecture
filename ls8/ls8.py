#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()
# print(sys.argv)
cpu.load()
cpu.run()