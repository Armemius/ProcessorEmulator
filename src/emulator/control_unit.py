import time
from enum import Enum

from src.emulator.components.alu import alu_code, AluOperations, \
    OperandOperation
from src.emulator.components.commutator import commutator_code, CommutatorFlags
from src.emulator.data_path import DataPathOperations, RegisterCodes, \
    gen_mc, gen_mc_read, gen_mc_write


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
        # SP + 1 -> SP
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.SP.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()

    def execute_pushf(self):
        # SP - 1 -> SP, AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.SP.value | RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # SR -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.SR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())
        self.inc_tick()

    def execute_inc(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR + 1 -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())
        self.inc_tick()

    def execute_dec(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR + ~0 -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())
        self.inc_tick()

    def execute_swap(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR -> BR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.BR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # SP + 1 -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())
        # BR -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # SP + 1 -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_popf(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR -> SR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.SR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # SP + 1 -> SP
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.SP.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()

    def execute_dup(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # SP - 1 -> SP, AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.SP.value | RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())
        self.inc_tick()

    def execute_ret(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR -> PC
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.PC.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # SP + 1 -> SP
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.SP.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )

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
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR -> BR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.BR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # SP + 1 -> AR, SP
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value | RegisterCodes.SP.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        # BR + DR -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.DR.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_sub(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR -> BR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.BR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # SP + 1 -> AR, SP
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value | RegisterCodes.SP.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        # BR + ~DR+1 -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.DR.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value
                                     | OperandOperation.INC.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_mul(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR -> BR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.BR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # SP + 1 -> AR, SP
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value | RegisterCodes.SP.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        # BR * DR -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.DR.value,
                   alu_code=alu_code(AluOperations.MUL,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_div(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR -> BR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.BR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # SP + 1 -> AR, SP
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value | RegisterCodes.SP.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        # BR / DR -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.DR.value,
                   alu_code=alu_code(AluOperations.DIV,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_and(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR -> BR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.BR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # SP + 1 -> AR, SP
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value | RegisterCodes.SP.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        # BR & DR -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.DR.value,
                   alu_code=alu_code(AluOperations.AND,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_or(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR -> BR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.BR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # SP + 1 -> AR, SP
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value | RegisterCodes.SP.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        # ~BR & ~DR -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.DR.value,
                   alu_code=alu_code(AluOperations.AND,
                                     OperandOperation.NOT.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )
        # ~DR -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NOT.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )

        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_not(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # ~DR -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NOT.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_neg(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # ~DR+1 -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NOT.value
                                     | OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_shl(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # SHL(DR) -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SHL]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_shr(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # SHL(DR) -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SHR]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_rol(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # SHL(DR) -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.ROL]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_ror(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # SHL(DR) -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.ROR]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_cmp(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR -> BR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.BR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # SP + 1 -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        # BR + ~DR+1 -> NULL
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.NONE.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.DR.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value
                                     | OperandOperation.INC.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.SET_C,
                        CommutatorFlags.SET_NZ, CommutatorFlags.SET_V]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())

    def execute_ld(self):
        # SP -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()

        # SP - 1 -> AR, SP
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value | RegisterCodes.SP.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )

        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())
        self.inc_tick()

    def execute_st(self):
        # SP + 1 -> AR, SP
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value | RegisterCodes.SP.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR -> BR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.BR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # SP - 1 -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # BR -> AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())
        self.inc_tick()

    # Non Addr instructions implementation

    def execute_push(self):
        # CUTB(CR) -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.CR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.CUTB]))
        )
        # SP - 1 -> SP, AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.SP.value | RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()

        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())
        self.inc_tick()

    def execute_jmp(self):
        # CUTB(CR) -> PC
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.PC.value,
                   lhs=RegisterCodes.CR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.CUTB]))
        )
        self.inc_tick()

    def execute_jz(self):
        if (self.registers.SR & 0x4) == 0:
            return
        # CUTB(CR) -> PC
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.PC.value,
                   lhs=RegisterCodes.CR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.CUTB]))
        )
        self.inc_tick()

    def execute_je(self):
        if (self.registers.SR & 0x4) == 0:
            return
        # CUTB(CR) -> PC
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.PC.value,
                   lhs=RegisterCodes.CR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.CUTB]))
        )
        self.inc_tick()

    def execute_jnz(self):
        if (self.registers.SR & 0x4) != 0:
            return
        # CUTB(CR) -> PC
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.PC.value,
                   lhs=RegisterCodes.CR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.CUTB]))
        )
        self.inc_tick()

    def execute_jg(self):
        if (self.registers.SR & 0x8) != 0:
            return
        # CUTB(CR) -> PC
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.PC.value,
                   lhs=RegisterCodes.CR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.CUTB]))
        )
        self.inc_tick()

    def execute_jge(self):
        if (self.registers.SR & 0x8) != 0 and (self.registers.SR & 0x4) == 0:
            return
        # CUTB(CR) -> PC
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.PC.value,
                   lhs=RegisterCodes.CR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.CUTB]))
        )
        self.inc_tick()

    def execute_jl(self):
        if (self.registers.SR & 0x8) == 0:
            return
        # CUTB(CR) -> PC
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.PC.value,
                   lhs=RegisterCodes.CR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.CUTB]))
        )
        self.inc_tick()

    def execute_jle(self):
        if (self.registers.SR & 0x8) == 0 and (self.registers.SR & 0x4) == 0:
            return
        # CUTB(CR) -> PC
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.PC.value,
                   lhs=RegisterCodes.CR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.CUTB]))
        )
        self.inc_tick()

    def execute_call(self):
        # SP - 1 -> SP, AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.SP.value | RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # PC -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.PC.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.CUTB]))
        )
        self.inc_tick()
        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())
        self.inc_tick()

        # CUTB(CR) -> PC
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.PC.value,
                   lhs=RegisterCodes.CR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH,
                        CommutatorFlags.CUTB]))
        )
        self.inc_tick()

    def execute_set(self):
        self.execute_push()
        self.execute_ld()
        # SP - 1 -> SP, AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.SP.value | RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # BR & ~BR -> BR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.BR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.BR.value,
                   alu_code=alu_code(AluOperations.AND,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # BR + 1 -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()

        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())
        self.inc_tick()

        self.execute_ror()
        self.execute_or()
        self.execute_st()
        self.execute_pop()

    def execute_unset(self):
        self.execute_push()
        self.execute_ld()
        # SP - 1 -> SP, AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.SP.value | RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # BR & ~BR -> BR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.BR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.BR.value,
                   alu_code=alu_code(AluOperations.AND,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # BR + 1 -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()

        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())
        self.inc_tick()

        self.execute_ror()
        self.execute_not()
        self.execute_and()
        self.execute_st()
        self.execute_pop()

    def execute_check(self):
        self.execute_push()
        self.execute_ld()
        # SP - 1 -> SP, AR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.SP.value | RegisterCodes.AR.value,
                   lhs=RegisterCodes.SP.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # BR & ~BR -> BR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.BR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.BR.value,
                   alu_code=alu_code(AluOperations.AND,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NOT.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        # BR + 1 -> DR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.DR.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()

        # DR -> MEM(AR)
        self.data_path.execute(gen_mc_write())
        self.inc_tick()

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
        # PC -> AR, BR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.AR.value | RegisterCodes.BR.value,
                   lhs=RegisterCodes.PC.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # MEM(AR) -> DR
        self.data_path.execute(gen_mc_read())
        self.inc_tick()
        # DR -> CR
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.CR.value,
                   lhs=RegisterCodes.DR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.NONE.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()
        # BR + 1 -> PC
        self.data_path.execute(
            gen_mc(DataPathOperations.NONE.value,
                   target=RegisterCodes.PC.value,
                   lhs=RegisterCodes.BR.value,
                   rhs=RegisterCodes.NONE.value,
                   alu_code=alu_code(AluOperations.ADD,
                                     OperandOperation.INC.value,
                                     OperandOperation.NONE.value),
                   commutator_code=commutator_code(
                       [CommutatorFlags.LTOL, CommutatorFlags.HTOH]))
        )
        self.inc_tick()

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
        with open('states.txt', 'w') as golden_file:
            self.registers.SR |= 0x8000
            while self.check_stop_flag():
                self.process()
                golden_file.write(self.print_state() + '\n')
                time.sleep(instruction_delay / 1000)
            print(
                f'Emulation finished in {self.tick} ticks '
                f'/ {self.instruction} instruction executions')
