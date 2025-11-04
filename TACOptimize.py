# Função que aplica a técnica de propagação de constantes em código de três endereços
def propagar_constantes(codigo):
    # Dicionário que armazena variáveis com valores constantes conhecidos
    constantes = {}

    # Lista para armazenar o código otimizado
    otimizado = []

    # Processa cada linha do código original
    for linha in codigo:
        # Remove espaços em branco no início e fim
        linha = linha.strip()

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
        if nova_direita.isdigit():
            constantes[esquerda] = nova_direita
        else:
            if esquerda in constantes:
                constantes.pop(esquerda, None)

        # Adiciona a linha otimizada à saída
        otimizado.append(esquerda + " = " + nova_direita)

    # Retorna a lista final do código otimizado
    return otimizado

# Função que aplica a técnica de simplificação de expressões
def simplificar_expressoes(codigo):
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

def eliminar_subexpressoes_comuns_corrigido(codigo):
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

def TACOptimize(codigo):
    passes = [
        propagar_constantes,
        simplificar_expressoes,
        eliminar_subexpressoes_comuns_corrigido,
    ]
    while True:
        before = "\n".join(codigo)
        for opt in passes:
            codigo = opt(codigo)
            codigo = [str(l).rstrip("\r") for l in codigo]
        after = "\n".join(codigo)
        if after == before:
            return codigo
