import os
import sys

def generate_pyinstaller_command():
    # Caminho para o CustomTkinter, assumindo uma instalação padrão no Windows
    # O usuário precisará ajustar isso se a instalação for diferente
    if sys.platform == "win32":
        python_path = os.path.dirname(sys.executable)
        customtkinter_path = os.path.join(python_path, "Lib", "site-packages", "customtkinter")
        
        if not os.path.exists(customtkinter_path):
            print(f"Aviso: CustomTkinter não encontrado em {customtkinter_path}. Por favor, verifique a instalação.")
            print("Você pode precisar ajustar o caminho manualmente no comando PyInstaller.")
            # Fallback para um caminho mais genérico, pode não funcionar
            customtkinter_path = "customtkinter"

        add_data_arg = f"--add-data \"{customtkinter_path};customtkinter\""
        command = f"pyinstaller --noconfirm --onefile --windowed {add_data_arg} pairs_trading_app.py"
        print("Comando PyInstaller para Windows:")
        print(command)
        print("\nExecute este comando no Prompt de Comando (CMD) ou PowerShell no seu ambiente Windows, após instalar as dependências.")
    else:
        print("Este script é destinado a gerar comandos PyInstaller para Windows.")
        print("Para Linux/macOS, use: pyinstaller --noconfirm --onefile --windowed pairs_trading_app.py")

if __name__ == "__main__":
    generate_pyinstaller_command()
