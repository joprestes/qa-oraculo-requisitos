@echo off
:: Este script automatiza a criação do ambiente virtual e a instalação das dependências.

ECHO ----------------------------------------------------
ECHO Iniciando o setup do ambiente para QA Oraculo...
ECHO ----------------------------------------------------

:: Verifica se o ambiente virtual já existe para não recriá-lo
IF NOT EXIST .venv (
    ECHO 1. Criando ambiente virtual (.venv)...
    python3 -m venv .venv
) ELSE (
    ECHO 1. Ambiente virtual (.venv) ja existe. Pulando a criacao.
)

ECHO 2. Ativando o ambiente virtual e instalando dependencias...

:: Ativa o ambiente, instala as dependências e desativa
call .\.venv\Scripts\activate

:: Aqui vamos instalar as bibliotecas.
 pip install -r requirements.txt

call .\.venv\Scripts\deactivate.bat


ECHO ----------------------------------------------------
ECHO Setup concluido com sucesso!
ECHO.
ECHO Para comecar a trabalhar, ative o ambiente virtual com o comando:
ECHO .\.venv\Scripts\activate
ECHO ----------------------------------------------------