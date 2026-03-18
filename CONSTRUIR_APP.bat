@echo off
chcp 65001 > nul

REM --- Script Mestre para Construir o Pairs Trading Analyzer ---
REM Este script ira:
REM 1. Mudar para o diretorio onde este .bat esta localizado.
REM 2. Criar o arquivo requirements.txt.
REM 3. Criar o script Python setup_build.py.
REM 4. Executar o setup_build.py para instalar dependencias e gerar o executavel.
REM 5. Manter a janela aberta para diagnostico.

set "CURRENT_DIR=%~dp0"
cd /d "%CURRENT_DIR%"

echo ==================================================
echo  Iniciando Construcao do Pairs Trading Analyzer
echo ==================================================
echo.

REM --- Criar requirements.txt ---
echo Criando requirements.txt...
(
    echo customtkinter
    echo yfinance
    echo matplotlib
    echo statsmodels
    echo pyinstaller
    echo pandas
    echo numpy
    echo scipy
) > requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Nao foi possivel criar requirements.txt.
    pause
    exit /b 1
)
echo requirements.txt criado com sucesso.
echo.

REM --- Criar setup_build.py ---
echo Criando setup_build.py...
(
    echo import subprocess
    echo import sys
    echo import os
    echo import shutil
    echo.
    echo APP_NAME = "pairs_trading_app.py"
    echo EXE_NAME = "PairsTradingAnalyzer"
    echo.
    echo def run_command(command, check=True, shell=False):
    echo     print(f"Executando: {command}")
    echo     try:
    echo         result = subprocess.run(command, check=check, shell=shell, capture_output=True, text=True, encoding=\'utf-8\')
    echo         print(result.stdout)
    echo         if result.stderr:
    echo             print(f"ERRO/AVISO: {result.stderr}")
    echo         return result.returncode == 0
    echo     except subprocess.CalledProcessError as e:
    echo         print(f"ERRO FATAL: Comando falhou com codigo {e.returncode}")
    echo         print(f"STDOUT: {e.stdout}")
    echo         print(f"STDERR: {e.stderr}")
    echo         return False
    echo     except Exception as e:
    echo         print(f"ERRO INESPERADO: {e}")
    echo         return False
    echo.
    echo def install_dependencies():
    echo     print("\\n--- 1. Instalando/Atualizando dependencias Python ---")
    echo     if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"]):
    echo         print("Falha ao atualizar o pip. Tentando continuar...")
    echo     
    echo     if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
    echo         print("ERRO: Falha ao instalar as dependencias do requirements.txt.")
    echo         return False
    echo     print("Dependencias instaladas/atualizadas com sucesso.")
    echo     return True
    echo.
    echo def find_customtkinter_path():
    echo     print("\\n--- 2. Encontrando o caminho do CustomTkinter ---")
    echo     try:
    echo         result = subprocess.run([sys.executable, "-c", "import site; print(site.getsitepackages()[0])"], capture_output=True, text=True, check=True, encoding=\'utf-8\')
    echo         site_packages_path = result.stdout.strip()
    echo         customtkinter_path = os.path.join(site_packages_path, "customtkinter")
    echo         
    echo         if os.path.exists(customtkinter_path):
    echo             print(f"CustomTkinter encontrado em: {customtkinter_path}")
    echo             return customtkinter_path
    echo         else:
    echo             print(f"AVISO: CustomTkinter nao encontrado no caminho padrao: {customtkinter_path}")
    echo             print("Tentando encontrar via `customtkinter.__file__`...")
    echo             result = subprocess.run([sys.executable, "-c", "import customtkinter; import os; print(os.path.dirname(customtkinter.__file__))"], capture_output=True, text=True, check=True, encoding=\'utf-8\')
    echo             customtkinter_path = result.stdout.strip()
    echo             if os.path.exists(customtkinter_path):
    echo                 print(f"CustomTkinter encontrado em: {customtkinter_path}")
    echo                 return customtkinter_path
    echo             else:
    echo                 print("ERRO: Nao foi possivel encontrar o diretorio de instalacao do CustomTkinter.")
    echo                 return None
    echo     except Exception as e:
    echo         print(f"ERRO ao tentar encontrar o CustomTkinter: {e}")
    echo         return None
    echo.
    echo def build_executable(customtkinter_path):
    echo     print("\\n--- 3. Gerando o executavel com PyInstaller ---")
    echo     if not os.path.exists(APP_NAME):
    echo         print(f"ERRO: O arquivo da aplicacao \'{APP_NAME}\' nao foi encontrado no diretorio atual.")
    echo         return False
    echo.
    echo     print("Limpando diretorios \'build\' e \'dist\' antigos...")
    echo     if os.path.exists("build"):
    echo         shutil.rmtree("build")
    echo     if os.path.exists("dist"):
    echo         shutil.rmtree("dist")
    echo     if os.path.exists(f"{EXE_NAME}.spec"):
    echo         os.remove(f"{EXE_NAME}.spec")
    echo.
    echo     add_data_arg = f"{customtkinter_path};customtkinter/"
    echo     
    echo     command = [
    echo         sys.executable, "-m", "PyInstaller",
    echo         "--noconfirm",
    echo         "--onefile",
    echo         "--windowed",
    echo         "--name", EXE_NAME,
    echo         "--add-data", add_data_arg,
    echo         APP_NAME
    echo     ]
    echo     
    echo     if not run_command(command):
    echo         print("ERRO: Falha ao gerar o executavel. Verifique as mensagens acima para detalhes.")
    echo         print("Tente executar o PyInstaller sem \'--windowed\' para ver erros em tempo de execucao:")
    echo         print(f"{sys.executable} -m PyInstaller --noconfirm --onefile --name {EXE_NAME} --add-data \\\"{add_data_arg}\\\" {APP_NAME}")
    echo         return False
    echo         
    echo     print(f"Executavel \'{EXE_NAME}.exe\' gerado com sucesso na pasta \'dist\'.")
    echo     return True
    echo.
    echo if __name__ == "__main__":
    echo     print("Iniciando processo de build...")
    echo     if not install_dependencies():
    echo         print("Processo de build interrompido devido a falha nas dependencias.")
    echo         sys.exit(1)
    echo     
    echo     ctk_path = find_customtkinter_path()
    echo     if ctk_path is None:
    echo         print("Processo de build interrompido devido a falha ao encontrar CustomTkinter.")
    echo         sys.exit(1)
    echo         
    echo     if not build_executable(ctk_path):
    echo         print("Processo de build interrompido devido a falha na geracao do executavel.")
    echo         sys.exit(1)
    echo         
    echo     print("\\nProcesso de build concluido com sucesso!")
    echo     print(f"Seu executavel esta em: .\\dist\\{EXE_NAME}.exe")
    echo     input("Pressione Enter para sair...")
) > setup_build.py
if %errorlevel% neq 0 (
    echo ERRO: Nao foi possivel criar setup_build.py.
    pause
    exit /b 1
)
echo setup_build.py criado com sucesso.
echo.

REM --- Executar o script Python de build ---
echo Executando o script de build Python...
"%PYTHON_EXE%" setup_build.py

if %errorlevel% neq 0 (
    echo ERRO: O script de build Python falhou. Verifique as mensagens acima.
)

echo.
echo ==================================================
echo  Processo de Construcao Finalizado.
echo ==================================================
echo.
pause
endlocal
