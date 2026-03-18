import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run_backtest():
    # Carregar dados analisados
    df = pd.read_csv("analyzed_data.csv", index_col=0)
    df.index = pd.to_datetime(df.index)
    
    # Parâmetros da estratégia
    entry_threshold = 2.0
    exit_threshold = 0.0
    
    # Sinais
    # Z-Score > +2: Venda WINFUT, Compra DIFUT (espera o spread cair)
    # Z-Score < -2: Compra WINFUT, Venda DIFUT (espera o spread subir)
    
    df['Position'] = 0
    current_pos = 0
    
    for i in range(len(df)):
        z = df['Z-Score'].iloc[i]
        
        if current_pos == 0:
            if z > entry_threshold:
                current_pos = -1 # Venda Spread
            elif z < -entry_threshold:
                current_pos = 1 # Compra Spread
        elif current_pos == 1: # Long Spread
            if z >= exit_threshold:
                current_pos = 0 # Fecha
        elif current_pos == -1: # Short Spread
            if z <= exit_threshold:
                current_pos = 0 # Fecha
                
        df.iloc[i, df.columns.get_loc('Position')] = current_pos
        
    # Calcular retornos
    # Retorno do Spread = Variação do Spread
    # Como o Spread é WINFUT - Beta * DIFUT, o retorno diário é a mudança no valor do spread
    # Mas para simplificar, vamos usar a variação percentual dos ativos
    
    df['WINFUT_Ret'] = df['WINFUT'].pct_change()
    df['DIFUT_Ret'] = df['DIFUT'].pct_change()
    
    # Beta foi calculado na análise (aproximadamente -2.3M)
    # Vamos recarregar o beta da análise ou usar o valor salvo
    # Para este exemplo, vamos focar no retorno do Spread normalizado
    
    # Retorno da estratégia:
    # Se Position = 1 (Long WINFUT, Short DIFUT): Ret = WINFUT_Ret - DIFUT_Ret
    # Se Position = -1 (Short WINFUT, Long DIFUT): Ret = -WINFUT_Ret + DIFUT_Ret
    
    df['Strategy_Ret'] = df['Position'].shift(1) * (df['WINFUT_Ret'] - df['DIFUT_Ret'])
    df['Cum_Strategy_Ret'] = (1 + df['Strategy_Ret'].fillna(0)).cumprod()
    
    print(f"Retorno Acumulado da Estratégia: {(df['Cum_Strategy_Ret'].iloc[-1] - 1)*100:.2f}%")
    
    # Plotar Retorno
    plt.figure(figsize=(12, 6))
    plt.plot(df['Cum_Strategy_Ret'], label='Estratégia Pairs Trading')
    plt.title('Retorno Acumulado da Estratégia (WINFUT vs DIFUT)')
    plt.legend()
    plt.savefig('backtest_results.png')
    print("Gráfico de backtest salvo em backtest_results.png")
    
    df.to_csv("backtest_results.csv")
    return df

if __name__ == "__main__":
    run_backtest()
