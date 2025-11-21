# ==========================================================
# Makefile - QA Oráculo
# ==========================================================
# Comandos comuns para desenvolvimento e manutenção
# do projeto QA Oráculo.
# ==========================================================

.PHONY: help install install-dev setup run test lint format clean docs

# === Configuração ===
PYTHON := python3.12
PIP := pip3
VENV := .venv
PYTHON_VENV := $(VENV)/bin/python
PIP_VENV := $(VENV)/bin/pip

# === Cores para output ===
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# === Ajuda ===
help: ## Mostra esta mensagem de ajuda
	@echo "$(GREEN)QA Oráculo - Comandos Disponíveis$(NC)"
	@echo "=================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# === Instalação ===
install: ## Instala dependências de produção
	@echo "$(GREEN)Instalando dependências de produção...$(NC)"
	$(PIP_VENV) install -r requirements.txt

install-dev: ## Instala dependências de desenvolvimento
	@echo "$(GREEN)Instalando dependências de desenvolvimento...$(NC)"
	$(PIP_VENV) install -r requirements-dev.txt

setup: ## Configura ambiente de desenvolvimento completo
	@echo "$(GREEN)Configurando ambiente de desenvolvimento...$(NC)"
	@if [ -d "venv" ] && [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)Detectado ambiente virtual legado em venv/. Considere removê-lo com 'make clean-venv'.$(NC)"; \
	fi
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)Criando ambiente virtual...$(NC)"; \
		$(PYTHON) -m venv $(VENV); \
	fi
	@echo "$(YELLOW)Ativando ambiente virtual...$(NC)"
	@echo "$(YELLOW)Instalando dependências...$(NC)"
	$(MAKE) install-dev
	@echo "$(GREEN)Ambiente configurado com sucesso!$(NC)"
	@echo "$(YELLOW)Para ativar o ambiente: source $(VENV)/bin/activate$(NC)"

# === Execução ===
run: ## Executa a aplicação Streamlit
	@echo "$(GREEN)Executando QA Oráculo...$(NC)"
	$(PYTHON_VENV) -m streamlit run main.py

run-dev: ## Executa em modo desenvolvimento com auto-reload
	@echo "$(GREEN)Executando em modo desenvolvimento...$(NC)"
	$(PYTHON_VENV) -m streamlit run main.py --server.runOnSave true

# === Testes ===
test: ## Executa todos os testes
	@echo "$(GREEN)Executando testes...$(NC)"
	$(PYTHON_VENV) -m pytest tests/ -v

test-cov: ## Executa testes com cobertura
	@echo "$(GREEN)Executando testes com cobertura...$(NC)"
	$(PYTHON_VENV) -m pytest tests/ --cov=qa_core --cov-report=html --cov-report=term

test-fast: ## Executa apenas testes rápidos
	@echo "$(GREEN)Executando testes rápidos...$(NC)"
	$(PYTHON_VENV) -m pytest tests/ -v -m "not slow"

# === Qualidade de Código ===
lint: ## Executa verificação de linting
	@echo "$(GREEN)Executando linting...$(NC)"
	$(PYTHON_VENV) -m ruff check qa_core/ tests/ main.py

lint-fix: ## Corrige problemas de linting automaticamente
	@echo "$(GREEN)Corrigindo problemas de linting...$(NC)"
	$(PYTHON_VENV) -m ruff check qa_core/ tests/ main.py --fix

format: ## Formata código com Black
	@echo "$(GREEN)Formatando código...$(NC)"
	$(PYTHON_VENV) -m black qa_core/ tests/ main.py

format-check: ## Verifica formatação sem alterar arquivos
	@echo "$(GREEN)Verificando formatação...$(NC)"
	$(PYTHON_VENV) -m black qa_core/ tests/ main.py --check

# === Limpeza ===
clean: ## Remove arquivos temporários e caches
	@echo "$(GREEN)Limpando arquivos temporários...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	@echo "$(GREEN)Limpeza concluída!$(NC)"

clean-venv: ## Remove ambiente virtual
	@echo "$(RED)Removendo ambiente virtual...$(NC)"
	rm -rf $(VENV)
	rm -rf venv
	@echo "$(GREEN)Ambiente virtual removido!$(NC)"

# === Documentação ===
docs: ## Gera documentação
	@echo "$(GREEN)Gerando documentação...$(NC)"
	@echo "$(YELLOW)Documentação disponível em docs/$(NC)"

docs-serve: ## Serve documentação localmente
	@echo "$(GREEN)Servindo documentação...$(NC)"
	@echo "$(YELLOW)Acesse: http://localhost:8000$(NC)"
	cd docs && python -m http.server 8000

# === Build e Deploy ===
build: ## Constrói o pacote
	@echo "$(GREEN)Construindo pacote...$(NC)"
	$(PYTHON_VENV) -m build

install-pkg: ## Instala o pacote localmente
	@echo "$(GREEN)Instalando pacote localmente...$(NC)"
	$(PIP_VENV) install -e .

# === Desenvolvimento ===
dev-setup: setup install-pkg ## Setup completo para desenvolvimento
	@echo "$(GREEN)Setup de desenvolvimento concluído!$(NC)"

dev-check: lint format-check test ## Verifica qualidade antes do commit
	@echo "$(GREEN)Verificação de qualidade concluída!$(NC)"

# === Utilitários ===
requirements: ## Atualiza requirements.txt
	@echo "$(GREEN)Atualizando requirements...$(NC)"
	$(PIP_VENV) freeze > requirements.txt

requirements-dev: ## Atualiza requirements-dev.txt
	@echo "$(GREEN)Atualizando requirements de desenvolvimento...$(NC)"
	$(PIP_VENV) freeze > requirements-dev.txt

# === Status ===
status: ## Mostra status do projeto
	@echo "$(GREEN)Status do Projeto QA Oráculo$(NC)"
	@echo "================================"
	@echo "$(YELLOW)Ambiente Virtual:$(NC) $(if $(wildcard $(VENV)),✅ Ativo,❌ Não encontrado)"
	@echo "$(YELLOW)Testes:$(NC) $(shell $(PYTHON_VENV) -m pytest tests/ --collect-only -q 2>/dev/null | tail -1 || echo "❌ Erro")
	@echo "$(YELLOW)Linting:$(NC) $(shell $(PYTHON_VENV) -m ruff check qa_core/ --quiet 2>/dev/null && echo "✅ OK" || echo "❌ Problemas encontrados")
	@echo "$(YELLOW)Formatação:$(NC) $(shell $(PYTHON_VENV) -m black qa_core/ --check --quiet 2>/dev/null && echo "✅ OK" || echo "❌ Problemas encontrados")

# === Comando padrão ===
.DEFAULT_GOAL := help
