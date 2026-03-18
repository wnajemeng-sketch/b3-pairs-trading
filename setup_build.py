import subprocess
import sys
import os
import shutil

APP_NAME = "pairs_trading_app.py"
EXE_NAME = "PairsTradingAnalyzer"

def run_command(command, check=True, shell=False):
    print(f"Executando: {command}")
    try:
        result = subprocess.run(command, check=check, shell=shell, capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        if result.stderr:
            print(f"ERRO/AVISO: {result.stderr}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"ERRO FATAL: Comando falhou com código {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"ERRO INESPERADO: {e}")
        return False

def install_dependencies():
    print("\n--- 1. Instalando/Atualizando dependências Python ---")
    if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"]):
        print("Falha ao atualizar o pip. Tentando continuar...")
    
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
        print("ERRO: Falha ao instalar as dependências do requirements.txt.")
        return False
    print("Dependências instaladas/atualizadas com sucesso.")
    return True

def find_customtkinter_path():
    print("\n--- 2. Encontrando o caminho do CustomTkinter ---")
    try:
        # Tenta encontrar o caminho do site-packages
        result = subprocess.run([sys.executable, "-c", "import site; print(site.getsitepackages()[0])"], capture_output=True, text=True, check=True, encoding='utf-8')
        site_packages_path = result.stdout.strip()
        customtkinter_path = os.path.join(site_packages_path, "customtkinter")
        
        if os.path.exists(customtkinter_path):
            print(f"CustomTkinter encontrado em: {customtkinter_path}")
            return customtkinter_path
        else:
            print(f"AVISO: CustomTkinter não encontrado no caminho padrão: {customtkinter_path}")
            print("Tentando encontrar via `customtkinter.__file__`...")
            result = subprocess.run([sys.executable, "-c", "import customtkinter; import os; print(os.path.dirname(customtkinter.__file__))"], capture_output=True, text=True, check=True, encoding='utf-8')
            customtkinter_path = result.stdout.strip()
            if os.path.exists(customtkinter_path):
                print(f"CustomTkinter encontrado em: {customtkinter_path}")
                return customtkinter_path
            else:
                print("ERRO: Não foi possível encontrar o diretório de instalação do CustomTkinter.")
                return None
    except Exception as e:
        print(f"ERRO ao tentar encontrar o CustomTkinter: {e}")
        return None

def build_executable(customtkinter_path):
    print("\n--- 3. Gerando o executável com PyInstaller ---")
    if not os.path.exists(APP_NAME):
        print(f"ERRO: O arquivo da aplicação '{APP_NAME}' não foi encontrado no diretório atual.")
        return False

    # Limpar builds anteriores
    print("Limpando diretórios 'build' e 'dist' antigos...")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists(f"{EXE_NAME}.spec"):
        os.remove(f"{EXE_NAME}.spec")

    add_data_arg = f"{customtkinter_path};customtkinter/"
    
    # Comando PyInstaller
    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed", # Para não abrir a janela do console
        "--name", EXE_NAME,
        "--add-data", add_data_arg,
        APP_NAME
    ]
    
    if not run_command(command):
        print("ERRO: Falha ao gerar o executável. Verifique as mensagens acima para detalhes.")
        print("Tente executar o PyInstaller sem '--windowed' para ver erros em tempo de execução:")
        print(f"{sys.executable} -m PyInstaller --noconfirm --onefile --name {EXE_NAME} --add-data \"{add_data_arg}\" {APP_NAME}")
        return False
        
    print(f"Executável '{EXE_NAME}.exe' gerado com sucesso na pasta 'dist'.")
    return True

if __name__ == "__main__":
    print("Iniciando processo de build...")
    if not install_dependencies():
        print("Processo de build interrompido devido a falha nas dependências.")
        sys.exit(1)
    
    ctk_path = find_customtkinter_path()
    if ctk_path is None:
        print("Processo de build interrompido devido a falha ao encontrar CustomTkinter.")
        sys.exit(1)
        
    if not build_executable(ctk_path):
        print("Processo de build interrompido devido a falha na geração do executável.")
        sys.exit(1)
        
    print("\nProcesso de build concluído com sucesso!")
    print(f"Seu executável está em: .\\dist\\{EXE_NAME}.exe")
    input("Pressione Enter para sair...")
