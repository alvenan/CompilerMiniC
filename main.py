import sys
import os
from antlr4 import *
from miniCLexer import miniCLexer
from miniCParser import miniCParser
from Visitor import Visitor
from TACVisitor import TACVisitor
from TACOptimizer import TACOptimize

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

    resultados_dir = "results"
    os.makedirs(resultados_dir, exist_ok=True)

    base_name = os.path.basename(sys.argv[1]).rsplit('.', 1)[0]
    out_path = os.path.join(resultados_dir, base_name + ".tac")

    tac = list(tacvisitor.code)
    text_orig = "\n".join(tac)
    if not text_orig.endswith("\n"):
        text_orig += "\n"
    with open(out_path, "w") as file:
        file.write(text_orig)
    print("Arquivo " + out_path + " gerado")

    tacopt = TACOptimize().optimize(list(tac))

    out_opt = os.path.join(resultados_dir, base_name + "_opt.tac")
    text = "\n".join(tacopt)
    if not text.endswith("\n"):
        text += "\n"
    with open(out_opt, "w") as file:
        file.write(text)
    print("Arquivo " + out_opt + " gerado")