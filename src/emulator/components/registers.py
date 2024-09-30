class Registry:
    def __init__(self):
        self.IR = 0  # Instruction Register
        self.PC = 0  # Program Counter
        self.SP = 0x1000000  # Stack Pointer
        self.CR = 0  # Control Register
        self.AR = 0  # Address Register
        self.DR = 0  # Data Register
        self.SR = 0  # State Register
        self.BR = 0  # Buffer Register

    def __str__(self):
        return (f"PC: {self.PC & 0xFFFFFF:06X} "
                f"| SP: {self.SP & 0xFFFFFF:06X} "
                f"| CR: {self.CR & 0xFFFFFFFF:08X} "
                f"| AR: {self.AR & 0xFFFFFF:06X} "
                f"| DR: {self.DR & 0xFFFFFFFF:08X} "
                f"| SR: {self.SR & 0xFFFF:04X} "
                f"| BR: {self.BR & 0xFFFFFFFF:08X}")
