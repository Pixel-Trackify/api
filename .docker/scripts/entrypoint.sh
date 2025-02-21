#!/bin/sh
set -e  # Para o script caso algum comando falhe

# Se um argumento for passado, executa esse comando
if [ "$#" -gt 0 ]; then
    echo "▶ Running command: $@"
    exec "$@"
else
    echo "⚠ No command provided. Exiting."
    exit 1
fi
