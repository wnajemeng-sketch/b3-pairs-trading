@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

echo.
echo ==========================================================
echo  GERADOR DE EXECUTAVEL - PAIRS TRADING ANALYZER
echo ==========================================================
echo.

REM 1. Forcar o diretorio para a pasta onde o .bat esta
cd /d "%~dp0"
echo Diretorio atual: "%cd%"

REM 2. Verificar se o Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado! 
    echo Por favor, instale o Python (3.9 ou superior) e marque "Add Python to PATH".
    echo Download: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

REM 3. Instalar/Atualizar dependencias
echo.
echo [1/3] Instalando bibliotecas necessarias...
python -m pip install --upgrade pip
python -m pip install customtkinter yfinance matplotlib statsmodels pyinstaller pandas numpy scipy
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias. Verifique sua internet.
    pause
    exit /b 1
)

REM 4. Localizar o CustomTkinter no sistema (Infalivel via Python)
echo.
echo [2/3] Localizando arquivos do CustomTkinter...
for /f "delims=" %%i in ('python -c "import customtkinter; import os; print(os.path.dirname(customtkinter.__file__))"') do set "CTK_PATH=%%i"

if not exist "!CTK_PATH!" (
    echo [ERRO] Nao foi possivel localizar a pasta do CustomTkinter.
    pause
    exit /b 1
)
echo CustomTkinter encontrado em: "!CTK_PATH!"

REM 5. Gerar o Executavel
echo.
echo [3/3] Criando o arquivo .EXE (Isso pode levar alguns minutos)...
echo Limpando pastas antigas...
if exist build rd /s /q build
if exist dist rd /s /q dist

python -m PyInstaller --noconfirm --onefile --windowed --name "PairsTradingAnalyzer" --add-data "!CTK_PATH!;customtkinter/" pairs_trading_app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha na geracao do executavel. 
    echo Tentando modo de depuracao (sem --windowed)...
    python -m PyInstaller --noconfirm --onefile --name "PairsTradingAnalyzer" --add-data "!CTK_PATH!;customtkinter/" pairs_trading_app.py
)

echo.
echo ==========================================================
echo  PROCESSO CONCLUIDO!
echo ==========================================================
echo O seu programa esta na pasta: %cd%\dist\PairsTradingAnalyzer.exe
echo.
pause
