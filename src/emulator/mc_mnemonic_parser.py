import re

from src.emulator.components.commutator import alu_flags, commutator_code, \
    CommutatorFlags
from src.emulator.data_path import gen_mc_write, gen_mc_read, gen_mc, \
    registries as registries_codes, DataPathOperations, RegisterCodes
from src.emulator.components.alu import AluOperations, OperandOperation, \
    alu_code


def _check_rw_operations(mnemonic):
    match = re.match(r'\s*DR\s*->\s*MEM\s*\(\s*AR\)\s*', mnemonic)
    if match:
        return gen_mc_write()
    match = re.match(r'\s*MEM\s*\(\s*AR\)\s*->\s*DR\s*', mnemonic)
    if match:
        return gen_mc_read()
    return None


def _parse_lhs(lhs):
    match = re.match(r'^((?P<cmc>[A-Z]+\s*\(\s*(?P<clhs>0|(~?[A-Z]{2}'
                     r'(\s*\|\s*[A-Z]{2}\s*)*(\s*\+\s*1)?))\s*(?P<cop>[+*/&])?'
                     r'\s*(?P<crhs>(~?(([A-Z]{2}(\s*\|\s*[A-Z]{2}\s*)*)|0)(\s*'
                     r'\+\s*1)?))?\s*\))|(\s*(?P<lhs>0|(~?[A-Z]{2}(\s*\|\s*'
                     r'[A-Z]{2}\s*)*(\s*\+\s*1)?))\s*(?P<op>[+*/&])?\s*'
                     r'(?P<rhs>(~?(([A-Z]{2}(\s*\|\s*[A-Z]{2}\s*)*)|0)'
                     r'(\s*\+\s*1)?))?\s*))$', lhs)

    if match:
        if match.group('cmc'):
            lhs = match.group('clhs')
            op = match.group('cop')
            rhs = match.group('crhs')
        else:
            lhs = match.group('lhs')
            op = match.group('op')
            rhs = match.group('rhs')

        if op is None != rhs is None:
            raise ValueError(f"Invalid lhs syntax: {lhs}")

        def get_op(value):
            if value is None:
                return None, False, False
            not_op = False
            inc_op = False
            op_match = re.match(r'\s*~.*', value)
            if op_match:
                not_op = True
                value = re.sub(r'\s*~', '', value)
            op_match = re.match(r'.*?\+\s*1\s*', value)
            if op_match:
                inc_op = True
                value = re.sub(r'\+\s*1\s*', '', value)
            return (re.split(r'\s*\|\s*', value) if value else None,
                    not_op, inc_op)

        lhs, lhs_not, lhs_inc = get_op(lhs)
        rhs, rhs_not, rhs_inc = get_op(rhs)

        lhs_code = 0
        rhs_code = 0

        for registry in lhs:
            if registry == '0':
                continue
            if registry not in ['PC', 'SP', 'CR', 'AR', 'DR', 'SR', 'BR']:
                raise ValueError(f"Invalid registry: {registry}")
            lhs_code |= registries_codes[registry]
        lhs_operations = OperandOperation.NONE.value
        if lhs_not:
            lhs_operations |= OperandOperation.NOT.value
        if lhs_inc:
            lhs_operations |= OperandOperation.INC.value

        if rhs:
            for registry in rhs:
                if registry == '0':
                    continue
                if registry not in ['PC', 'SP', 'CR', 'AR', 'DR', 'SR', 'BR']:
                    raise ValueError(f"Invalid registry: {registry}")
                rhs_code |= registries_codes[registry]


            rhs_operations = OperandOperation.NONE.value

            if rhs_not:
                rhs_operations |= OperandOperation.NOT.value
            if rhs_inc:
                rhs_operations |= OperandOperation.INC.value

            if op is not None and op not in ['+', '*', '/', '&']:
                raise ValueError(f"Invalid operator: {op}")

            opcodes = {
                '+': AluOperations.ADD,
                '*': AluOperations.MUL,
                '/': AluOperations.DIV,
                '&': AluOperations.AND
            }

            return {
                'lhs': (lhs_code, lhs_operations),
                'rhs': (rhs_code, rhs_operations),
                'opcode': opcodes[op] if op else None
            }
        return {
            'lhs': (lhs_code, lhs_operations),
            'rhs': (RegisterCodes.NONE.value, OperandOperation.NONE.value),
            'opcode': AluOperations.ADD
        }

    else:
        raise ValueError(f"Invalid lhs syntax: {lhs}")


def _parse_rhs(rhs):
    match = re.match(r'^(null|(?P<registries>\S{2}(\s*,\s*\S{2})*)\s*'
                     r'(?P<flags>\{(NZ)?V?C?})?)$', rhs)
    if match:
        registries = match.group('registries')
        flags = match.group('flags')
        registries = re.split(r'\s*,\s*', registries)
        target_code = 0
        operation_flags = []
        for registry in registries:
            if registry not in ['PC', 'SP', 'CR', 'AR', 'DR', 'SR', 'BR']:
                raise ValueError(f"Invalid registry: {registry}")
            target_code |= registries_codes[registry]
        if flags:
            flags = re.sub(r'[{}]', '', flags)
            for flag in flags:
                if flag not in ['N', 'Z', 'V', 'C']:
                    raise ValueError(f"Invalid flag: {flag}")
                operation_flags += [alu_flags[flag]]
        return target_code, operation_flags
    else:
        raise ValueError(f"Invalid rhs syntax: {rhs}")


def parse_mnemonic(mnemonic):
    rw_operation = _check_rw_operations(mnemonic)
    if rw_operation:
        return rw_operation

    match = re.match(r'(.+?)\s*->\s*(.+)', mnemonic)
    if match:
        lhs, rhs = match.groups()
        source = _parse_lhs(lhs)
        target, flags = _parse_rhs(rhs)

        return gen_mc(DataPathOperations.NONE.value,
                      target=target,
                      lhs=source['lhs'][0],
                      rhs=source['rhs'][0],
                      alu_code=alu_code(source['opcode'],
                                        source['lhs'][1],
                                        source['rhs'][1]),
                      commutator_code=commutator_code(
                          [CommutatorFlags.LTOL, CommutatorFlags.HTOH] +
                          flags))

    else:
        raise ValueError(f"Invalid syntax: {mnemonic}")

