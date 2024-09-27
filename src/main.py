import argparse

from src.translator.translator import main as translator_main
from src.emulator.emulator import main as emulator_main

def main(source, output):
    translator_main(source, output)
    emulator_main(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSA Lab 3 assembly translator")
    parser.add_argument("-s", "--source", required=True, type=str, help="File with asm code")
    parser.add_argument("-o", "--output", required=True, type=str, help="File with output sources")
    args = parser.parse_args()
    main(args.source, args.output)
