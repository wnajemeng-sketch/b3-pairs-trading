import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run_backtest_wdo_di():
    # Carregar dados analisados
    df = pd.read_csv("analyzed_data_wdo_di.csv", index_col=0)
    df.index = pd.to_datetime(df.index)
    
    # Parâmetros da estratégia
    entry_threshold = 2.0
    exit_threshold = 0.0
    
    # Sinais
    df["Position"] = 0
    current_pos = 0
    
    for i in range(len(df)):
        z = df["Z-Score"].iloc[i]
        
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
                
        df.iloc[i, df.columns.get_loc("Position")] = current_pos
        
    # Calcular retornos
    df["WDOFUT_Ret"] = df["WDOFUT"].pct_change()
    df["DIFUT_Ret"] = df["DIFUT"].pct_change()
    
    # Retorno da estratégia:
    # Se Position = 1 (Long WDO, Short DI): Ret = WDO_Ret - DI_Ret
    # Se Position = -1 (Short WDO, Long DI): Ret = -WDO_Ret + DI_Ret
    df["Strategy_Ret"] = df["Position"].shift(1) * (df["WDOFUT_Ret"] - df["DIFUT_Ret"])
    df["Cum_Strategy_Ret"] = (1 + df["Strategy_Ret"].fillna(0)).cumprod()
    
    print(f"Retorno Acumulado da Estratégia (WDO/DI): {(df['Cum_Strategy_Ret'].iloc[-1] - 1)*100:.2f}%")
    
    # Plotar Retorno
    plt.figure(figsize=(12, 6))
    plt.plot(df["Cum_Strategy_Ret"], label="Estratégia Pairs Trading WDO/DI", color="orange")
    plt.title("Retorno Acumulado da Estratégia (WDOFUT vs DIFUT)")
    plt.legend()
    plt.savefig("backtest_results_wdo_di.png")
    print("Gráfico de backtest salvo em backtest_results_wdo_di.png")
    
    df.to_csv("backtest_results_wdo_di.csv")
    return df

if __name__ == "__main__":
    run_backtest_wdo_di()
