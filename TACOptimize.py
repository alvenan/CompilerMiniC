from miniCVisitor import miniCVisitor
from typing import List

class TACOptimize(miniCVisitor):
    def __init__(self) -> None:
        pass
# Função que aplica a técnica de propagação de constantes em código de três endereços
    def propagar_constantes(self, codigo):
    # Dicionário que armazena variáveis com valores constantes conhecidos
        constantes = {}

    # Lista para armazenar o código otimizado
        otimizado = []

    # Processa cada linha do código original
        for linha in codigo:
        # Remove espaços em branco no início e fim
            linha = linha.strip()

            # fronteiras de controle e chamadas: não propagar através
            if linha.startswith(('label', 'goto', 'ifz', 'ret', 'arg')):
                constantes = {}
                otimizado.append(linha)
                continue
            if " call " in (" " + linha + " "):
                constantes = {}

        # Mantém qualquer linha que não seja uma atribuição
            if "=" not in linha:
                otimizado.append(linha)
                continue

        # Divide a linha em duas partes: lado esquerdo e lado direito da atribuição
        # (apenas a primeira ocorrência de '=' para não quebrar '==', '!=', '<=', '>=')

            partes = linha.split("=", 1)
            esquerda = partes[0].strip()   # variável que recebe o valor
            direita = partes[1].strip()    # expressão atribuída à variável

        # Quebra o lado direito em palavras (tokens)
            palavras = direita.split()

        # Inicializa a nova versão do lado direito, com substituições
            ops_rel = {'==', '!=', '<', '<=', '>', '>='}
            if len(palavras) == 3 and palavras[1] in ops_rel and (not palavras[0].lstrip('-').isdigit() or not palavras[2].lstrip('-').isdigit()):
                nova_direita = direita
            else:
                nova_direita = ""

        # Substitui variáveis conhecidas por seus valores constantes
                for palavra in palavras:
                    if palavra in constantes:
                        nova_direita += constantes[palavra] + " "
                    else:
                        nova_direita += palavra + " "
                nova_direita = nova_direita.strip()

        # Se a expressão for apenas um número, armazenamos como constante conhecida
        # Caso contrário, invalidamos possível constante anterior da variável da esquerda

            if nova_direita.isdigit() or (nova_direita.startswith("-") and nova_direita[1:].isdigit()):
                constantes[esquerda] = nova_direita
            else:
                if esquerda in constantes:
                    constantes.pop(esquerda, None)

        # Adiciona a linha otimizada à saída

            otimizado.append(esquerda + " = " + nova_direita)

    # Retorna a lista final do código otimizado
        return otimizado

# Função que aplica a técnica de simplificação de expressões

    def simplificar_expressoes(self, codigo):
        otimizado = []

    # Processa cada linha do código original
        for linha in codigo:
            linha = linha.strip()

        # Processa apenas atribuições
            if "=" in linha:
            # divide só a primeira '=', preservando '==' '!=' '<=' '>=' na direita
                partes = linha.split("=", 1)
                esquerda = partes[0].strip()
                direita = partes[1].strip()
                tokens = direita.split()

            # Só processa expressões com exatamente 3 tokens (ex: b * 1)
                if len(tokens) == 3:
                    op1 = tokens[0]
                    operador = tokens[1]
                    op2 = tokens[2]

                # Otimizações para "*"
                    if operador == "*" and op2 == "1":
                        nova_direita = op1
                    elif operador == "*" and op1 == "1":
                        nova_direita = op2
                    elif operador == "*" and (op1 == "0" or op2 == "0"):
                        nova_direita = "0"

                # Otimizações para "/"
                    elif operador == "/" and op2 == "1":
                        nova_direita = op1

                # Otimizações para "+"
                    elif operador == "+" and op1 == "0" and op2 == "0":
                        nova_direita = "0"
                    elif operador == "+" and op2 == "0":
                        nova_direita = op1
                    elif operador == "+" and op1 == "0":
                        nova_direita = op2

                # Otimizações para "-"
                    elif operador == "-" and op1 == "0" and op2 == "0":
                        nova_direita = "0"
                    elif operador == "-" and op2 == "0":
                        nova_direita = op1
                    else:
                        nova_direita = direita
                else:
                # Se não for binária, mantém como está
                    nova_direita = direita

            # Adiciona a linha otimizada
                otimizado.append(esquerda + " = " + nova_direita)
            else:
            # Mantém qualquer outra linha
                otimizado.append(linha)
        return otimizado

    def eliminar_subexpressoes_comuns_corrigido(self, codigo):
        subexpressoes = {}   # dicionário de subexpressões conhecidas
        operandos_usados = {} # mapeamento de operandos → subexpressões dependentes
        otimizado = []
        for linha in codigo:
            linha = linha.strip()
            if "=" in linha:
            # divide só a primeira '=', preservando '==' '!=' '<=' '>='
                partes = linha.split("=", 1)
                esquerda = partes[0].strip()
                direita = partes[1].strip()
                tokens = direita.split()
                if len(tokens) == 3:
                    op1 = tokens[0]
                    operador = tokens[1]
                    op2 = tokens[2]
                    chave = op1 + " " + operador + " " + op2

                # Verifica se a subexpressão ainda é válida
                    if chave in subexpressoes:
                        otimizado.append(f"{esquerda} = {subexpressoes[chave]}")
                    else:
                    # Registra a nova subexpressão
                        subexpressoes[chave] = esquerda
                        otimizado.append(linha)

                    # Armazena os operandos utilizados nas subexpressões
                        for var in [op1, op2]:
                            if var not in operandos_usados:
                                operandos_usados[var] = set()
                            operandos_usados[var].add(chave)
                else:
                    otimizado.append(linha)
            # IMPORTANTE: sempre que uma variável for atualizada, invalidamos as subexpressões que dependem dela
                if esquerda in operandos_usados:
                    for chave_dependente in operandos_usados[esquerda]:
                        if chave_dependente in subexpressoes:
                            del subexpressoes[chave_dependente]
                    del operandos_usados[esquerda]
            else:
                otimizado.append(linha)
        return otimizado

    def dobrar_constantes(self, codigo):
        otimizado = []
        for linha in codigo:
            s = linha.strip()
            if "=" in s:
                esquerda, direita = s.split("=", 1)
                esquerda = esquerda.strip()
                direita = direita.strip()
                tokens = direita.split()

                if len(tokens) == 3:
                    op1, operador, op2 = tokens

                    is_int_op1 = op1.isdigit() or (op1.startswith("-") and op1[1:].isdigit())
                    is_int_op2 = op2.isdigit() or (op2.startswith("-") and op2[1:].isdigit())

                    if is_int_op1 and is_int_op2:
                        a = int(op1); b = int(op2)
                        val = None
                        try:
                            if operador == "+":
                                val = a + b
                            elif operador == "-":
                                val = a - b
                            elif operador == "*":
                                val = a * b
                            elif operador == "/":
                                if b != 0:
                                    val = int(a / b)
                            elif operador == "%":
                                if b != 0:
                                    val = a % b
                        except Exception:
                            val = None
                        if val is not None:
                            direita = str(val)
                otimizado.append(f"{esquerda} = {direita}")
            else:
                otimizado.append(s)
        return otimizado

    def eliminar_codigo_morto(self, codigo):
        usados = set()
        resultado = []

        def tokens_de_uso(rhs):
            ops = {"+","-","*","/","%","==","!=","<","<=",">",">=","call",",","arg"}
            out = []
            for t in rhs.split():
                tt = t.rstrip(",")
                if tt in ops or tt.isdigit() or (tt.startswith("-") and tt[1:].isdigit()) or tt.startswith("L"):
                    continue
                out.append(tt)
            return out

        for linha in reversed(codigo):
            s = linha.strip()
            if s.startswith(("ret","arg ","goto ","label ")):
                if s.startswith("ret") and len(s.split()) > 1:
                    for t in tokens_de_uso(s[3:].strip()):
                        usados.add(t)
                elif s.startswith("arg "):
                    for t in tokens_de_uso(s[4:].strip()):
                        usados.add(t)
                resultado.append(s)
                continue

            if "=" not in s:
                if s.startswith("ifz "):
                    cond = s[4:].split("goto",1)[0].strip()
                    for t in tokens_de_uso(cond):
                        usados.add(t)
                resultado.append(s)
                continue

            lhs, rhs = s.split("=",1)
            lhs = lhs.strip(); rhs = rhs.strip()

            if " call " in (" " + rhs + " "):
                for t in tokens_de_uso(rhs):
                    usados.add(t)
                usados.add(lhs)
                resultado.append(s)
                continue

            if lhs not in usados:
                for t in tokens_de_uso(rhs):
                    usados.add(t)
                continue

            for t in tokens_de_uso(rhs):
                usados.add(t)
            resultado.append(s)

        resultado.reverse()

        compactado = []
        i = 0
        while i < len(resultado):
            cur = resultado[i]
            if cur.startswith("goto ") and i + 1 < len(resultado):
                alvo = cur.split()[1]
                j = i + 1
                while j < len(resultado) and resultado[j].strip() == "":
                    j += 1
                if j < len(resultado) and resultado[j].strip() == f"label {alvo}":
                    i += 1
                    continue
            compactado.append(cur)
            i += 1

        referenciados = set()
        for s in compactado:
            st = s.strip()
            if st.startswith("goto "):
                referenciados.add(st.split()[1])
            elif st.startswith("ifz ") and "goto" in st:
                referenciados.add(st.split("goto",1)[1].strip())

        final = []
        for s in compactado:
            st = s.strip()
            if st.startswith("label "):
                nome = st.split()[1]
                if nome not in referenciados:
                    continue
            final.append(s)

        return final

    def optimize(self, codigo: List[str]) -> List[str]:
        s = [str(l).rstrip("\r") for l in codigo]
        while True:
            before = "\n".join(s)
            for f in (
                self.propagar_constantes,
                self.dobrar_constantes,
                self.simplificar_expressoes,
                self.eliminar_subexpressoes_comuns_corrigido,
                self.eliminar_codigo_morto,
            ):
                s = f(s)
                s = [str(l).rstrip("\r") for l in s]
            if "\n".join(s) == before:
                return s
