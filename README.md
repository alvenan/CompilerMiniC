# Trabalho 10 — Otimização (parte 2)

Dando continuidade ao Trabalho 09, este projeto integra duas novas técnicas de otimização ao pipeline de código de três endereços (TAC) da linguagem MiniC:

* (iv) Constant folding (dobrando constantes)

* (v) Eliminação de código morto (inclui remoção de saltos e rótulos inúteis)

## O que deve ser feito

1. Ler via linha de comando um arquivo com TAC não otimizado e gerar o TAC otimizado.

2. Integrar cinco otimizadores e definir a sequência de execução:

    1. Propagação de constantes
    2. Constant folding (novo)
    3. Simplificação de expressões
    4. Eliminação de subexpressões comuns (CSE)
    5. Eliminação de código morto (novo)

3. Repetir a sequência até ponto fixo (parar quando não houver mudanças).

4. Entregar o programa Python e pelo menos 5 arquivos de testes em um ZIP nomeado com o seu nome.

> Observação: é permitido reaproveitar os códigos do T09/slides, fazendo os ajustes mínimos necessários.

## Descrição de alto nível — Novos otimizadores
(iv) Constant folding (dobrando constantes)

* Ideia: avaliar em tempo de compilação expressões onde ambos os operandos são literais inteiros e substituir o resultado:

    `t1 = 4 * 3 → t1 = 12, t2 = 7 - 2 → t2 = 5.`

* Implementação (resumo):

    * Para linhas `lhs = rhs`, dividir com `split("=", 1)` (não quebrar `==`, `!=`, `<=`, `>=`).

    * Tokenizar `rhs`. `Se len(tokens) == 3`, `op ∈ {+, -, *, /, %}` e op1/op2 são dígitos, calcular e substituir por um único número.

    * Mantém-se conservador (apenas inteiros literais).

(v) Eliminação de código morto (DCE) — incluindo rótulos

* Ideia: remover instruções que não afetam o resultado observável (atribuições cujo destino nunca é lido), além de limpar saltos redundantes e rótulos órfãos.

* Implementação (resumo):

    1. Dead assignments (liveness backward):

        * Percorra de trás para frente mantendo um conjunto `live`.
        * Para `lhs = rhs`: se `lhs ∉ live` e a instrução não tem efeitos colaterais (sem `call` no RHS, e não é `arg`, `ret`, `goto`, `label`), remover.
        * Adicionar ao `live` todas as variáveis lidas em `rhs`.

    2. Saltos/rótulos inúteis:

        * Remover `goto Lx` se a próxima instrução (ignorando vazias) for `label Lx`.
        * Coletar alvos de `goto`/`ifz ... goto` e remover `label` não referenciado.