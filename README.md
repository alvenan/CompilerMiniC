# Trabalho 09 - Otimização (parte 1)

Este trabalho trata da integração de otimizadores para o código intermediário baseado no código de três endereços (TAC) da linguagem MiniC.

## O que deve ser feito:

1. Ler via linha de comando um arquivo com TAC não otimizado e gerar um arquivo com TAC otimizado.

2. Integrar as três técnicas apresentadas em aula:

    (i) Simplificação de expressões (identidades algébricas simples);

    (ii) Propagação de constantes;

    (iii) Eliminação de subexpressões comuns (CSE).

3. Definir a sequência de execução dos três otimizadores e repeti-la até ponto fixo, isto é, enquanto houver mudanças no TAC.

4. Caso deseje, pode reutilizar os códigos de exemplo dos slides/Colab — faça ajustes mínimos necessários para integração.

5. A solução pode ser autônoma (TAC → TAC) ou acoplada ao seu pipeline MiniC (MiniC → TAC → otimização → TAC).

## O que deve ser entregue:

* O código Python dos otimizadores e do programa principal que orquestra as passes.

* A gramática (se integrar ao pipeline MiniC), o Visitor semântico e o gerador de TAC (opcional se você optar por trabalhar só TAC→TAC).

* Pelo menos cinco arquivos de teste (entradas TAC e seus respectivos TACs otimizados), compactados em um ZIP.

* Nomeie o ZIP com seu nome.