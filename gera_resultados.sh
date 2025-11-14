#!/usr/bin/env bash

set -e

mkdir -p results

{
    echo "=== Gerando parser ==="
    antlr4 -Dlanguage=Python3 -visitor miniC.g

    echo
    echo "=== Limpando TAC antigos ==="
    rm -rf results/*.tac
    echo

    echo "=== miniC.g ==="
    cat miniC.g
    echo
    echo
    echo "=== main.py ==="
    cat main.py
    echo
    echo
    echo "=== Visitor.py ==="
    cat Visitor.py
    echo
    echo
    echo "=== TACVisitor.py ==="
    cat TACVisitor.py
    echo
    echo
    echo "=== TACOptimize.py ==="
    cat TACOptimize.py
    echo
    echo

    echo
    echo "=== Rodando testes em testes/*.mc ==="

    for mc in testes/*.mc; do
        [ -e "$mc" ] || continue
        base="$(basename "$mc" .mc)"

        echo
        echo "=== ${base} ==="
        echo
        echo "--- Código MiniC (${mc}) ---"
        cat "$mc"
        echo

        python main.py "$mc"
        echo

        if [ -f "results/${base}.tac" ]; then
            echo "--- TAC (results/${base}.tac) ---"
            cat "results/${base}.tac"
            echo
        fi

        if [ -f "results/${base}_opt.tac" ]; then
            echo "--- TAC otimizado (results/${base}_opt.tac) ---"
            cat "results/${base}_opt.tac"
            echo
        fi
    done
} > results/resultados.txt 2>&1