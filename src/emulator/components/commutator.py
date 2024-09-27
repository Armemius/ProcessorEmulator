from enum import Enum

class CommutatorFlags(Enum):
    NONE   = 0b0000000000
    LTOH   = 0b0000000001
    LTOL   = 0b0000000010
    HTOL   = 0b0000000100
    HTOH   = 0b0000001000
    CUTB   = 0b0000001111
    SHL    = 0b0000010000
    SHR    = 0b0000100000
    ROL    = 0b0000110000
    ROR    = 0b0001000000
    SET_NZ = 0b0010000000
    SET_V  = 0b0100000000
    SET_C  = 0b1000000000

def commutator_code (flags):
    res = 0
    for it in flags:
        res |= it.value
    return res

def process_commutator_code(data, opcode, flags, registers) -> int:
    res = 0

    if opcode & opcode & CommutatorFlags.LTOH.value != 0 \
        and opcode & opcode & CommutatorFlags.LTOL.value != 0 \
        and opcode & opcode & CommutatorFlags.HTOH.value != 0 \
        and opcode & opcode & CommutatorFlags.HTOL.value:
        res = data & 0x00FFFFFF
    else:
        # Bit mutations
        if opcode & CommutatorFlags.LTOH.value != 0:
            res |= (data & 0x0000FFFF) << 16
        if opcode & CommutatorFlags.LTOL.value != 0:
            res |= (data & 0x0000FFFF)
        if opcode & CommutatorFlags.HTOL.value != 0:
            res |= (data & 0xFFFF0000) >> 16
        if opcode & CommutatorFlags.HTOH.value != 0:
            res |= (data & 0xFFFF0000)

    # Bit shifts
    shift = (opcode >> 4) & 0b111
    if opcode & CommutatorFlags.SHL.value != 0:
        res = data << 1
    elif opcode & CommutatorFlags.SHR.value != 0:
        res = data >> 1
    elif opcode & CommutatorFlags.ROL.value != 0:
        res = (data << 1) | (data >> 31)
    elif opcode & CommutatorFlags.ROR.value != 0:
        res = (data >> 1) | (data << 31)

    # Flags
    if opcode & CommutatorFlags.SET_NZ.value != 0:
        registers.SR = (registers.SR & ~0b1100) | (flags & 0b1100)
    if opcode & CommutatorFlags.SET_V.value != 0:
        registers.SR = (registers.SR & ~0b0010) | (flags & 0b0010)
    if opcode & CommutatorFlags.SET_C.value != 0:
        registers.SR = (registers.SR & ~0b0001) | (flags & 0b0001)

    return res & 0xFFFFFFFF
