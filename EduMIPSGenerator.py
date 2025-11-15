import sys


"""Author: Alison Venâncio"""


class EduMIPSGenerator:
    """Transforma código de três endereços em Assembly EduMIPS64."""

    def __init__(self):
        self.max_args = 0

    # ---------- constantes ----------

    REGS = [
        "$t0",
        "$t1",
        "$t2",
        "$t3",
        "$t4",
        "$t5",
        "$t6",
        "$t7",
        "$t8",
        "$t9",
        "$s0",
        "$s1",
        "$s2",
        "$s3",
        "$s4",
        "$s5",
        "$s6",
        "$s7",
        "$s8",
        "$s9",
    ]  # $t9/$t8 usados p/ literais; $s* extras p/ temporários

    OPERADORES = (
        ">=",
        "<=",
        "==",
        "!=",
        ">",
        "<",
        "+",
        "-",
        "*",
        "=",
    )
    KEYWORDS = (
        "if",
        "goto",
        "func",
        "end",
        "return",
        "param",
        "call",
        "print",
        "var",
        "int",
        "char",
        "label",
        "endfunc",
    )

    def generate(self, tac_lines):
            cod_inter = [lin.rstrip("\n") for lin in tac_lines]

            variaveis = self.coletar_vars(cod_inter)
            regs, spilled = self.map_regs(variaveis)
            asm = self.traduzir(cod_inter, regs, spilled)

            saida = [".data"]
            for v in variaveis:
                saida.append(f"{v}:   .word 0")

            if self.max_args > 0:
                saida.append(f"args_area: .space {8 * self.max_args}")

            saida.append("")
            saida.append(".text")
            saida.append(".globl main")
            saida.extend(asm)
            saida.append("SYSCALL 0")
            return saida

    # ---------- utilitarios ----------

    def e_num(self, tok: str) -> bool:
        tok = tok.strip()
        if tok.startswith("-"):
            tok = tok[1:]
        return tok.isdigit()

    def e_char(self, tok: str) -> bool:
        return len(tok) >= 3 and tok.startswith("'") and tok.endswith("'")

    def valor_char(self, tok: str) -> int:
        if len(tok) >= 4 and tok[1] == "\\":
            return ord(tok[2])
        return ord(tok[1])

    def e_label(self, tok: str) -> bool:
        return tok.startswith("L") and tok[1:].isdigit()

    def e_var(self, tok: str) -> bool:
        return (
            tok
            and tok.isidentifier()
            and tok not in self.KEYWORDS
            and tok not in self.OPERADORES
            and tok not in self.REGS
            and not self.e_label(tok)
        )

    # dado uma linha retorna uma lista de todos os tokens
    def coletar_vars(self, tac) -> list[str]:
        vistos, varList = set(), []
        max_args = 0

        for lin in tac:
            parte = lin.partition(";")[0].strip()
            if not parte:
                continue

            # var int global_counter
            if parte.startswith("var "):
                parts = parte.split()
                if len(parts) >= 3:
                    name = parts[2]
                    if name not in vistos:
                        vistos.add(name)
                        varList.append(name)
                continue

            # param int a (opcional, se quiser em memória)
            if parte.startswith("param "):
                parts = parte.split()
                if len(parts) >= 3:
                    name = parts[2]
                    if name not in vistos:
                        vistos.add(name)
                        varList.append(name)
                continue

            # ignora linhas estruturais
            if parte.startswith(("func ", "endfunc", "end func",
                                 "label ", "goto ", "ifz ", "print ", "arg ")):
                # mas podemos aproveitar para contar args em 'call'
                pass

            # rastrear maior argc em 'call f, N'
            if "call " in parte:
                rhs = parte
                if "=" in parte:
                    _, rhs = parte.split("=", 1)
                rhs = rhs.strip()
                if rhs.startswith("call "):
                    try:
                        after_call = rhs.split("call", 1)[1].strip()
                        if "," in after_call:
                            _, argc_str = after_call.split(",", 1)
                            argc = int(argc_str.strip())
                            if argc > max_args:
                                max_args = argc
                    except Exception:
                        pass

            # lado esquerdo de atribuição são variáveis/temporários
            if "=" in parte and not parte.startswith(("func ", "endfunc", "end func")):
                left = parte.split("=", 1)[0].strip()
                if self.e_var(left) and left not in vistos:
                    vistos.add(left)
                    varList.append(left)

        # guardar quantos argumentos máximos foram vistos (para área de parâmetros)
        self.max_args = max_args

        return varList

    # ---------- registradores ----------
    def map_regs(self, vars_: list[str]) -> dict[str, str]:
        regs = {}
        spilled = set()
        for i, v in enumerate(vars_):
            if i < len(self.REGS):
                regs[v] = self.REGS[i]
            else:
                spilled.add(v)
        return regs, spilled

    # ---------- Carrega operando (var ou constante) ----------
    # Constante = carrega o valor em $t9
    # Variável = carrega o respectivo registrador

    def load_operand(self, tok: str, regs: dict[str, str], out: list[str], dest="$t9", spilled: set|None=None) -> str:
        tok = tok.strip()
        if self.e_num(tok):  # literal inteiro
            out.append(f"DADDIU  {dest}, $zero, {tok}")
            return dest
        if self.e_char(tok):
            val = self.valor_char(tok)
            out.append(f"DADDIU  {dest}, $zero, {val}")
            return dest
        r = regs.get(tok)
        if r:
            out.append(f"LD      {r}, {tok}($zero)")
            return r
        if spilled and tok in spilled:
            out.append(f"LD      {dest}, {tok}($zero)")
            return dest
        return tok

    # ---------- Geração linha a linha ----------
    def traduzir(self, cod_inter, regs: dict[str, str], spilled: set) -> list[str]:
        out = []
        params = []
        func_atual = None
        param_index = 0
        for lin in cod_inter:
            original = lin.rstrip()
            parte = original.partition(";")[0].strip()
            if not parte:
                continue

            out.append(f"; {original}")  # comentário

            # --- cabeçalho de função ---
            if parte.startswith("func "):
                parts = parte.split()
                # Ex.: "func void process_data" ou "func int main"
                if len(parts) >= 3:
                    nome = parts[2].split(",", 1)[0]
                elif len(parts) >= 2:
                    nome = parts[1].split(",", 1)[0]
                else:
                    continue
                func_atual = nome
                param_index = 0
                out.append(f"{nome}:")
                continue

            if parte.startswith("end func"):
                func_atual = None
                continue

            # --- rótulo ---
            if parte.endswith(":"):
                out.append(parte)
                continue

            # --- var (declaração) ---
            if parte.startswith("var "):
                continue

            # --- label (rótulo simples gerado em TAC) ---
            if parte.startswith("label "):
                out.append(parte.split(None,1)[1])
                continue

            # --- goto ---
            if parte.startswith("goto "):
                out.append(f"B       {parte.split()[1]}")
                continue

            # --- ifz VAR goto L ---
            if parte.startswith("ifz ") and "goto" in parte:
                # formato: ifz <cond> goto L
                cond = parte.split("goto",1)[0][4:].strip()
                label = parte.split("goto",1)[1].strip()
                rv = regs.get(cond)
                if rv:
                    out.append(f"LD      {rv}, {cond}($zero)")
                else:
                    rv = self.load_operand(cond, regs, out, "$t0", spilled)
                out.append(f"BEQ     {rv}, $zero, {label}")
                continue

            # --- param: copiar da área de args para variável formal ---
            if parte.startswith("param "):
                # formato: "param int a" ou "param char c"
                toks = parte.split()
                if len(toks) >= 3:
                    var_name = toks[2]
                    offset = 8 * param_index
                    out.append(f"LD      $t0, args_area+{offset}($zero)")
                    out.append(f"SD      $t0, {var_name}($zero)")
                    param_index += 1
                continue

            # --- arg: argumentos para chamadas ---
            if parte.startswith("arg "):
                params.append(parte.split(" ", 1)[1].strip())
                continue

            # --- print ---
            if parte.startswith("print "):
                op = parte.split(" ", 1)[1].strip()
                reg = self.load_operand(op, regs, out, "$t0", spilled)
                out.append(f"DADDU   $a0, {reg}, $zero")
                out.append("DADDIU  $v0, $zero, 1")
                out.append("SYSCALL 1")
                out.append("DADDIU  $a0, $zero, 10")
                out.append("DADDIU  $v0, $zero, 11")
                out.append("SYSCALL 11")
                continue

            # --- return ---
            if parte.startswith("return") or parte.startswith("ret"):
                toks = parte.split()
                if len(toks) > 1:
                    reg = self.load_operand(toks[1], regs, out, "$v0")
                    if reg != "$v0":
                        out.append(f"DADDU   $v0, {reg}, $zero")
                if func_atual and func_atual != "main":
                    out.append("JR      $ra")
                continue

            # --- atribuição ---
            if "=" in parte:
                toks = parte.split("=", 1)
                esq_ = toks[0].strip()
                dir_ = toks[1].strip()

                # chamada retornando valor
                if dir_.startswith("call "):
                    resto = dir_.split(" ", 1)[1]
                    try:
                        nome_parte, argc_parte = resto.split(",", 1)
                        argc = int(argc_parte.strip())
                    except ValueError:
                        nome_parte, argc = resto, 0
                    nome = nome_parte.strip()
                    args = params[-argc:] if argc else []
                    if argc:
                        params = params[:-argc]
                    for idx, arg in enumerate(args):
                        reg_arg = self.load_operand(arg, regs, out, "$t0", spilled)
                        offset = 8 * idx
                        out.append(f"SD      {reg_arg}, args_area+{offset}($zero)")
                    out.append(f"JAL     {nome}")
                    rd = regs.get(esq_)
                    if rd:
                        out.append(f"SD      $v0, {esq_}($zero)")
                    continue

                rd = regs.get(esq_)
                if rd is None:
                    rd = "$t0"

                # 1) constante direta
                if self.e_num(dir_):
                    out.append(f"DADDIU  {rd}, $zero, {dir_}")
                    out.append(f"SD      {rd}, {esq_}($zero)")
                    continue

                if self.e_char(dir_):
                    val = self.valor_char(dir_)
                    out.append(f"DADDIU  {rd}, $zero, {val}")
                    out.append(f"SD      {rd}, {esq_}($zero)")
                    continue

                # 2) operações aritméticas/comparações
                operador = None
                for op in ("<=", ">=", "==", "!=", ">", "<", "+", "-", "*", "/", "%"):
                    if f" {op} " in dir_ or op in dir_:
                        operador = op
                        break

                if operador:
                    # caso especial: soma com vários termos: a+b+c+d+e
                    if operador == "+" and "+" in dir_.strip().replace(" ", ""):
                        termos = [t.strip() for t in dir_.split("+")]
                        if not termos:
                            continue
                        # primeiro termo vai para rd
                        rx = self.load_operand(termos[0], regs, out, rd, spilled)
                        if rx != rd:
                            out.append(f"DADDU   {rd}, {rx}, $zero")
                        # soma os demais
                        for termo in termos[1:]:
                            ry = self.load_operand(termo, regs, out, "$t1", spilled)
                            out.append(f"DADDU   {rd}, {rd}, {ry}")
                        out.append(f"SD      {rd}, {esq_}($zero)")
                        continue

                    # caso geral binário (<=, >=, ==, !=, >, <, +, -, *)
                    x, y = [t.strip() for t in dir_.split(operador, 1)]
                    rx = self.load_operand(x, regs, out, "$t0", spilled)
                    ry = self.load_operand(y, regs, out, "$t1", spilled)
                    if operador == "+":
                        out.append(f"DADDU   {rd}, {rx}, {ry}")
                    elif operador == "-":
                        out.append(f"DSUBU   {rd}, {rx}, {ry}")
                    elif operador == "*":
                        out.append(f"DMULU   {rd}, {rx}, {ry}")
                    elif operador == "/":
                        # divisão inteira: quociente em rd
                        out.append(f"DIV     {rx}, {ry}")
                        out.append(f"MFLO    {rd}")
                    elif operador == "%":
                        # resto em rd
                        out.append(f"DIV     {rx}, {ry}")
                        out.append(f"MFHI    {rd}")
                    elif operador == "<":
                        out.append(f"SLT     {rd}, {rx}, {ry}")
                    elif operador == ">":
                        out.append(f"SLT     {rd}, {ry}, {rx}")
                    elif operador == ">=":
                        out.append(f"SLT     {rd}, {rx}, {ry}")
                        out.append(f"XORI    {rd}, {rd}, 1")
                    elif operador == "<=":
                        out.append(f"SLT     {rd}, {ry}, {rx}")
                        out.append(f"XORI    {rd}, {rd}, 1")
                    elif operador == "==":
                        out.append(f"DSUBU   $t8, {rx}, {ry}")
                        out.append(f"SLTIU   {rd}, $t8, 1")
                    elif operador == "!=":
                        out.append(f"DSUBU   $t8, {rx}, {ry}")
                        out.append(f"SLTIU   {rd}, $t8, 1")
                        out.append(f"XORI    {rd}, {rd}, 1")
                    # aqui você ainda não mexe em / e %
                    # (vamos colocar já no passo 2)
                    # grava SEMPRE o resultado em memória
                    out.append(f"SD      {rd}, {esq_}($zero)")
                    continue

                # 4) cópia simples
                if self.e_var(dir_):
                    rv = regs.get(dir_)
                    if rv:
                        out.append(f"LD      {rv}, {dir_}($zero)")
                        out.append(f"SD      {rv}, {esq_}($zero)")
                        continue

                rv = self.load_operand(dir_, regs, out, "$t0", spilled)
                out.append(f"SD      {rv}, {esq_}($zero)")
                continue

            # --- chamada void ---
            if parte.startswith("call "):
                resto = parte.split(" ", 1)[1]
                try:
                    nome_parte, argc_parte = resto.split(",", 1)
                    argc = int(argc_parte.strip())
                except ValueError:
                    nome_parte, argc = resto, 0
                nome = nome_parte.strip()
                args = params[-argc:] if argc else []
                if argc:
                    params = params[:-argc]
                for idx, arg in enumerate(args):
                    reg_arg = self.load_operand(arg, regs, out, "$t0", spilled)
                    offset = 8 * idx
                    out.append(f"SD      {reg_arg}, args_area+{offset}($zero)")
                out.append(f"JAL     {nome}")
                continue

            if parte.startswith("endfunc") or parte.startswith("end func"):
                if func_atual and func_atual != "main":
                    if not out or not out[-1].startswith("JR "):
                        out.append("JR      $ra")
                func_atual = None
                continue

            # linha não reconhecida
            print("Comando não reconhecido: ", original)

        return out
