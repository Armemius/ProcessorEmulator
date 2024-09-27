import argparse
import src.translator.lexer as lexer
import src.translator.syntax_analyzer as astparser
import src.translator.semantic_analyzer as semparser
import src.translator.generator as generator

def main(source, output):
    with open(source, 'r', encoding='utf-8') as file:
        assembly_file = file.read()

    tokens = list(lexer.lex(assembly_file))
    syntax_parser = astparser.SyntaxAnalyzer(tokens)
    syntax_tree = syntax_parser.parse()
    semantic_analyzer = semparser.SemanticAnalyzer(syntax_tree)
    semantic_analyzer.analyze()

    gen = generator.MachineCodeGenerator(syntax_tree)
    machine_code = gen.generate()

    with open(output, 'w', encoding='utf-8') as output_file:
        output_file.write(machine_code)

    print(f'File successfully saved to {output}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSA Lab 3 assembly translator")
    parser.add_argument("-s", "--source", required=True, type=str, help="File with asm code")
    parser.add_argument("-o", "--output", required=True, type=str, help="File with output sources")
    args = parser.parse_args()
    main(args.source, args.output)
