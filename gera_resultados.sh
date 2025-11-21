#!/usr/bin/env bash

set -e

if [ -d results ]; then
    rm -rf results/*
else
    mkdir results
fi

ts=$(date +%m-%d-%H-%M-%S)
outfile="results/code_${ts}.txt"
resultfile="results/results_${ts}.txt"

header="Gerado em: $(date '+%Y-%m-%d %H:%M:%S')"
echo "$header" > "$outfile"
echo "$header" > "$resultfile"

testes_pattern="testes/*.mc"

if [ "$#" -gt 0 ]; then
    testes_pattern=""
    for arg in "$@"; do
        if [ -f "$arg" ]; then
            testes_pattern="$testes_pattern $arg"
        else
            echo "Erro: teste '$arg' não encontrado."
            exit 1
        fi
    done
fi

# BLOCO 1: só informações de código / diffs → code_...
{
    echo
    echo "=== Gerando parser ==="
    antlr4 -Dlanguage=Python3 -visitor miniC.g

    echo
    echo "=== Limpando TAC e ASM antigos ==="
    rm -rf results/*.tac
    rm -rf results/*.s
    echo

    echo "=== gera_resultados.sh ==="
    cat gera_resultados.sh
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
    echo "=== TACOptimizer.py ==="
    cat TACOptimizer.py
    echo
    echo
    echo "=== EduMIPSGenerator.py ==="
    cat EduMIPSGenerator.py
    echo
    echo
    echo "=== ../eduMips/generate_mips.py ==="
    cat ../eduMips/generate_mips.py
    echo
    echo

    echo "=== git diff ==="
    git diff || true
    echo
    echo

    echo "=== git diff EduMIPSGenerator.py ../eduMips/generate_mips.py ==="
    git diff EduMIPSGenerator.py ../eduMips/generate_mips.py || true
    echo
    echo
} >> "$outfile" 2>&1

# BLOCO 2: só execução de testes → results_...
{
    echo
    echo "=== Rodando testes em ${testes_pattern} ==="

    for mc in $testes_pattern; do
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

        if [ -f "results/${base}.s" ]; then
            echo "--- Assembly EduMIPS (results/${base}.s) ---"
            cat "results/${base}.s"
            echo
        fi
    done
} >> "$resultfile" 2>&1