import sys
from antlr4 import *
from miniCLexer import miniCLexer
from miniCParser import miniCParser
from Visitor import Visitor
from TACVisitor import TACVisitor

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
    tacvisitor = TACVisitor()
    tacvisitor.visit(tree)
    out_path = sys.argv[1].rsplit('.', 1)[0] + ".tac"
    with open(out_path, "w") as file:
        for line in tacvisitor.code:
            file.write(line + "\n")
    print("Arquivo " + sys.argv[1].rsplit('.', 1)[0] + ".tac gerado")