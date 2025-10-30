#!/usr/bin/env python3
# ==========================================================
# main.py — Entry Point do QA Oráculo
# ==========================================================
# Este arquivo serve como ponto de entrada para o Streamlit,
# permitindo que o módulo qa_core seja importado corretamente.
# ==========================================================

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path do Python
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Importa e executa o app principal
from qa_core.app import main

if __name__ == "__main__":
    main()
