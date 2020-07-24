"""CPU functionality."""

import sys

SP = 7

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.pc = 0
        self.ram = [0] * 256
        self.running = True
        self.branch_table = {}
        self.fl = 0b00000000

        self.branch_table[LDI] = self.op_LDI
        self.branch_table[PRN] = self.op_PRN
        self.branch_table[HLT] = self.op_HLT
        self.branch_table[MUL] = self.op_MUL
        self.branch_table[ADD] = self.op_ADD
        self.branch_table[PUSH] = self.op_PUSH
        self.branch_table[POP] = self.op_POP
        self.branch_table[CALL] = self.op_CALL
        self.branch_table[RET] = self.op_RET
        self.branch_table[CMP] = self.op_CMP
        self.branch_table[JMP] = self.op_JMP
        self.branch_table[JEQ] = self.op_JEQ
        self.branch_table[JNE] = self.op_JNE

        self.reg[SP] = 0xf4

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    try:
                        line = line.split('#',1)[0]
                        line = int(line, 2)  # int() is base 10 by default
                        self.ram[address] = line
                        address += 1
                    except ValueError:
                        pass

        except FileNotFoundError:
            print(f"Couldn't find file {sys.argv[1]}")
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'CMP':
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100

            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010

            elif self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):

        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]

        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def op_JMP(self, running):
        reg_num = self.ram[self.pc + 1]
        self.pc = self.reg[reg_num]

    def op_LDI(self, running):
        reg_num = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]

        self.reg[reg_num] = value

        self.pc += 3  

    def op_PRN(self, running):
        reg_num = self.ram[self.pc + 1]
        print(self.reg[reg_num])

        self.pc += 2

    def op_HLT(self, running):
        # halt the cpu and exit em
        self.running = False

    def op_ADD(self, running):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        self.alu('ADD', reg_a, reg_b)

        self.pc += 3

    def op_CMP(self, running):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        self.alu('CMP', reg_a, reg_b)

        self.pc += 3

    def op_JEQ(self, running):

        if self.fl == 0b00000001:
            # print('hit')
            reg_num = self.ram[self.pc + 1]
            self.pc = self.reg[reg_num]

        else:
            self.pc += 2

    def op_JNE(self, running):

        if self.fl == 0b00000001:
            # print('equals')
            self.pc += 2

        else:
            # print('not equals')
            reg_num = self.ram[self.pc + 1]
            self.pc = self.reg[reg_num]

    def op_MUL(self, running):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        self.alu('MUL', reg_a, reg_b)

        self.pc += 3

    def op_PUSH(self, running):
        self.reg[SP] -= 1
        self.reg[SP] &= 0xff

        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num]

        address_to_push = self.reg[SP]
        # print(address_to_push)
        self.ram[address_to_push] = value

        self.pc += 2

    def op_POP(self, running):
        address_to_pop = self.reg[SP]
        value = self.ram[address_to_pop]

        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = value
        
        self.reg[SP] += 1
        
        self.pc += 2

    def op_CALL(self, running):
        return_addr = self.pc + 2

        self.reg[SP] -= 1
        address_to_push = self.reg[SP]
        self.ram[address_to_push] = return_addr

        reg_num = self.ram[self.pc + 1]
        subroutine_addr = self.reg[reg_num]

        self.pc = subroutine_addr

    def op_RET(self, running):
        address_to_pop = self.reg[SP]
        return_addr = self.ram[address_to_pop]
        self.reg[SP] += 1

        self.pc = return_addr

    def run(self):
        """Run the CPU."""
        # print("Ram: ", self.ram)
        # print("PC: ", self.pc)
        # print("Reg: ", self.reg)

        while self.running:
            # self.trace()

            instructions = self.ram_read(self.pc)
            # print(instructions)
            if instructions in self.branch_table:
                self.branch_table[instructions](self.running)
            else:
                print(f"Unknown instruction {instructions}")
                self.running = False