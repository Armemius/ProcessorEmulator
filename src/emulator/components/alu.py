from enum import Enum


class AluOperations(Enum):
    ADD = 0b00
    AND = 0b01
    MUL = 0b10
    DIV = 0b11


class OperandOperation(Enum):
    NONE = 0b00
    NOT = 0b01
    INC = 0b10


def alu_code(operation, op1, op2):
    return operation.value << 4 | op1 << 2 | op2


def process_alu_code(lhs, rhs, code):
    res = 0

    operation = (code >> 4) & 0b11
    lhs_op = (code >> 2) & 0b11
    rhs_op = code & 0b11

    lhs_val = lhs
    if lhs_op & OperandOperation.NOT.value != 0:
        lhs_val = ~lhs
    if lhs_op & OperandOperation.INC.value != 0:
        lhs_val += 1

    rhs_val = rhs
    if rhs_op & OperandOperation.NOT.value != 0:
        rhs_val = ~rhs
    if rhs_op & OperandOperation.INC.value != 0:
        rhs_val += 1

    flags = 0
    if operation == AluOperations.ADD.value:
        res = lhs_val + rhs_val
        if res > 0xFFFFFFFF:
            flags |= 0x1  # Carry
        if (lhs_val > 0 > res and rhs_val > 0) or (lhs_val < 0 < res and rhs_val < 0):
            flags |= 0x2  # Overflow
    elif operation == AluOperations.AND.value:
        res = lhs_val & rhs_val
    elif operation == AluOperations.MUL.value:
        res = lhs_val * rhs_val
        if res > 0xFFFFFFFF:
            flags |= 0x1  # Carry
    elif operation == AluOperations.DIV.value:
        res = lhs_val // rhs_val

    if res & 0x80000000 != 0:
        flags |= 0x8  # Negative
    if res == 0:
        flags |= 0x4  # Zero

    return res & 0xFFFFFFFF, flags
