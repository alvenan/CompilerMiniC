import sys
from antlr4 import *
from miniCLexer import miniCLexer
from miniCParser import miniCParser
from Visitor import Visitor

input_stream = FileStream(sys.argv[1])
lexer = miniCLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = miniCParser(token_stream)
tree = parser.program()

visitor = Visitor()
visitor.visit(tree)

if visitor.errors:
    print("Erros encontrados:")
    for err in visitor.errors:
        print(err)
else:
    print("Nenhum erro encontrado.")
