from enum import Enum

from src.emulator.components.alu import process_alu_code
from src.emulator.components.commutator import process_commutator_code


class DataPathOperations(Enum):
    NONE = 0b000
    READ = 0b001
    WRITE = 0b010
    DEV_FLAGS = 0b100


class RegisterCodes(Enum):
    NONE = 0b0000000
    PC = 0b0000001
    SP = 0b0000010
    CR = 0b0000100
    AR = 0b0001000
    DR = 0b0010000
    SR = 0b0100000
    BR = 0b1000000


registries = {
    'null': RegisterCodes.PC.value,
    'PC': RegisterCodes.PC.value,
    'SP': RegisterCodes.SP.value,
    'CR': RegisterCodes.CR.value,
    'AR': RegisterCodes.AR.value,
    'DR': RegisterCodes.DR.value,
    'SR': RegisterCodes.SR.value,
    'BR': RegisterCodes.BR.value
}


def gen_mc(op, target, lhs, rhs, alu_code, commutator_code):
    return (op << 37 | target << 30 | lhs << 23
            | rhs << 16 | alu_code << 10 | commutator_code)


def gen_mc_read():
    return gen_mc(DataPathOperations.READ.value, RegisterCodes.NONE.value,
                  RegisterCodes.NONE.value,
                  RegisterCodes.NONE.value, 0, 0)


def gen_mc_write():
    return gen_mc(DataPathOperations.WRITE.value, RegisterCodes.NONE.value,
                  RegisterCodes.NONE.value,
                  RegisterCodes.NONE.value, 0, 0)


def gen_io_read(device):
    return ((
                    DataPathOperations.READ
                    | DataPathOperations.DEV_FLAGS) << 30) | device


def gen_io_write(device):
    return ((
                    DataPathOperations.READ
                    | DataPathOperations.DEV_FLAGS) << 30) | device


class DataPath:
    def __init__(self, memory, registry, devices):
        self.registry = registry
        self.memory = memory

    def io_read(self, device):
        pass

    def io_write(self, device):
        pass

    def execute(self, code):
        op = (code >> 37) & 0b111
        if (op & DataPathOperations.READ.value != 0
                and op & DataPathOperations.DEV_FLAGS.value != 0):
            self.memory.io_read(op & 0xFF)
            return
        if (op & DataPathOperations.WRITE.value != 0
                and op & DataPathOperations.DEV_FLAGS.value != 0):
            self.memory.io_write(op & 0xFF)
            return
        if op & DataPathOperations.READ.value != 0:
            self.memory.read()
            return
        if op & DataPathOperations.WRITE.value != 0:
            self.memory.write()
            return

        target = (code >> 30) & 0b1111111
        lhs_code = (code >> 23) & 0b1111111
        rhs_code = (code >> 16) & 0b1111111

        def get_value(registers):
            val = 0
            if registers & RegisterCodes.PC.value != 0:
                val |= self.registry.PC
            if registers & RegisterCodes.SP.value != 0:
                val |= self.registry.SP
            if registers & RegisterCodes.CR.value != 0:
                val |= self.registry.CR
            if registers & RegisterCodes.AR.value != 0:
                val |= self.registry.AR
            if registers & RegisterCodes.DR.value != 0:
                val |= self.registry.DR
            if registers & RegisterCodes.SR.value != 0:
                val |= self.registry.SR
            if registers & RegisterCodes.BR.value != 0:
                val |= self.registry.BR
            return val

        lhs = get_value(lhs_code)
        rhs = get_value(rhs_code)

        alu_code = (code >> 10) & 0b111111
        commutator_code = code & 0b1111111111

        res, flags = process_alu_code(lhs, rhs, alu_code)
        res = process_commutator_code(res, commutator_code, flags,
                                      self.registry)

        if target & RegisterCodes.PC.value != 0:
            self.registry.PC = res
        if target & RegisterCodes.SP.value != 0:
            self.registry.SP = res
        if target & RegisterCodes.CR.value != 0:
            self.registry.CR = res
        if target & RegisterCodes.AR.value != 0:
            self.registry.AR = res
        if target & RegisterCodes.DR.value != 0:
            self.registry.DR = res
        if target & RegisterCodes.SR.value != 0:
            self.registry.SR = res
        if target & RegisterCodes.BR.value != 0:
            self.registry.BR = res
