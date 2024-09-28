import pytest

from src.emulator.emulator import main as emulator_main


@pytest.mark.timeout(5)
def test_prob5():
    emulator_main('test/sources/prob5.opc')
    with open('sources.txt', 'r') as golden_file:
        output = golden_file.read()

    with open('test/output/prob5.txt', 'r') as test_file:
        expected = test_file.read()

    assert output == expected
