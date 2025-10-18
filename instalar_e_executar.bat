@echo off
echo ========================================
echo Sistema de Fechamento de Caixa - Brumake
echo Script de Instalacao e Execucao
echo ========================================
echo.

:: Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao esta instalado ou nao esta no PATH
    echo Por favor, instale o Python 3.8 ou superior
    pause
    exit /b 1
)

echo Python encontrado!
python --version

echo.
echo Instalando dependencias...
pip install reportlab Pillow

echo.
echo Verificando instalacao...
python -c "import tkinter; import sqlite3; print('Tkinter e SQLite3: OK')"
python -c "import reportlab; print('ReportLab: OK')" 2>nul || echo "AVISO: ReportLab nao instalado - PDFs nao funcionarao"

echo.
echo ========================================
echo Instalacao concluida!
echo ========================================
echo.
echo Para executar o sistema:
echo 1. Execute: python src/main.py
echo 2. OU execute este arquivo novamente
echo.
echo Usuario master padrao:
echo   Usuario: admin
echo   Senha: admin123
echo.
echo ========================================

set /p choice="Deseja executar o sistema agora? (s/n): "
if /i "%choice%"=="s" (
    echo.
    echo Iniciando sistema...
    cd /d "%~dp0"
    python src/main.py
) else (
    echo.
    echo Para executar posteriormente, use: python src/main.py
)

pause