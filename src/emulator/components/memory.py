import re


def parse_line(line):
    match = re.match(r'([0-9a-fA-F]{6})\s*([:>])\s*([0-9a-fA-F]{8})\s*(<-.*)?', line)
    if match:
        address = match.group(1)
        separator = match.group(2)
        value = match.group(3)
        comment = match.group(4).strip() if match.group(4) else ''
        return address, separator, value, comment
    else:
        raise ValueError(f'Invalid line in operation codes: {line}')


class Memory:
    def __init__(self, registry):
        self.size = 0x1000000
        self.cells = [0] * self.size
        self.registry = registry

    def read(self):
        self.registry.DR = self.cells[self.registry.AR & 0xFFFFFF]

    def write(self):
        self.cells[self.registry.AR & 0xFFFFFF] = self.registry.DR

    def load(self, data):
        # Handle CRLF, CR, LF line endings
        for line in data.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
            if line == '':
                continue
            parsed_line = parse_line(line)
            if parsed_line:
                address, separator, value, comment = parsed_line

                if separator == '>' or separator == '+':
                    self.registry.PC = int(address, 16)
                    print('Entry point set to', hex(self.registry.PC))

                self.cells[int(address, 16)] = int(value, 16)
