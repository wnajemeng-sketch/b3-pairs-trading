import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm

def analyze_wdo_di():
    # Carregar dados
    df = pd.read_csv("historical_data_wdo_di.csv", index_col=0)
    df.index = pd.to_datetime(df.index)
    
    print("Iniciando análise de Pairs Trading WDOFUT vs DIFUT...")
    
    # 1. Correlação de Pearson
    correlation = df["WDOFUT"].corr(df["DIFUT"])
    print(f"Correlação de Pearson entre WDOFUT e DIFUT: {correlation:.4f}")
    
    # 2. Teste de Cointegração (Engle-Granger)
    score, p_value, _ = coint(df["WDOFUT"], df["DIFUT"])
    print(f"P-valor do teste de Cointegração: {p_value:.4f}")
    
    if p_value < 0.05:
        print("Os ativos são COINTEGRADOS (95% de confiança).")
    else:
        print("Os ativos NÃO são cointegrados com 95% de confiança.")
        
    # 3. Cálculo do Hedge Ratio (Beta) via Regressão OLS
    Y = df["WDOFUT"]
    X = df["DIFUT"]
    X = sm.add_constant(X)
    model = sm.OLS(Y, X).fit()
    beta = model.params["DIFUT"]
    intercept = model.params["const"]
    
    print(f"Hedge Ratio (Beta): {beta:.4f}")
    
    # 4. Cálculo do Spread
    df["Spread"] = df["WDOFUT"] - (beta * df["DIFUT"] + intercept)
    
    # 5. Z-Score do Spread
    spread_mean = df["Spread"].mean()
    spread_std = df["Spread"].std()
    df["Z-Score"] = (df["Spread"] - spread_mean) / spread_std
    
    # Plotar resultados
    plt.figure(figsize=(15, 10))
    
    # Subplot 1: Preços Normalizados
    plt.subplot(3, 1, 1)
    wdo_norm = (df["WDOFUT"] - df["WDOFUT"].mean()) / df["WDOFUT"].std()
    di_norm = (df["DIFUT"] - df["DIFUT"].mean()) / df["DIFUT"].std()
    plt.plot(wdo_norm, label="WDOFUT (Normalizado)")
    plt.plot(di_norm, label="DIFUT (Normalizado)")
    plt.title("WDOFUT vs DIFUT (Normalizados)")
    plt.legend()
    
    # Subplot 2: Spread
    plt.subplot(3, 1, 2)
    plt.plot(df["Spread"], color="orange")
    plt.axhline(df["Spread"].mean(), color="black", linestyle="--")
    plt.title("Spread (WDOFUT - Beta * DIFUT - Intercept)")
    
    # Subplot 3: Z-Score e Sinais
    plt.subplot(3, 1, 3)
    plt.plot(df["Z-Score"], color="blue")
    plt.axhline(0, color="black", linestyle="--")
    plt.axhline(2, color="red", linestyle="--")
    plt.axhline(-2, color="green", linestyle="--")
    plt.title("Z-Score do Spread (Sinais de Entrada)")
    plt.legend(["Z-Score", "Média", "Venda Spread (+2)", "Compra Spread (-2)"])
    
    plt.tight_layout()
    plt.savefig("pairs_trading_wdo_di.png")
    print("Gráfico de análise salvo em pairs_trading_wdo_di.png")
    
    # Salvar dados processados
    df.to_csv("analyzed_data_wdo_di.csv")
    return df

if __name__ == "__main__":
    analyze_wdo_di()
