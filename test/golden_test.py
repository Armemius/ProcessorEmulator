import pytest
from src.emulator.emulator import main as emulator_main

def test_prob5():
    emulator_main("test/sources/prob5.opc")
    with open('states.txt', 'r') as golden_file:
       output = golden_file.read().strip()

    with open('test/output/prob5.txt', 'r') as test_file:
       expected = test_file.read().strip()

    assert expected == output
