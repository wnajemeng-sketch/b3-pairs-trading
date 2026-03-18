@echo off
setlocal

REM --- Configurações ---
set "APP_NAME=pairs_trading_app.py"
set "EXE_NAME=PairsTradingAnalyzer"

echo.
echo ==================================================
echo  Gerador de Executavel para Pairs Trading Analyzer
echo ==================================================
echo.

REM --- 1. Encontrar o Python e Pip ---
set "PYTHON_EXE="
set "PIP_EXE="

for %%P in (python.exe python3.exe) do (
    where %%P >nul 2>nul
    if not errorlevel 1 (
        for /f "delims=" %%i in (
            'where %%P'
        ) do set "PYTHON_EXE=%%i"
        goto :found_python
    )
)

:found_python
if "%PYTHON_EXE%"=="" (
    echo ERRO: Python nao encontrado no PATH. Por favor, instale Python (versao 3.9+) e adicione-o ao PATH.
    echo Download: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

echo Python encontrado: "%PYTHON_EXE%"

for %%P in (pip.exe pip3.exe) do (
    where %%P >nul 2>nul
    if not errorlevel 1 (
        for /f "delims=" %%i in (
            'where %%P'
        ) do set "PIP_EXE=%%i"
        goto :found_pip
    )
)

:found_pip
if "%PIP_EXE%"=="" (
    echo ERRO: Pip nao encontrado no PATH. Verifique sua instalacao do Python.
    pause
    exit /b 1
)

echo Pip encontrado: "%PIP_EXE%"
echo.

REM --- 2. Instalar/Atualizar Dependencias ---
echo Verificando e instalando dependencias Python...
"%PIP_EXE%" install --upgrade pip
"%PIP_EXE%" install customtkinter yfinance matplotlib statsmodels pyinstaller
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias. Verifique as mensagens acima.
    pause
    exit /b 1
)
echo Dependencias instaladas/atualizadas com sucesso.
echo.

REM --- 3. Encontrar o caminho do CustomTkinter ---
set "SITE_PACKAGES_PATH="
for /f "delims=" %%i in (
    '"%PYTHON_EXE%" -c "import site; print(site.getsitepackages()[0])"'
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

REM --- 4. Gerar o Executavel com PyInstaller ---
echo Gerando o executavel "%EXE_NAME%.exe"...

"%PYTHON_EXE%" -m PyInstaller --noconfirm --onefile --windowed --name "%EXE_NAME%" --add-data "%CUSTOMTKINTER_PATH%;customtkinter/" "%APP_NAME%"

if %errorlevel% neq 0 (
    echo ERRO: Falha ao gerar o executavel. Verifique as mensagens acima para detalhes.
    echo Tente executar o comando PyInstaller manualmente para ver o erro:
    echo "%PYTHON_EXE%" -m PyInstaller --noconfirm --onefile --windowed --name "%EXE_NAME%" --add-data "%CUSTOMTKINTER_PATH%;customtkinter/" "%APP_NAME%"
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
