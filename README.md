# Algoritmo de Pairs Trading: WINFUT vs DIFUT (B3)

Este repositório contém um algoritmo completo para análise de correlação, cointegração e backtesting de uma estratégia de **Pairs Trading** entre o Mini Contrato Futuro de Ibovespa (**WINFUT**) e o Contrato Futuro de Taxa DI (**DIFUT**) da B3.

## 📊 Visão Geral

A estratégia de Pairs Trading (ou Arbitragem Estatística) baseia-se na premissa de que dois ativos correlacionados tendem a manter uma relação estável ao longo do tempo. Quando o "spread" entre eles desvia significativamente da média histórica, abrimos uma posição comprando o ativo subvalorizado e vendendo o sobrevalorizado, esperando a reversão à média.

Neste projeto, analisamos a relação entre o mercado de ações (WINFUT) e as taxas de juros (DIFUT), que historicamente apresentam correlação negativa.

## 🛠️ Estrutura do Projeto

- `data_collector.py`: Script para coleta de dados históricos usando `yfinance` (WINFUT proxy) e `pyield` (DIFUT/DI1).
- `pairs_trading_analysis.py`: Realiza testes estatísticos de Correlação de Pearson e Cointegração (Engle-Granger), além de calcular o Spread e Z-Score.
- `backtest.py`: Simula a estratégia baseada em desvios de Z-Score (+2/-2) e calcula retornos acumulados.
- `historical_data.csv`: Dados brutos coletados.
- `analyzed_data.csv`: Dados com cálculos de Spread e Z-Score.
- `backtest_results.png`: Gráfico de desempenho da estratégia.
- `pairs_trading_analysis.png`: Gráfico de análise técnica (Z-Score e Sinais).

## 🚀 Como Executar

1. Instale as dependências:
   ```bash
   pip install yfinance pandas numpy matplotlib seaborn statsmodels pyield polars
   ```

2. Execute a coleta de dados:
   ```bash
   python data_collector.py
   ```

3. Realize a análise estatística:
   ```bash
   python pairs_trading_analysis.py
   ```

4. Execute o backtesting:
   ```bash
   python backtest.py
   ```

## 📈 Resultados da Análise Recente (Últimos 60 dias úteis)

- **Correlação**: ~ -0.61 (Forte correlação negativa).
- **Cointegração**: Não detectada (P-valor > 0.05).
- **Conclusão**: O par apresentou desvios estruturais no período analisado, o que invalidou a estratégia de reversão à média estática, resultando em um retorno negativo no backtest simples. Recomenda-se o uso de modelos dinâmicos (como Filtro de Kalman) para períodos de alta volatilidade macroeconômica.

## ⚠️ Aviso Legal

Este código tem fins puramente educacionais e de estudo quantitativo. O mercado financeiro envolve riscos e este algoritmo não constitui recomendação de investimento.
