import time
from enum import Enum

from src.emulator.components.alu import alu_code, AluOperations, \
    OperandOperation
from src.emulator.components.commutator import commutator_code, CommutatorFlags
from src.emulator.data_path import DataPathOperations, RegisterCodes, \
    gen_mc, gen_mc_read, gen_mc_write
from src.emulator.mc_mnemonic_parser import parse_mnemonic


class AdrrMode(Enum):
    ABSOLUTE = 0b00
    RELATIVE = 0b01
    DIRECT = 0b10


address_mode = {
    0x00: AdrrMode.ABSOLUTE,
    0x01: AdrrMode.RELATIVE,
    0x02: AdrrMode.DIRECT
}


class AddrCommands(Enum):
    JMP = 0x80
    JZ = 0x84
    JE = 0x88
    JNZ = 0x8C
    JG = 0x90
    JGE = 0x94
    JL = 0x98
    JLE = 0x9C
    CALL = 0xA0
    PUSH = 0xA4
    SET = 0xF0,
    UNSET = 0xF4,
    CHECK = 0xFC


address_commands = {
    0x80: AddrCommands.JMP,
    0x84: AddrCommands.JZ,
    0x88: AddrCommands.JE,
    0x8C: AddrCommands.JNZ,
    0x90: AddrCommands.JG,
    0x94: AddrCommands.JGE,
    0x98: AddrCommands.JL,
    0x9C: AddrCommands.JLE,
    0xA0: AddrCommands.CALL,
    0xA4: AddrCommands.PUSH,
    0xF0: AddrCommands.SET,
    0xF4: AddrCommands.UNSET,
    0xFC: AddrCommands.CHECK,
}


class NonAddrCommands(Enum):
    NOP = 0x00
    POP = 0x02
    PUSHF = 0x03
    POPF = 0x04
    INC = 0x05
    DEC = 0x06
    SWAP = 0x07
    DUP = 0x08
    RET = 0x09
    HALT = 0x0A
    IRET = 0x0C
    EI = 0x0D
    DI = 0x0E
    ADD = 0x11
    SUB = 0x12
    MUL = 0x13
    DIV = 0x14
    AND = 0x15
    OR = 0x16
    XOR = 0x17
    NOT = 0x18
    NEG = 0x19
    SHL = 0x1A
    SHR = 0x1B
    ROL = 0x1C
    ROR = 0x1D
    CMP = 0x1E
    LD = 0x28
    ST = 0x29


non_address_commands = {
    0x00: NonAddrCommands.NOP,
    0x02: NonAddrCommands.POP,
    0x03: NonAddrCommands.PUSHF,
    0x04: NonAddrCommands.POPF,
    0x05: NonAddrCommands.INC,
    0x06: NonAddrCommands.DEC,
    0x07: NonAddrCommands.SWAP,
    0x08: NonAddrCommands.DUP,
    0x09: NonAddrCommands.RET,
    0x0A: NonAddrCommands.HALT,
    0x0C: NonAddrCommands.IRET,
    0x0D: NonAddrCommands.EI,
    0x0E: NonAddrCommands.DI,
    0x11: NonAddrCommands.ADD,
    0x12: NonAddrCommands.SUB,
    0x13: NonAddrCommands.MUL,
    0x14: NonAddrCommands.DIV,
    0x15: NonAddrCommands.AND,
    0x16: NonAddrCommands.OR,
    0x17: NonAddrCommands.XOR,
    0x18: NonAddrCommands.NOT,
    0x19: NonAddrCommands.NEG,
    0x1A: NonAddrCommands.SHL,
    0x1B: NonAddrCommands.SHR,
    0x1C: NonAddrCommands.ROL,
    0x1D: NonAddrCommands.ROR,
    0x1E: NonAddrCommands.CMP,
    0x28: NonAddrCommands.LD,
    0x29: NonAddrCommands.ST,
}


class ControlUnit:
    def __init__(self, registers, memory, data_path, io_devices):
        self.registers = registers
        self.data_path = data_path
        self.memory = memory
        self.tick = 0
        self.instruction = 0
        self.io_devices = io_devices

    def execute_mnemonic(self, mnemonic):
        code = parse_mnemonic(mnemonic)
        self.data_path.execute(code)
        self.inc_tick()

    def execute_addr_instruction(self, opcode):
        instruction = address_commands[opcode]
        if instruction == AddrCommands.PUSH:
            self.execute_push()
        elif instruction == AddrCommands.JMP:
            self.execute_jmp()
        elif instruction == AddrCommands.JZ:
            self.execute_jz()
        elif instruction == AddrCommands.JE:
            self.execute_je()
        elif instruction == AddrCommands.JNZ:
            self.execute_jnz()
        elif instruction == AddrCommands.JG:
            self.execute_jg()
        elif instruction == AddrCommands.JGE:
            self.execute_jge()
        elif instruction == AddrCommands.JL:
            self.execute_jl()
        elif instruction == AddrCommands.JLE:
            self.execute_jle()
        elif instruction == AddrCommands.CALL:
            self.execute_call()
        elif instruction == AddrCommands.SET:
            self.execute_set()
        elif instruction == AddrCommands.UNSET:
            self.execute_unset()
        elif instruction == AddrCommands.CHECK:
            self.execute_check()

    def execute_non_addr_instruction(self, opcode):
        instruction = non_address_commands[opcode]
        if instruction == NonAddrCommands.HALT:
            self.execute_halt()
        elif instruction == NonAddrCommands.NOP:
            self.execute_nop()
        elif instruction == NonAddrCommands.POP:
            self.execute_pop()
        elif instruction == NonAddrCommands.PUSHF:
            self.execute_pushf()
        elif instruction == NonAddrCommands.POPF:
            self.execute_popf()
        elif instruction == NonAddrCommands.INC:
            self.execute_inc()
        elif instruction == NonAddrCommands.DEC:
            self.execute_dec()
        elif instruction == NonAddrCommands.SWAP:
            self.execute_swap()
        elif instruction == NonAddrCommands.DUP:
            self.execute_dup()
        elif instruction == NonAddrCommands.RET:
            self.execute_ret()
        elif instruction == NonAddrCommands.IRET:
            self.execute_iret()
        elif instruction == NonAddrCommands.EI:
            self.execute_ei()
        elif instruction == NonAddrCommands.DI:
            self.execute_di()
        elif instruction == NonAddrCommands.ADD:
            self.execute_add()
        elif instruction == NonAddrCommands.SUB:
            self.execute_sub()
        elif instruction == NonAddrCommands.MUL:
            self.execute_mul()
        elif instruction == NonAddrCommands.DIV:
            self.execute_div()
        elif instruction == NonAddrCommands.AND:
            self.execute_and()
        elif instruction == NonAddrCommands.OR:
            self.execute_or()
        elif instruction == NonAddrCommands.NOT:
            self.execute_not()
        elif instruction == NonAddrCommands.NEG:
            self.execute_neg()
        elif instruction == NonAddrCommands.SHL:
            self.execute_shl()
        elif instruction == NonAddrCommands.SHR:
            self.execute_shr()
        elif instruction == NonAddrCommands.ROL:
            self.execute_rol()
        elif instruction == NonAddrCommands.ROR:
            self.execute_ror()
        elif instruction == NonAddrCommands.CMP:
            self.execute_cmp()
        elif instruction == NonAddrCommands.LD:
            self.execute_ld()
        elif instruction == NonAddrCommands.ST:
            self.execute_st()

    # Non addr instructions implementation
    def execute_halt(self):
        # TODO adjust implementation for microcode
        self.registers.SR &= 0x7FFF
        self.inc_tick()

    def execute_nop(self):
        pass

    def execute_pop(self):
        self.execute_mnemonic('SP + 1 -> SP')

    def execute_pushf(self):
        self.execute_mnemonic('SP + ~0 -> SP, AR')
        self.execute_mnemonic('SR -> DR')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_inc(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR + 1 -> DR')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_dec(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR + ~0 -> DR')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_swap(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR -> BR')
        self.execute_mnemonic('SP + 1 -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('DR -> MEM(AR)')
        self.execute_mnemonic('BR -> DR')
        self.execute_mnemonic('SP + 1 -> AR')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_popf(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR -> SR')
        self.execute_mnemonic('SP + 1 -> SP')

    def execute_dup(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('SP - 1 -> SP, AR')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_ret(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR -> PC')
        self.execute_mnemonic('SP + 1 -> SP')

    def execute_iret(self):
        self.execute_popf()
        self.execute_ret()

    def execute_ei(self):
        # TODO adjust implementation for microcode
        self.registers.SR |= 0x4000
        self.inc_tick()

    def execute_di(self):
        # TODO adjust implementation for microcode
        self.registers.SR &= 0xBFFF
        self.inc_tick()

    def execute_add(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR -> BR')
        self.execute_mnemonic('SP + 1 -> AR, SP')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('BR + DR -> DR {NZVC}')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_sub(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR -> BR')
        self.execute_mnemonic('SP + 1 -> AR, SP')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('BR + ~DR+1 -> DR {NZVC}')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_mul(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR -> BR')
        self.execute_mnemonic('SP + 1 -> AR, SP')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('BR * DR -> DR {NZVC}')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_div(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR -> BR')
        self.execute_mnemonic('SP + 1 -> AR, SP')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('BR / DR -> DR {NZVC}')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_and(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR -> BR')
        self.execute_mnemonic('SP + 1 -> AR, SP')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('BR & DR -> DR {NZ}')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_or(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR -> BR')
        self.execute_mnemonic('SP + 1 -> AR, SP')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('~BR & ~DR -> DR')
        self.execute_mnemonic('~DR -> DR {NZ}')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_not(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('~DR -> DR {NZ}')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_neg(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('~DR+1 -> DR {NZ}')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_shl(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('SHL(DR) -> DR')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_shr(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('SHR(DR) -> DR')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_rol(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('ROL(DR) -> DR')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_ror(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('ROR(DR) -> DR')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_cmp(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR -> BR')
        self.execute_mnemonic('SP + 1 -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('BR + ~DR+1 -> BR {NZVC}')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_ld(self):
        self.execute_mnemonic('SP -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('SP + ~0 -> AR, SP')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_st(self):
        self.execute_mnemonic('SP + 1 -> AR, SP')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR -> BR')
        self.execute_mnemonic('SP + ~0 -> AR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('BR -> AR')
        self.execute_mnemonic('DR -> MEM(AR)')

    # Non Addr instructions implementation

    def execute_push(self):
        self.execute_mnemonic('CUTB(CR) -> DR')
        self.execute_mnemonic('SP + ~0 -> SP, AR')
        self.execute_mnemonic('DR -> MEM(AR)')

    def execute_jmp(self):
        self.execute_mnemonic('CUTB(CR) -> PC')

    def execute_jz(self):
        if (self.registers.SR & 0x4) == 0:
            return
        self.execute_mnemonic('CUTB(CR) -> PC')

    def execute_je(self):
        if (self.registers.SR & 0x4) == 0:
            return
        self.execute_mnemonic('CUTB(CR) -> PC')

    def execute_jnz(self):
        if (self.registers.SR & 0x4) != 0:
            return
        self.execute_mnemonic('CUTB(CR) -> PC')

    def execute_jg(self):
        if (self.registers.SR & 0x8) != 0:
            return
        self.execute_mnemonic('CUTB(CR) -> PC')

    def execute_jge(self):
        if (self.registers.SR & 0x8) != 0 and (self.registers.SR & 0x4) == 0:
            return
        self.execute_mnemonic('CUTB(CR) -> PC')

    def execute_jl(self):
        if (self.registers.SR & 0x8) == 0:
            return
        self.execute_mnemonic('CUTB(CR) -> PC')

    def execute_jle(self):
        if (self.registers.SR & 0x8) == 0 and (self.registers.SR & 0x4) == 0:
            return
        self.execute_mnemonic('CUTB(CR) -> PC')

    def execute_call(self):
        self.execute_mnemonic('SP + ~0 -> SP, AR')
        self.execute_mnemonic('PC -> DR')
        self.execute_mnemonic('DR -> MEM(AR)')
        self.execute_mnemonic('CUTB(CR) -> PC')

    def execute_set(self):
        self.execute_push()
        self.execute_ld()
        self.execute_mnemonic('SP + ~0 -> SP, AR')
        self.execute_mnemonic('BR & ~BR -> BR')
        self.execute_mnemonic('BR + 1 -> DR')
        self.execute_mnemonic('DR -> MEM(AR)')
        self.execute_ror()
        self.execute_or()
        self.execute_st()
        self.execute_pop()

    def execute_unset(self):
        self.execute_push()
        self.execute_ld()
        self.execute_mnemonic('SP + ~0 -> SP, AR')
        self.execute_mnemonic('BR & ~BR -> BR')
        self.execute_mnemonic('BR + 1 -> DR')
        self.execute_mnemonic('DR -> MEM(AR)')
        self.execute_ror()
        self.execute_not()
        self.execute_and()
        self.execute_st()
        self.execute_pop()

    def execute_check(self):
        self.execute_push()
        self.execute_ld()
        self.execute_mnemonic('SP - 1 -> SP, AR')
        self.execute_mnemonic('0+1 -> DR')
        self.execute_mnemonic('DR -> MEM(AR)')
        self.execute_ror()
        self.execute_and()
        self.execute_pop()
        self.execute_pop()

    def inc_tick(self):
        self.tick += 1

    def inc_instruction(self):
        self.instruction += 1

    def check_stop_flag(self):
        return (self.registers.SR & 0x8000) != 0

    def fetch_instruction(self):
        self.execute_mnemonic('PC -> AR, BR')
        self.execute_mnemonic('MEM(AR) -> DR')
        self.execute_mnemonic('DR -> CR')
        self.execute_mnemonic('BR + 1 -> PC')

    def execute_instruction(self):
        opcode = self.registers.CR >> 24
        if opcode & 0x80 != 0:
            opcode &= 0b11111100
            self.execute_addr_instruction(opcode)
        else:
            self.execute_non_addr_instruction(opcode)

    def handle_devices(self):
        for device in self.io_devices:
            device.process()

    def process(self):
        self.fetch_instruction()
        self.execute_instruction()
        self.handle_devices()
        self.inc_instruction()

    def print_state(self):
        return (
            f'Tick: {self.tick} \t'
            f'| Instruction: {self.instruction}   '
            f'| {self.registers} '
            f'| TOS: '
            f'{self.memory.cells[self.registers.SP & 0xFFFFFF]:08X} '
            f'| NOS: '
            f'{self.memory.cells[(self.registers.SP + 1) & 0xFFFFFF]:08X}'
        )

    def run(self, instruction_delay):
        with open('sources.txt', 'w') as golden_file:
            self.registers.SR |= 0x8000
            while self.check_stop_flag():
                self.process()
                print(self.print_state())
                golden_file.write(self.print_state() + '\n')
                time.sleep(instruction_delay / 1000)
            print(
                f'Emulation finished in {self.tick} ticks '
                f'/ {self.instruction} instruction executions')
