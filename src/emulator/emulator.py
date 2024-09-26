import argparse

from src.emulator.components.memory import Memory
from src.emulator.components.registers import Registry
from src.emulator.control_unit import ControlUnit
from src.emulator.data_path import DataPath


def main():
    parser = argparse.ArgumentParser(description="CSA Lab 3 emulator")
    parser.add_argument("-s", "--source", required=True, type=str, help="File with operation codes")
    args = parser.parse_args()

    with open(args.source, 'r', encoding='utf-8') as file:
        operation_codes = file.read()

    print('Emulator started...')

    registry = Registry()
    memory = Memory(registry)
    memory.load(operation_codes)
    data_path = DataPath(memory, registry, None)
    control_unit = ControlUnit(registry, memory, data_path)

    control_unit.run(50)

if __name__ == "__main__":
    main()