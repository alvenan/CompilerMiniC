# Trabalho 06 — Verificação de Variáveis, Tipos e Funções (MiniC)

Este trabalho deve considerar o analisador sintático feito para a linguagem **MiniC**.

## O que deve ser feito

1. **Extensão de tipos**
   - A gramática atual do MiniC só tem o tipo `int`. **Altere a gramática para incluir o tipo `char`.**
   - Inclua na regra `primary` mais uma opção para **`char`**.

2. **Analisador semântico**

### Parte 1 (cada questão vale 1 ponto)
a) Verificação de **variáveis não declaradas**;  
b) Verificação de **variáveis declaradas mais de uma vez**;  
c) Verificação do **número de argumentos** de chamadas de função;  
d) Verificação dos **tipos dos argumentos** (definidos e usados) nas chamadas de função;

### Parte 2 (cada questão vale 2 pontos)
e) **Compatibilidade de tipos** na atribuição, incluindo operações binárias (`+=`, `*=`, etc.);  
f) **Operandos** de `+`, `-`, `*`, `/`, `%` devem ser do tipo **int**;  
g) Comandos **`break`** e **`continue`** **apenas** dentro de laços **`while`**.

## O que deve ser entregue
- A **gramática modificada**;
- O **novo Visitor/Listener** (analisador semântico);
- O **programa principal**.

> Compacte os arquivos em **ZIP** e nomeie o arquivo **com o seu nome**.

## Observações
1. **Coloque todos os erros em uma lista** e **imprima a lista** ao final da análise.
2. **Mostre a linha e a posição** na linha onde ocorreu cada erro.
3. **Sugestão**: resolva por partes e, depois, faça a integração.

---

## Estrutura sugerida do projeto (mínima)