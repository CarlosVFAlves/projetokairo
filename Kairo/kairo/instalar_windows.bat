@echo off
echo ========================================
echo    INSTALADOR AUTOMATICO - PROJETO KAIRO
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Baixe Python em: https://python.org/downloads/
    echo Marque "Add Python to PATH" durante a instalacao
    pause
    exit /b 1
)

echo.
echo [2/4] Instalando dependencias essenciais...
pip install requests colorama
if %errorlevel% neq 0 (
    echo Tentando instalacao alternativa...
    python -m pip install --user requests colorama
)

echo.
echo [3/4] Testando sistema...
cd maestro
python verificacao_completa.py

echo.
echo [4/4] Instalacao concluida!
echo.
echo ========================================
echo    COMO USAR O KAIRO:
echo ========================================
echo 1. Instale Ollama: https://ollama.ai/download
echo 2. Execute: ollama pull llama2
echo 3. Execute: ollama serve
echo 4. Execute: python main.py
echo ========================================
echo.
pause

