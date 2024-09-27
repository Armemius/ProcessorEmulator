from src.translator.syntax_analyzer import SectionNode, LabelNode, \
    InstructionNode


class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.labels = set()
        self.current_section = 'text'

    def analyze(self):
        for statement in self.ast.statements:
            if isinstance(statement, LabelNode):
                self.check_label(statement)
        if 'start' not in self.labels:
            raise SemanticError(
                "No entry point found in provided file "
                "(label 'start' is missing)")

        for statement in self.ast.statements:
            if isinstance(statement, SectionNode):
                self.check_section(statement)
            elif isinstance(statement, InstructionNode):
                self.check_instruction(statement)
            elif isinstance(statement, LabelNode):
                continue
            else:
                raise SemanticError(
                    f"Unknown statement type: {type(statement)}")

    def check_section(self, section):
        if section.section_type not in ['text', 'data', 'devices']:
            raise SemanticError(
                f"Invalid section type: {section.section_type}")
        self.current_section = section.section_type

    def check_label(self, label):
        if label.identifier in self.labels:
            raise SemanticError(f"Duplicate label: {label.identifier}")
        self.labels.add(label.identifier)

    def check_instruction(self, instruction):
        if self.current_section is None:
            raise SemanticError("Instruction outside of any section")
        if (instruction.opcode not in ['byte', 'char', 'res',
                                      'str']
                and self.current_section == 'data'):
            raise SemanticError(
                f"Instruction {instruction.opcode} "
                f"is not allowed in data section")

        if (instruction.opcode not in ['byte',
                                      'addr']
                and self.current_section == 'devices'):
            raise SemanticError(
                f"Instruction {instruction.opcode} "
                f"is not allowed in devices section")

        if instruction.opcode in ['nop', 'pop', 'pushf', 'popf', 'inc', 'dec',
                                  'swap', 'dup', 'nop', 'ret', 'halt',
                                  'iret', 'ei', 'di', 'in', 'out', 'not',
                                  'neg', 'shl', 'shr', 'rol', 'ror', 'add',
                                  'sub', 'mul', 'div', 'and', 'or', 'xor',
                                  'ld', 'st', 'cmp']:
            if instruction.operands:
                raise SemanticError(
                    f"Instruction {instruction.opcode} "
                    f"does not take any operands")

        if instruction.opcode in ['push', 'call', 'int', 'jmp', 'call', 'jz',
                                  'je', 'jnz', 'jg', 'jge', 'jl', 'jle',
                                  'str']:
            if len(instruction.operands) != 1:
                raise SemanticError(
                    f"Instruction {instruction.opcode} "
                    f"takes exactly one operand")

        if instruction.opcode in ['jmp', 'call', 'jz', 'je', 'jnz', 'jg',
                                  'jge', 'jl', 'jle']:
            if instruction.operands[0] not in self.labels:
                raise SemanticError(
                    f"Label {instruction.operands[0]} not found")

        if instruction.opcode == 'byte':
            if len(instruction.operands) == 0:
                raise SemanticError(
                    "Instruction byte requires at least one operand")
            for operand in instruction.operands:
                if not isinstance(operand, int):
                    raise SemanticError(f"Operand {operand} is not a number")
                if operand < 0 or operand > 255:
                    raise SemanticError(
                        f"Operand {operand} is out of range for byte")

        if instruction.opcode == 'char':
            if len(instruction.operands) == 0:
                raise SemanticError(
                    "Instruction char requires at least one operand")
            for operand in instruction.operands:
                if not isinstance(operand, str):
                    raise SemanticError(f"Operand {operand} is not a string")
                if len(operand) != 1:
                    raise SemanticError(
                        f"Operand {operand} is not a character")

        if instruction.opcode == 'str':
            if len(instruction.operands) == 0:
                raise SemanticError(
                    "Instruction str requires at least one operand")
            for operand in instruction.operands:
                if not isinstance(operand, str):
                    raise SemanticError(f"Operand {operand} is not a string")
                for char in operand:
                    if ord(char) < 0 or ord(char) > 255:
                        raise SemanticError(
                            f"Character {char} is out of range for byte")

        if instruction.opcode == 'res':
            if len(instruction.operands) != 1:
                raise SemanticError(
                    "Instruction res requires exactly one operand")
            if not isinstance(instruction.operands[0], int):
                raise SemanticError(
                    f"Operand {instruction.operands[0]} is not a number")
            if instruction.operands[0] < 1:
                raise SemanticError(
                    f"Operand {instruction.operands[0]} "
                    f"should be greater than 0")

        if instruction.opcode == 'addr':
            if len(instruction.operands) != 1:
                raise SemanticError(
                    "Instruction res requires exactly one operand")
            if not isinstance(instruction.operands[0], str):
                raise SemanticError(
                    f"Operand {instruction.operands[0]} "
                    f"is not a label or null")

        if instruction.opcode in ['set', 'unset', 'check']:
            if len(instruction.operands) != 1:
                raise SemanticError(
                    f"Instruction {instruction.opcode} "
                    f"takes exactly one operand")
            if not isinstance(instruction.operands[0], str):
                raise SemanticError(
                    f"Operand {instruction.operands[0]} is not a label")
            if instruction.operands[0] not in ['dev0', 'dev1', 'dev2', 'dev3',
                                               'dev4', 'dev5', 'dev6', 'dev7',
                                               'dev8',
                                               'dev9', 'dev10', 'dev11',
                                               'dev12', 'dev13', 'dev14',
                                               'dev15']:
                raise SemanticError(
                    f"Label should point to device [dev0-dev15], "
                    f"got {instruction.operands[0]}")
