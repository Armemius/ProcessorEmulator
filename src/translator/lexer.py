import re

# Define token specifications
token_specification = [
    ('NUMBER', r'0x[0-9A-Fa-f]+|0b[01]+|\d+'),  # Hex, binary, or decimal number
    ('CHAR', r"'[^']'"),  # Character
    ('STRING', r'"[^"]*"'),  # String
    ('NULLPTR', r'null'),  # Null pointer
    ('LABEL', r'[a-zA-Z_][a-zA-Z0-9_]*:'),  # Label
    ('SECTION', r'.section\s+(text|data|devices)'),  # Section
    ('COMMENT', r';[^\n]*'),  # Comment
    ('OPCODE',
     r'(?i)(pushf|popf|push|str|pop|inc|dec|swap|dup|nop|jmp|call|ret|halt|int|iret|ei|di|in|out|add|sub|mul|div|and|or|xor|not|neg|ld|st|cmp|jz|je|jnz|jg|jge|jl|jle|res|byte|char|shl|shr|rol|ror|addr|set|unset|check)[^a-zA-Z0-9_]'),
    # Opcode
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Identifier
    ('COMMA', r','),  # Comma
    ('NEWLINE', r'\n'),  # Line endings
    ('SKIP', r'[ \t]+'),  # Skip over spaces and tabs
    ('MISMATCH', r'.'),  # Any other character
]

# Compile the regular expressions
token_re = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
get_token = re.compile(token_re).match


def process_value(kind, value):
    if kind == 'NUMBER':
        if value.startswith('0x'):
            return int(value, 16)
        elif value.startswith('0b'):
            return int(value, 2)
        else:
            return int(value)
    if kind == 'CHAR':
        return str(value[1])
    if kind == 'STRING':
        return value[1:-1].encode().decode('unicode_escape')
    if kind == 'LABEL' or kind == 'OPCODE':
        return value[:-1]
    if kind == 'SECTION':
        return value.split()[1]
    return value.lower()


# Lexer function
def lex(code):
    line_num = 1
    mo = get_token(code)
    while mo is not None:
        kind = mo.lastgroup
        value = mo.group(kind)
        if kind == 'NEWLINE':
            line_num += 1
        elif kind == 'SKIP' or kind == 'COMMENT':
            pass
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected on line {line_num}')
        else:
            yield kind, process_value(kind, value), line_num
        mo = get_token(code, mo.end())
