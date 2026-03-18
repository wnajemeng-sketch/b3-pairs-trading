import pyield as yd
import pandas as pd
from datetime import datetime, timedelta

def test_di1():
    print("Testando pyield para DI1...")
    # Tentar obter dados do DI1 para o vencimento mais próximo ou específico
    try:
        # O pyield costuma ter funções para buscar taxas DI
        # Vamos tentar buscar os dados de fechamento recentes
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # De acordo com a documentação sugerida no snippet: from pyield import futures
        from pyield import futures
        df = futures.get_di1(reference_date="2024-01-02") # Exemplo de data fixa para teste
        print("Dados DI1 obtidos com sucesso!")
        print(df.head())
    except Exception as e:
        print(f"Erro ao obter dados DI1: {e}")

if __name__ == "__main__":
    test_di1()
