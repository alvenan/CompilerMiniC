import sys
import os
from antlr4 import *
from antlr4.InputStream import InputStream
from miniCLexer import miniCLexer

"""Author: Alison Venâncio"""

from miniCParser import miniCParser
from Visitor import Visitor
from TACVisitor import TACVisitor
from TACOptimizer import TACOptimizer
from EduMIPSGenerator import EduMIPSGenerator

src_text = open(sys.argv[1], 'r', encoding='utf-8').read()
input_stream = InputStream(src_text)
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

    tacopt = TACOptimizer().optimize(list(tac))

    out_opt = os.path.join(resultados_dir, base_name + "_opt.tac")
    text = "\n".join(tacopt)
    if not text.endswith("\n"):
        text += "\n"
    with open(out_opt, "w") as file:
        file.write(text)
    print("Arquivo " + out_opt + " gerado")
    try:
        gen = EduMIPSGenerator()
        asm_lines = gen.generate(tacopt)
        out_s = os.path.join(resultados_dir, base_name + ".s")
        asm_text = "\n".join(asm_lines)
        if not asm_text.endswith("\n"):
            asm_text += "\n"
        with open(out_s, "w") as fasm:
            fasm.write(asm_text)
        print("Arquivo " + out_s + " gerado")
    except SystemExit as se:
        print("Aviso: gerador EduMIPS finalizou (possível falta de registradores):", se)
    except Exception as e:
        print("Aviso: falha ao gerar assembly EduMIPS:", e)