import pytest

from src.emulator.emulator import main as emulator_main


@pytest.mark.timeout(5)
def test_hello_world():
    emulator_main('test/sources/hello_world.opc',
                  ['Hello, World!'])
    with open('sources.txt', 'r') as golden_file:
        output = golden_file.read()

    with open('out.txt', 'r') as golden_file:
        io = golden_file.read()

    with open('test/output/hello_world.txt', 'r') as test_file:
        output_expected = test_file.read()

    with open('test/io/hello_world.txt', 'r') as test_file:
        io_expected = test_file.read()

    assert output == output_expected and io == io_expected


@pytest.mark.timeout(5)
def test_hello_username():
    emulator_main('test/sources/hello_username.opc',
                  ['Amogus'])
    with open('sources.txt', 'r') as golden_file:
        output = golden_file.read()

    with open('out.txt', 'r') as golden_file:
        io = golden_file.read()

    with open('test/output/hello_username.txt', 'r') as test_file:
        output_expected = test_file.read()

    with open('test/io/hello_username.txt', 'r') as test_file:
        io_expected = test_file.read()

    assert output == output_expected and io == io_expected


@pytest.mark.timeout(5)
def test_cat():
    emulator_main('test/sources/cat.opc',
                  ['Hello, World!', 'I', 'love', 'CSA', 'Lab3'])
    with open('sources.txt', 'r') as golden_file:
        output = golden_file.read()

    with open('out.txt', 'r') as golden_file:
        io = golden_file.read()

    with open('test/output/cat.txt', 'r') as test_file:
        output_expected = test_file.read()

    with open('test/io/cat.txt', 'r') as test_file:
        io_expected = test_file.read()

    assert output == output_expected and io == io_expected


@pytest.mark.timeout(5)
def test_prob5():
    emulator_main('test/sources/prob5.opc')
    with open('sources.txt', 'r') as golden_file:
        output = golden_file.read()

    with open('out.txt', 'r') as golden_file:
        io = golden_file.read()

    with open('test/output/prob5.txt', 'r') as test_file:
        output_expected = test_file.read()

    with open('test/io/prob5.txt', 'r') as test_file:
        io_expected = test_file.read()

    assert output == output_expected and io == io_expected
