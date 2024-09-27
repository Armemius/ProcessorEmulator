class ASTNode:
    def __str__(self):
        return self.__class__.__name__


class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __str__(self):
        return f"ProgramNode(statements=[{', '.join(str(stmt) for stmt in self.statements)}])"


class StatementNode(ASTNode):
    pass


class InstructionNode(StatementNode):
    def __init__(self, opcode, operands):
        self.opcode = opcode
        self.operands = operands

    def __str__(self):
        return f"InstructionNode(opcode={self.opcode}, operands={self.operands})"


class LabelNode(StatementNode):
    def __init__(self, identifier):
        self.identifier = identifier

    def __str__(self):
        return f"LabelNode(identifier={self.identifier})"


class SectionNode(StatementNode):
    def __init__(self, section_type):
        self.section_type = section_type

    def __str__(self):
        return f"SectionNode(section_type={self.section_type})"


class CommentNode(StatementNode):
    def __init__(self, comment):
        self.comment = comment

    def __str__(self):
        return f"CommentNode(comment={self.comment})"


class ParserToken:
    def __init__(self, token_type, value, line):
        self.type = token_type
        self.value = value
        self.line = line


class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.next_token()

    def next_token(self):
        if self.tokens:
            token = self.tokens.pop(0)
            self.current_token = ParserToken(token[0], token[1], token[2])
        else:
            self.current_token = None

    def parse(self):
        statements = []
        while self.current_token is not None:
            if self.current_token.type == 'SECTION':
                statements.append(self.parse_section())
            elif self.current_token.type == 'LABEL':
                statements.append(self.parse_label())
            elif self.current_token.type == 'OPCODE':
                statements.append(self.parse_instruction())
            else:
                self.error()
            # self.next_token()
        return ProgramNode(statements)

    def parse_section(self):
        section_type = self.current_token.value
        self.next_token()
        return SectionNode(section_type)

    def parse_label(self):
        identifier = self.current_token.value
        self.next_token()
        return LabelNode(identifier)

    def parse_instruction(self):
        opcode = self.current_token.value
        self.next_token()
        operands = []
        while self.current_token and self.current_token.type in ['IDENTIFIER', 'NUMBER', 'CHAR', 'STRING', 'NULLPTR']:
            operands.append(self.current_token.value)
            self.next_token()
            if self.current_token and self.current_token.type == 'COMMA':
                self.next_token()
        return InstructionNode(opcode, operands)

    def parse_comment(self):
        comment = self.current_token.value
        self.next_token()
        return CommentNode(comment)

    def error(self):
        raise Exception(f"Unexpected token '{self.current_token.value}' on line {self.current_token.line}")
