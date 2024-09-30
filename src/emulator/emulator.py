import argparse

from src.emulator.components.io_device import InputDevice, \
    StringConsoleOutputDevice, IntConsoleOutputDevice, \
    UIntConsoleOutputDevice, HexConsoleOutputDevice, StringFileOutputDevice, \
    IntFileOutputDevice, UIntFileOutputDevice, \
    HexFileOutputDevice
from src.emulator.components.memory import Memory
from src.emulator.components.registers import Registry
from src.emulator.control_unit import ControlUnit
from src.emulator.data_path import DataPath


def main(opcodes, input_queue=None):
    with open(opcodes, 'r', encoding='utf-8') as file:
        operation_codes = file.read()

    with open('out.txt', 'w') as file:
        file.truncate(0)

    print('Emulator started...')

    registry = Registry()
    memory = Memory(registry)
    memory.load(operation_codes)
    data_path = DataPath(memory, registry, None)

    input_data = ['Amogus', 'I', 'love', 'CSA', 'Lab3']

    if input_queue is not None:
        input_data = input_queue

    io_devices = [
        InputDevice(0, registry, memory, input_data),
        StringConsoleOutputDevice(1, registry, memory),
        IntConsoleOutputDevice(2, registry, memory),
        UIntConsoleOutputDevice(3, registry, memory),
        HexConsoleOutputDevice(4, registry, memory),
        StringFileOutputDevice(5, registry, memory),
        IntFileOutputDevice(6, registry, memory),
        UIntFileOutputDevice(7, registry, memory),
        HexFileOutputDevice(8, registry, memory)
    ]

    control_unit = ControlUnit(registry, memory, data_path, io_devices)

    control_unit.run(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSA Lab 3 emulator")
    parser.add_argument("-o", "--sources", required=True,
                        type=str, help="File with operation codes")
    args = parser.parse_args()
    main(args.opcodes)
