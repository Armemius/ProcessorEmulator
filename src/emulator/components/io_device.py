class IODevice:
    def __init__(self, dev_id, registers, memory):
        self.init_vector_addr = dev_id * 2
        self.registers = registers
        self.memory = memory

    def get_buffer(self):
        buffer = self.memory.cells[self.init_vector_addr + 1]
        size, addr = (buffer & 0xFF000000) >> 24, buffer & 0x00FFFFFF
        return size, addr

    def check_status(self):
        status = self.memory.cells[self.init_vector_addr]
        return status & 0x80000000

    def set_ready(self):
        self.memory.cells[self.init_vector_addr] |= 0x80000000

    def unset_ready(self):
        self.memory.cells[self.init_vector_addr] &= 0x7FFFFFFF

    def process(self):
        pass


# Writes data into a memory buffer
class InputDevice(IODevice):
    def __init__(self, dev_id, registers, memory, input_data):
        self.it = 0
        self.input_data = input_data
        super().__init__(dev_id, registers, memory)

    def process(self):
        # Data is not read by the processor yet
        if self.check_status():
            return

        # If there is no data ro read skip
        if self.it >= len(self.input_data):
            return

        size, addr = self.get_buffer()
        bytes_written = 0
        while self.it < size and bytes_written < len(self.input_data[self.it]):
            data = ord(self.input_data[self.it][bytes_written])
            self.memory.cells[addr + bytes_written // 4] &= ~(
                        0xFF000000 >> 8 * (bytes_written % 4))
            self.memory.cells[addr + bytes_written // 4] |= data << (
                    8 * (4 - bytes_written % 4 - 1))
            bytes_written += 1
        while bytes_written < size:
            self.memory.cells[addr + bytes_written // 4] &= ~(
                    0xFF000000 >> 8 * (bytes_written % 4))
            bytes_written += 1

        with open('out.txt', 'a') as file:
            file.write(f"< {self.input_data[self.it][:bytes_written]}\n")
        self.it += 1
        self.set_ready()


class Printer:
    def convert_data(self, data):
        pass


class OutputHandler:
    def output(self, data):
        pass


class OutputDevice(IODevice, OutputHandler, Printer):
    def __init__(self, dev_id, registers, memory):
        super().__init__(dev_id, registers, memory)

    def process(self):
        # Data is not written by the processor yet
        if not self.check_status():
            return

        size, addr = self.get_buffer()
        data = []
        bytes_read = 0
        while bytes_read < size:
            data.append((self.memory.cells[addr + bytes_read // 4] >> (
                    8 * (4 - bytes_read % 4 - 1))) & 0xFF)
            bytes_read += 1

        self.output(self.convert_data(data))
        self.unset_ready()


# Converts data from memory buffer to a string

class StringPrinter(Printer):
    def convert_data(self, data):
        res = ''.join(map(chr, data))
        if res.find('\0') != -1:
            return res[:res.find('\0')]
        return res


class IntPrinter(Printer):
    def convert_data(self, data):
        return int.from_bytes(data, 'big', signed=True)


class UIntPrinter(Printer):
    def convert_data(self, data):
        return int.from_bytes(data, 'big', signed=False)


class HexPrinter(Printer):
    def convert_data(self, data):
        return ''.join(map(lambda x: f'{x:02X}', data))


# Method to output data

class ConsolePrinter(OutputHandler):
    def output(self, data):
        print("Output:", data)
        with open('out.txt', 'a') as file:
            file.write(f"> {data}\n")


class FilePrinter(OutputHandler):
    def output(self, data):
        with open('out.txt', 'a') as file:
            file.write(f"> {data}\n")


# Output devices

class StringConsoleOutputDevice(OutputDevice, StringPrinter, ConsolePrinter):
    def __init__(self, dev_id, registers, memory):
        super().__init__(dev_id, registers, memory)


class IntConsoleOutputDevice(OutputDevice, IntPrinter, ConsolePrinter):
    def __init__(self, dev_id, registers, memory):
        super().__init__(dev_id, registers, memory)


class UIntConsoleOutputDevice(OutputDevice, UIntPrinter, ConsolePrinter):
    def __init__(self, dev_id, registers, memory):
        super().__init__(dev_id, registers, memory)


class HexConsoleOutputDevice(OutputDevice, HexPrinter, ConsolePrinter):
    def __init__(self, dev_id, registers, memory):
        super().__init__(dev_id, registers, memory)


class StringFileOutputDevice(OutputDevice, StringPrinter, FilePrinter):
    def __init__(self, dev_id, registers, memory):
        super().__init__(dev_id, registers, memory)


class IntFileOutputDevice(OutputDevice, IntPrinter, FilePrinter):
    def __init__(self, dev_id, registers, memory):
        super().__init__(dev_id, registers, memory)


class UIntFileOutputDevice(OutputDevice, UIntPrinter, FilePrinter):
    def __init__(self, dev_id, registers, memory):
        super().__init__(dev_id, registers, memory)


class HexFileOutputDevice(OutputDevice, HexPrinter, FilePrinter):
    def __init__(self, dev_id, registers, memory):
        super().__init__(dev_id, registers, memory)
