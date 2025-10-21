import sys
from antlr4 import *
from miniCLexer import miniCLexer
from miniCParser import miniCParser

input_stream = FileStream(sys.argv[1])
lexer = miniCLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = miniCParser(token_stream)
tree = parser.program()
print(tree.toStringTree(recog=parser))