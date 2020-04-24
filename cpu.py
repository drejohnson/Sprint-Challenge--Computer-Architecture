"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        self.ram = [0] * 256
        self.reg = [0] * 8
        self.sp = 7
        self.reg[self.sp] = 0xF4
        self.pc = 0
        self.ir = self.pc
        self.fl = 6
        self.instructions = {
            0b10000010: self.ldi_handler,
            0b01000111: self.prn_handler,
            0b00000001: self.hlt_handler,
            0b10100000: self.add_handler,
            0b10100010: self.mult_handler,
            0b01000101: self.push_handler,
            0b01000110: self.pop_handler,
            0b01010000: self.call_handler,
            0b10100111: self.cmp_handler,
            0b00010001: self.ret_handler,
            0b01010110: self.jne_handler,
            0b01010100: self.jmp_handler,
            0b01010101: self.jeq_handler
        }

    def load(self):
        """Load a program into memory."""

        address = 0

        file = open('sctest.ls8',  "r")
        for line in file.readlines():
            # load a line into memory (not including comments)
            try:
                x = line[:line.index("#")]
            except ValueError:
                x = line

            try:
                # convert binary to decimal
                y = int(x, 2)
                self.ram[address] = y
            except ValueError:
                continue
            address += 1

    def ldi_handler(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def prn_handler(self, operand_a, operand_b):
        print(self.reg[operand_a])

    def hlt_handler(self, operand_a, operand_b):
        sys.exit()

    def mult_handler(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)

    # Add value to the stack.
    def push_handler(self, operand_a, operand_b):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.reg[operand_a]

    # Pop value off the stack into the given register.
    def pop_handler(self, operand_a, operand_b):
        self.reg[operand_a] = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

    # Sets the PC to the register value
    def call_handler(self, operand_a, operand_b):
        # address of instruction after call is pushed on to the stack
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + 2
        # set PC to value stored in given register
        self.pc = self.reg[operand_a]
        return True

    def ret_handler(self, operand_a, operand_b):
        # pop value from stack into register operand_a
        self.pop(operand_a, 0)
        self.pc = self.reg[operand_a]
        return True

    def add_handler(self, operand_a, operand_b):
        self.reg[operand_a] = self.reg[operand_a] + self.reg[operand_b]

    def cmp_handler(self, operand_a, operand_b):
        # self.alu("CMP", operand_a, operand_b)
        value_a = self.reg[operand_a]
        value_b = self.reg[operand_b]

        if value_a == value_b:
            # need to turn the bit in the 0th place to 1
            self.reg[self.fl] = 1
        elif value_a > value_b:
            self.reg[self.fl] = 2
        else:
            self.reg[self.fl] = 4

    def jne_handler(self, operand_a, operand_b):
        value = self.reg[self.fl]
        if value == 2 or value == 4:  # not equal
            return self.jmp_handler(operand_a, 0)

    def jmp_handler(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]
        return True

    def jeq_handler(self, operand_a, operand_b):
        if self.reg[self.fl] == 1:
            return self.jmp_handler(operand_a, 0)

    # accept memory address to read read and return the value stored there
    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        
        # register (IR)
        while True:
            self.ir = self.ram[self.pc]
            operand_a = self.ram[self.pc + 1]
            operand_b = self.ram[self.pc + 2]
            ir_length = (self.ir >> 6) + 1

            jump_instructions = self.instructions[self.ir](operand_a, operand_b)

            # shift right by 6 elements 
            # to find the # of arguments this function takes
            if not jump_instructions:
                self.pc += ir_length
