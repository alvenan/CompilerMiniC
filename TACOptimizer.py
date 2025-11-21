"""
Aqui eu explico, de forma direta e com exemplos, como implementei as duas 
novas otimizações: dobrando constantes e eliminação de código morto.

Escrevo em primeira pessoa, da forma como eu apresentaria no meu trabalho.

1) Dobrando constantes

Nesta etapa eu identifico expressões em que todos os valores são constantes
e substituo a expressão pela avaliação direta. A ideia é simples: se o
compilador já sabe o resultado, não faz sentido deixar a operação para o
tempo de execução.

Exemplos:
    t1 = 2 + 3  ->  t1 = 5
    t2 = 10 * 4 ->  t2 = 40
    t3 = 8 < 20 ->  t3 = 1

Isso reduz instruções desnecessárias e deixa o TAC mais limpo para as
otimizações seguintes: propagação de constantes, eliminação de subexpressões
comuns e eliminação de código morto.

2) Eliminação de código morto

Depois das demais otimizações, eu faço uma varredura de baixo para cima no
TAC. Durante essa varredura eu mantenho um conjunto de variáveis “vivas”,
ou seja, valores que ainda influenciam no resultado final do programa.

Sempre que encontro uma atribuição do tipo:
    t5 = ...
eu verifico se esse temporário t5 é realmente usado depois.  
Se não for, removo a linha.

Exemplo:
    t1 = a + b     (e t1 nunca é usado depois)
    -> removo essa instrução

Se for usado, eu mantenho a linha e adiciono as variáveis do lado direito
ao conjunto de vivas.

Exemplo:
    t3 = x + y      (t3 será usado mais adiante)
    -> mantenho  
    -> adiciono x e y como variáveis vivas

Para variáveis que não são temporárias (como a, b, g1, g2), eu mantenho
sempre, garantindo preservação de estado e semântica.

Remoção de rótulos:
Depois de eliminar instruções mortas, analiso todos os "goto Lx" e
"ifz ... goto Lx" para saber quais rótulos realmente são usados.  
Rótulos nunca referenciados são removidos.

Exemplo:
    label L7        (mas ninguém faz goto L7)
    -> removo

Assim, atendo ao requisito do T10: elimino
"""

"""Author: Alison Venâncio"""

from miniCVisitor import miniCVisitor
from typing import List

class TACOptimizer(miniCVisitor):
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
                partes = linha.split("=", 1)
                esquerda = partes[0].strip()
                direita = partes[1].strip()
                tokens = direita.split()

                # NÃO fazer CSE em chamadas de função
                if "call" in tokens:
                    otimizado.append(linha)
                else:
                    if len(tokens) == 3:
                        op1 = tokens[0]
                        operador = tokens[1]
                        op2 = tokens[2]
                        chave = op1 + " " + operador + " " + op2

                        if chave in subexpressoes:
                            otimizado.append(f"{esquerda} = {subexpressoes[chave]}")
                        else:
                            subexpressoes[chave] = esquerda
                            otimizado.append(linha)
                            for var in [op1, op2]:
                                if var not in operandos_usados:
                                    operandos_usados[var] = set()
                                operandos_usados[var].add(chave)
                    else:
                        otimizado.append(linha)

                # mantém a invalidação das subexpressões dependentes
                if esquerda in operandos_usados:
                    for chave_dependente in operandos_usados[esquerda]:
                        if chave_dependente in subexpressoes:
                            del subexpressoes[chave_dependente]
                    del operandos_usados[esquerda]
            else:
                # >>> ESSA PARTE FALTA NO TEU CÓDIGO
                otimizado.append(linha)
                # <<<

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

        def tokens_de_uso(rhs: str):
            ops = {"+","-","*","/","%","==","!=","<","<=",">",">=","call",",","arg"}
            out = []
            for t in rhs.split():
                tt = t.rstrip(",")
                if tt in ops or tt.isdigit() or (tt.startswith("-") and tt[1:].isdigit()) or tt.startswith("L"):
                    continue
                out.append(tt)
            return out

        usados = set()
        for linha in codigo:
            st = linha.strip()
            if not st:
                continue
            if st.startswith("ret"):
                partes = st.split(None, 1)
                if len(partes) == 2:
                    usados.update(tokens_de_uso(partes[1]))
            elif st.startswith("arg "):
                usados.update(tokens_de_uso(st[3:]))
            elif st.startswith("ifz ") and "goto" in st:
                cond = st.split("goto", 1)[0][4:]
                usados.update(tokens_de_uso(cond))
            elif st.startswith("print "):
                usados.update(tokens_de_uso(st[5:]))
            else:
                if " call " in (" " + st + " ") and "=" in st:
                    lhs, rhs = st.split("=", 1)
                    usados.update(tokens_de_uso(rhs))
                    usados.add(lhs.strip())

        n = len(codigo)
        viva = [False] * n
        changed = True
        while changed:
            changed = False
            for i, linha in enumerate(codigo):
                st = linha.strip()
                if not st:
                    continue
                if st.startswith(("func ", "endfunc", "label ", "goto ", "ifz ", "ret", "arg ")):
                    continue
                if "=" in st:
                    lhs, rhs = st.split("=", 1)
                    lhs = lhs.strip()
                    rhs = rhs.strip()
                    rhs_tokens = [t.rstrip(",") for t in rhs.split()]

                    if " call " in (" " + rhs + " "):
                        if not viva[i]:
                            viva[i] = True
                            changed = True
                        for t in tokens_de_uso(rhs):
                            if t not in usados:
                                usados.add(t); changed = True
                        if lhs not in usados:
                            usados.add(lhs); changed = True
                        continue

                    if lhs in usados or lhs in rhs_tokens:
                        if not viva[i]:
                            viva[i] = True
                            changed = True
                        for t in tokens_de_uso(rhs):
                            if t not in usados:
                                usados.add(t); changed = True
                    else:
                        for t in tokens_de_uso(rhs):
                            if t not in usados:
                                usados.add(t); changed = True

        resultado = []
        for i, linha in enumerate(codigo):
            st = linha.rstrip("\n")
            s = st.strip()
            if not s:
                resultado.append(st)
                continue
            if s.startswith(("func ", "endfunc", "label ", "goto ", "ifz ", "ret", "arg ")):
                resultado.append(st)
                continue
            if " call " in (" " + st + " "):
                resultado.append(st)
                continue
            if "=" in s:
                lhs = s.split("=", 1)[0].strip()
                if viva[i]:
                    resultado.append(st)
                else:
                    continue
            else:
                resultado.append(st)

        compactado = []
        i = 0
        while i < len(resultado):
            cur = resultado[i]
            st = cur.strip()
            if st.startswith("goto ") and i + 1 < len(resultado):
                alvo = st.split()[1]
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
