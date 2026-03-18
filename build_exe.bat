@echo off
setlocal

REM --- Configurações ---
set "APP_NAME=pairs_trading_app.py"
set "EXE_NAME=PairsTradingAnalyzer"
set "PYTHON_VERSION=Python311" REM Ajuste se sua versão do Python for diferente (ex: Python39, Python310)

echo.
echo ==================================================
echo  Gerador de Executavel para Pairs Trading Analyzer
echo ==================================================
echo.

REM --- 1. Verificar e Instalar Dependencias (Opcional, mas recomendado) ---
REM    Este passo assume que o pip esta no PATH. Se nao estiver, instale Python primeiro.

python -c "import sys; print(sys.version_info.major)" >nul 2>&1
if %errorlevel% neq 0 (
    echo Python nao encontrado. Por favor, instale Python (versao 3.9+) e adicione-o ao PATH.
    echo Download: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

echo Verificando e instalando dependencias Python...
pip install --upgrade pip >nul 2>&1
pip install customtkinter yfinance matplotlib statsmodels pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Erro ao instalar dependencias. Verifique sua conexao com a internet ou permissoes.
    pause
    exit /b 1
)
echo Dependencias instaladas/atualizadas com sucesso.
echo.

REM --- 2. Encontrar o caminho do CustomTkinter ---
for /f "delims=" %%i in (
    'python -c "import site; print(site.getsitepackages()[0])"'
) do set "SITE_PACKAGES_PATH=%%i"

set "CUSTOMTKINTER_PATH=%SITE_PACKAGES_PATH%\customtkinter"

if not exist "%CUSTOMTKINTER_PATH%" (
    echo ERRO: CustomTkinter nao encontrado em "%CUSTOMTKINTER_PATH%".
    echo Por favor, verifique se CustomTkinter esta instalado corretamente.
    pause
    exit /b 1
)

echo Caminho do CustomTkinter encontrado: "%CUSTOMTKINTER_PATH%"
echo.

REM --- 3. Gerar o Executavel com PyInstaller ---
echo Gerando o executavel "%EXE_NAME%.exe"...

pyinstaller --noconfirm --onefile --windowed --name "%EXE_NAME%" --add-data "%CUSTOMTKINTER_PATH%;customtkinter/" "%APP_NAME%"

if %errorlevel% neq 0 (
    echo ERRO: Falha ao gerar o executavel. Verifique as mensagens acima para detalhes.
    echo Tente executar o comando PyInstaller manualmente para ver o erro:
    echo pyinstaller --noconfirm --onefile --windowed --name "%EXE_NAME%" --add-data "%CUSTOMTKINTER_PATH%;customtkinter/" "%APP_NAME%"
    pause
    exit /b 1
)

echo.
echo ==================================================
echo  Executavel gerado com sucesso!
echo  Voce pode encontra-lo na pasta "dist" dentro deste diretorio.
echo ==================================================
echo.
pause
endlocal
