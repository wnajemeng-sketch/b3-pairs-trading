import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.stattools import coint, adfuller
import statsmodels.api as sm

def analyze_pairs():
    # Carregar dados
    df = pd.read_csv("historical_data.csv", index_col=0)
    df.index = pd.to_datetime(df.index)
    
    print("Iniciando análise de Pairs Trading...")
    
    # 1. Correlação de Pearson
    correlation = df['WINFUT'].corr(df['DIFUT'])
    print(f"Correlação de Pearson entre WINFUT e DIFUT: {correlation:.4f}")
    
    # 2. Teste de Cointegração (Engle-Granger)
    # H0: Não há cointegração
    score, p_value, _ = coint(df['WINFUT'], df['DIFUT'])
    print(f"P-valor do teste de Cointegração: {p_value:.4f}")
    
    if p_value < 0.05:
        print("Os ativos são COINTEGRADOS (95% de confiança).")
    else:
        print("Os ativos NÃO são cointegrados com 95% de confiança.")
        
    # 3. Cálculo do Hedge Ratio (Beta) via Regressão OLS
    Y = df['WINFUT']
    X = df['DIFUT']
    X = sm.add_constant(X)
    model = sm.OLS(Y, X).fit()
    beta = model.params['DIFUT']
    intercept = model.params['const']
    
    print(f"Hedge Ratio (Beta): {beta:.4f}")
    
    # 4. Cálculo do Spread
    # Spread = Y - (Beta * X + Intercept)
    df['Spread'] = df['WINFUT'] - (beta * df['DIFUT'] + intercept)
    
    # 5. Z-Score do Spread
    spread_mean = df['Spread'].mean()
    spread_std = df['Spread'].std()
    df['Z-Score'] = (df['Spread'] - spread_mean) / spread_std
    
    # Plotar resultados
    plt.figure(figsize=(15, 10))
    
    # Subplot 1: Preços Normalizados
    plt.subplot(3, 1, 1)
    win_norm = (df['WINFUT'] - df['WINFUT'].mean()) / df['WINFUT'].std()
    di_norm = (df['DIFUT'] - df['DIFUT'].mean()) / df['DIFUT'].std()
    plt.plot(win_norm, label='WINFUT (Normalizado)')
    plt.plot(di_norm, label='DIFUT (Normalizado)')
    plt.title('WINFUT vs DIFUT (Normalizados)')
    plt.legend()
    
    # Subplot 2: Spread
    plt.subplot(3, 1, 2)
    plt.plot(df['Spread'], color='purple')
    plt.axhline(df['Spread'].mean(), color='black', linestyle='--')
    plt.title('Spread (WINFUT - Beta * DIFUT - Intercept)')
    
    # Subplot 3: Z-Score e Sinais
    plt.subplot(3, 1, 3)
    plt.plot(df['Z-Score'], color='blue')
    plt.axhline(0, color='black', linestyle='--')
    plt.axhline(2, color='red', linestyle='--')
    plt.axhline(-2, color='green', linestyle='--')
    plt.title('Z-Score do Spread (Sinais de Entrada)')
    plt.legend(['Z-Score', 'Média', 'Venda Spread (+2)', 'Compra Spread (-2)'])
    
    plt.tight_layout()
    plt.savefig('pairs_trading_analysis.png')
    print("Gráfico de análise salvo em pairs_trading_analysis.png")
    
    # Salvar dados processados
    df.to_csv("analyzed_data.csv")
    return df

if __name__ == "__main__":
    analyze_pairs()
