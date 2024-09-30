from src.translator.syntax_analyzer import SectionNode, LabelNode, \
    InstructionNode


class MachineCodeGenerator:
    def __init__(self, syntax_tree):
        self.current_address = 0x1F
        self.label_addresses = {
            'dev0': 0x00,
            'dev1': 0x02,
            'dev2': 0x04,
            'dev3': 0x06,
            'dev4': 0x08,
            'dev5': 0x0A,
            'dev6': 0x0C,
            'dev7': 0x0E,
            'dev8': 0x10,
            'dev9': 0x12,
            'dev10': 0x14,
            'dev11': 0x16,
            'dev12': 0x18,
            'dev13': 0x1A,
            'dev14': 0x1C,
            'dev15': 0x1E
        }
        self.syntax_tree = syntax_tree
        self.machine_code = {}
        self.serialized_code = ""
        self.devices_section_present = False

    def check_address_for_label(self, address):
        res = ""
        for label, addr in self.label_addresses.items():
            if addr == address:
                if res != "":
                    res += ", "
                res = label
        return " <- " + res if res != "" else ""

    def generate(self):
        data_section_indices = []
        text_section_indices = []
        devices_section_index = -1
        for index, statement in enumerate(self.syntax_tree.statements):
            if isinstance(statement,
                          SectionNode) and statement.section_type == 'data':
                data_section_indices.append(index)
            elif isinstance(statement,
                            SectionNode) and statement.section_type == 'text':
                text_section_indices.append(index)
            elif (isinstance(statement,
                             SectionNode)
                  and statement.section_type == 'devices'):
                if self.devices_section_present:
                    raise Exception("Error: multiple devices sections")
                self.devices_section_present = True
                devices_section_index = index

        for index in data_section_indices:
            self.generate_data_section(index)

        self.current_address += 15
        text_section_start = self.current_address + 1
        for index in text_section_indices:
            self.calc_text_label_addresses(index)

        self.current_address = text_section_start
        for index in text_section_indices:
            self.generate_text_section(index)

        if devices_section_index >= 0:
            self.generate_devices_section(devices_section_index)

        entry_addr = self.label_addresses.get('start')
        self.serialized_code = "".join(
            f"{k:06x} {'>' if k == entry_addr else ':'} {v:08x} "
            f"{self.check_address_for_label(k)} \n"
            for k, v in
            sorted(self.machine_code.items()))

        return self.serialized_code

    def generate_data_section(self, start_index):
        it = start_index + 1
        cell_pos = 0
        while it < len(self.syntax_tree.statements) and not isinstance(
                self.syntax_tree.statements[it], SectionNode):
            statement = self.syntax_tree.statements[it]
            if isinstance(statement, LabelNode):
                if it > 0 and not isinstance(
                        self.syntax_tree.statements[it - 1], LabelNode):
                    self.current_address += 1
                cell_pos = 0
                if statement.identifier == "start":
                    raise Exception(
                        "Error: 'start' label should be "
                        "located in text section")
                self.label_addresses[
                    statement.identifier] = self.current_address
            elif isinstance(statement, InstructionNode):
                if statement.opcode == 'byte':
                    for operand in statement.operands:
                        if self.current_address not in self.machine_code:
                            self.machine_code[self.current_address] = 0
                        self.machine_code[self.current_address] |= operand << (
                                32 - (cell_pos + 1) * 8)
                        cell_pos += 1
                        if cell_pos >= 4:
                            self.current_address += 1
                            cell_pos = 0
                elif statement.opcode == 'char':
                    for operand in statement.operands:
                        if self.current_address not in self.machine_code:
                            self.machine_code[self.current_address] = 0
                        self.machine_code[self.current_address] |= ord(
                            operand) << (32 - (cell_pos + 1) * 8)
                        cell_pos += 1
                        if cell_pos >= 4:
                            self.current_address += 1
                            cell_pos = 0
                elif statement.opcode == 'res':
                    reserved = int(statement.operands[0])
                    while reserved > 0:
                        if self.current_address not in self.machine_code:
                            self.machine_code[self.current_address] = 0
                        self.current_address += 1
                        reserved -= 4
                elif statement.opcode == 'str':
                    for operand in statement.operands:
                        for char in operand:
                            if self.current_address not in self.machine_code:
                                self.machine_code[self.current_address] = 0
                            self.machine_code[self.current_address] |= ord(
                                char) << (32 - (cell_pos + 1) * 8)
                            cell_pos += 1
                            if cell_pos >= 4:
                                self.current_address += 1
                                cell_pos = 0
            it += 1

    def calc_text_label_addresses(self, index):
        it = index + 1
        while it < len(self.syntax_tree.statements) and not isinstance(
                self.syntax_tree.statements[it], SectionNode):
            if it > 0 and not isinstance(self.syntax_tree.statements[it - 1],
                                         LabelNode):
                self.current_address += 1
            if isinstance(self.syntax_tree.statements[it], LabelNode):
                self.label_addresses[self.syntax_tree.statements[
                    it].identifier] = self.current_address
                self.machine_code[self.current_address] = 0
            it += 1

        pass

    def generate_text_section(self, index):
        it = index + 1
        while it < len(self.syntax_tree.statements) and not isinstance(
                self.syntax_tree.statements[it], SectionNode):
            statement = self.syntax_tree.statements[it]
            if isinstance(statement, InstructionNode):
                self.machine_code[
                    self.current_address] = self.generate_instruction(
                    statement)
                self.current_address += 1
            it += 1

    def generate_instruction(self, node):
        opcode = self.get_opcode(node.opcode)

        addr_mode = 0b00
        value = 0

        if node.opcode in ['call', 'jmp', 'jz', 'je', 'jnz', 'jg', 'jge', 'jl',
                           'jle', 'set', 'unset', 'check']:
            addr_mode = 0b00
            value = self.label_addresses[node.operands[0]]

        if node.opcode == 'push':
            if isinstance(node.operands[0], str):
                addr_mode = 0b00
                if node.operands[0] not in self.label_addresses:
                    raise Exception(
                        f"Error: label '{node.operands[0]}' not found")
                value = self.label_addresses[node.operands[0]]
            elif isinstance(node.operands[0], int):
                addr_mode = 0b10
                value = node.operands[0]

        if node.opcode == 'int':
            addr_mode = 0b00
            value = int(node.operands[0])

        value &= 0x00FFFFFF
        return ((opcode | addr_mode) << 24) | value

    def generate_devices_section(self, start_index):
        devices = ['dev0', 'dev1', 'dev2', 'dev3', 'dev4', 'dev5', 'dev6',
                   'dev7', 'dev8', 'dev9', 'dev10', 'dev11',
                   'dev12', 'dev13', 'dev14', 'dev15']
        initialized_devices = []
        it = start_index + 1
        while it < len(self.syntax_tree.statements) and not isinstance(
                self.syntax_tree.statements[it], SectionNode):
            statement = self.syntax_tree.statements[it]
            if isinstance(statement, LabelNode):
                if statement.identifier in initialized_devices:
                    raise Exception("Error: device already initialized")
                if statement.identifier in devices:
                    initialized_devices.append(statement.identifier)
                    dev_id = devices.index(statement.identifier)

                    buffer = 0x0

                    it += 1
                    statement = self.syntax_tree.statements[it]

                    if statement.opcode == 'byte':
                        if len(statement.operands) != 1:
                            raise Exception(
                                "Error: invalid device initialization, "
                                "flags should be stored in 1 byte")
                        flags = statement.operands[0]
                        it += 1
                        statement = self.syntax_tree.statements[it]
                    else:
                        raise Exception(
                            "Error: invalid device initialization, "
                            "no device flags found")

                    if statement.opcode == 'addr':
                        if len(statement.operands) != 1:
                            raise Exception(
                                "Error: invalid device initialization, "
                                "handler address should be stored in 4 bytes")
                        handler = 0 if statement.operands[0] == 'null' else \
                            self.label_addresses[statement.operands[0]]
                        it += 1
                        statement = self.syntax_tree.statements[it]
                    else:
                        raise Exception(
                            "Error: invalid device initialization, "
                            "no device handler found")

                    if statement.opcode == 'byte':
                        if len(statement.operands) != 1:
                            raise Exception(
                                "Error: invalid device initialization, "
                                "buffer size should be stored in 1 byte")
                        buffer_size = statement.operands[0]
                        it += 1
                        statement = self.syntax_tree.statements[it]
                    else:
                        raise Exception(
                            "Error: invalid device initialization, "
                            "no buffer size found")

                    if statement.opcode == 'addr':
                        if len(statement.operands) != 1:
                            raise Exception(
                                "Error: invalid device initialization, "
                                "buffer address should be stored in 4 bytes")
                        buffer = 0 if statement.operands[0] == 'null' else \
                            self.label_addresses[statement.operands[0]]
                        if buffer == 0:
                            raise Exception(
                                "Error: invalid device initialization, "
                                "buffer address should not be null")

                    print(
                        f"Device {dev_id} initialized with flags {flags}, "
                        f"handler {handler}, buffer size {buffer_size}, "
                        f"buffer {buffer}")

                    self.machine_code[dev_id * 2] = (flags << 24) | handler
                    self.machine_code[dev_id * 2 + 1] = ((buffer_size << 24)
                                                         | buffer)

                    self.label_addresses[
                        f'device #{dev_id} initialization'] = dev_id * 2

                else:
                    raise Exception(
                        f"Error: invalid device name '{statement.identifier}'")
            it += 1

    @staticmethod
    def get_opcode(mnemonic):
        opcode_map = {
            'push': 0xA4,
            'pop': 0x02,
            'pushf': 0x03,
            'popf': 0x04,
            'inc': 0x05,
            'dec': 0x06,
            'swap': 0x07,
            'dup': 0x08,
            'nop': 0x00,
            'call': 0xA0,
            'ret': 0x09,
            'halt': 0x0A,
            'int': 0x0B,
            'iret': 0x0C,
            'ei': 0x0D,
            'di': 0x0E,
            'add': 0x11,
            'sub': 0x12,
            'mul': 0x13,
            'div': 0x14,
            'and': 0x15,
            'or': 0x16,
            'xor': 0x17,
            'not': 0x18,
            'neg': 0x19,
            'shl': 0x1A,
            'shr': 0x1B,
            'rol': 0x1C,
            'ror': 0x1D,
            'ld': 0x28,
            'st': 0x29,
            'cmp': 0x1E,
            'jmp': 0x80,
            'jz': 0x84,
            'je': 0x88,
            'jnz': 0x8C,
            'jg': 0x90,
            'jge': 0x94,
            'jl': 0x98,
            'jle': 0x9C,
            'set': 0xF0,
            'unset': 0xF4,
            'check': 0xFC,
        }
        return opcode_map.get(mnemonic, 0x00)
