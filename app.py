import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.stattools import coint, adfuller
import statsmodels.api as sm
import os

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="B3 Pairs Trading",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# HELPERS
# ============================================================

@st.cache_data
def load_data(pair: str) -> pd.DataFrame | None:
    filename = f"historical_data_{'win_di' if pair == 'WINFUT vs DIFUT' else 'wdo_di'}.csv"
    if not os.path.exists(filename):
        return None
    df = pd.read_csv(filename, index_col=0, parse_dates=True)
    return df


def compute_analysis(df: pd.DataFrame, col_a: str, col_b: str, window: int):
    """Run cointegration analysis and return enriched dataframe + stats."""
    result = {}

    # Correlation
    result["correlation"] = df[col_a].corr(df[col_b])

    # Cointegration test
    score, p_value, _ = coint(df[col_a], df[col_b])
    result["coint_score"] = score
    result["coint_pvalue"] = p_value

    # OLS hedge ratio
    Y = df[col_a]
    X = sm.add_constant(df[col_b])
    model = sm.OLS(Y, X).fit()
    beta = model.params.iloc[1]
    intercept = model.params.iloc[0]
    result["beta"] = beta
    result["intercept"] = intercept
    result["r_squared"] = model.rsquared

    # Spread
    df = df.copy()
    df["Spread"] = df[col_a] - (beta * df[col_b] + intercept)

    # Rolling Z-Score
    df["Spread_Mean"] = df["Spread"].rolling(window=window, min_periods=1).mean()
    df["Spread_Std"] = df["Spread"].rolling(window=window, min_periods=1).std()
    df["Z_Score"] = (df["Spread"] - df["Spread_Mean"]) / df["Spread_Std"]

    # ADF on spread
    adf_stat, adf_pvalue, *_ = adfuller(df["Spread"].dropna(), maxlag=1)
    result["adf_stat"] = adf_stat
    result["adf_pvalue"] = adf_pvalue

    # Half-life of mean reversion
    spread_lag = df["Spread"].shift(1)
    spread_diff = df["Spread"] - spread_lag
    spread_lag_clean = spread_lag.dropna()
    spread_diff_clean = spread_diff.loc[spread_lag_clean.index]
    hl_model = sm.OLS(spread_diff_clean, sm.add_constant(spread_lag_clean)).fit()
    lambda_val = hl_model.params.iloc[1]
    half_life = -np.log(2) / lambda_val if lambda_val < 0 else np.inf
    result["half_life"] = half_life

    return df, result


def run_backtest(df: pd.DataFrame, col_a: str, col_b: str,
                 entry_z: float, exit_z: float, stop_z: float,
                 beta: float):
    """Run vectorized-ish backtest and return enriched df + metrics."""
    df = df.copy()
    positions = np.zeros(len(df))
    current_pos = 0
    trades = []
    entry_idx = None

    for i in range(len(df)):
        z = df["Z_Score"].iloc[i]
        if np.isnan(z):
            positions[i] = 0
            continue

        if current_pos == 0:
            if z >= entry_z:
                current_pos = -1  # Short spread
                entry_idx = i
            elif z <= -entry_z:
                current_pos = 1  # Long spread
                entry_idx = i
        elif current_pos == 1:
            if z >= -exit_z or (stop_z > 0 and z <= -(entry_z + stop_z)):
                trades.append({"entry": entry_idx, "exit": i, "side": "long"})
                current_pos = 0
        elif current_pos == -1:
            if z <= exit_z or (stop_z > 0 and z >= (entry_z + stop_z)):
                trades.append({"entry": entry_idx, "exit": i, "side": "short"})
                current_pos = 0

        positions[i] = current_pos

    df["Position"] = positions

    # Returns
    df["Ret_A"] = df[col_a].pct_change()
    df["Ret_B"] = df[col_b].pct_change()

    # Strategy: long spread = long A + short B (weighted by beta)
    df["Strategy_Ret"] = df["Position"].shift(1) * (df["Ret_A"] - abs(beta) * df["Ret_B"])
    df["Strategy_Ret"] = df["Strategy_Ret"].fillna(0)
    df["Cum_Return"] = (1 + df["Strategy_Ret"]).cumprod()

    # Buy & hold A for comparison
    df["BH_A"] = (1 + df["Ret_A"].fillna(0)).cumprod()

    # Metrics
    total_ret = df["Cum_Return"].iloc[-1] - 1
    n_days = len(df)
    ann_factor = 252 / max(n_days, 1)

    daily_rets = df["Strategy_Ret"]
    sharpe = (daily_rets.mean() / daily_rets.std() * np.sqrt(252)) if daily_rets.std() > 0 else 0

    # Max drawdown
    cum_max = df["Cum_Return"].cummax()
    drawdown = (df["Cum_Return"] - cum_max) / cum_max
    max_dd = drawdown.min()

    # Trade stats
    n_trades = len(trades)
    winning = 0
    total_pnl_trades = []
    for t in trades:
        entry_val = df["Cum_Return"].iloc[t["entry"]]
        exit_val = df["Cum_Return"].iloc[t["exit"]]
        pnl = (exit_val - entry_val) / entry_val
        total_pnl_trades.append(pnl)
        if pnl > 0:
            winning += 1

    win_rate = winning / n_trades if n_trades > 0 else 0
    avg_trade = np.mean(total_pnl_trades) if total_pnl_trades else 0

    # Days in market
    days_in = (df["Position"] != 0).sum()
    exposure = days_in / n_days if n_days > 0 else 0

    metrics = {
        "total_return": total_ret,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "n_trades": n_trades,
        "win_rate": win_rate,
        "avg_trade": avg_trade,
        "exposure": exposure,
        "n_days": n_days,
    }

    return df, metrics, trades


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("⚙️ Parâmetros")

pair = st.sidebar.selectbox("Par de Ativos", ["WINFUT vs DIFUT", "WDOFUT vs DIFUT"])
col_a = pair.split(" vs ")[0]
col_b = pair.split(" vs ")[1]

st.sidebar.markdown("---")
st.sidebar.subheader("Análise")
window = st.sidebar.slider("Janela Rolling Z-Score", 5, 40, 20, 1)

st.sidebar.markdown("---")
st.sidebar.subheader("Backtest")
entry_z = st.sidebar.slider("Z-Score Entrada", 0.5, 3.5, 2.0, 0.1)
exit_z = st.sidebar.slider("Z-Score Saída", -1.0, 1.0, 0.0, 0.1)
stop_z = st.sidebar.slider("Stop Loss (Z adicional, 0=off)", 0.0, 3.0, 0.0, 0.5)

# ============================================================
# MAIN
# ============================================================
st.title("📈 B3 Pairs Trading Dashboard")
st.caption(f"**{pair}** | Janela: {window} | Entrada: ±{entry_z}σ | Saída: {exit_z}σ")

df_raw = load_data(pair)

if df_raw is None:
    st.error(f"Arquivo de dados não encontrado. Execute `python data_collector.py` primeiro.")
    st.stop()

# --- Analysis ---
df_analyzed, stats = compute_analysis(df_raw, col_a, col_b, window)

# --- Metrics Row ---
st.markdown("## 🔬 Análise Estatística")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Correlação", f"{stats['correlation']:.4f}")
c2.metric("Cointegração (p)", f"{stats['coint_pvalue']:.4f}",
          delta="Cointegrado" if stats['coint_pvalue'] < 0.05 else "Não cointegrado",
          delta_color="normal" if stats['coint_pvalue'] < 0.05 else "inverse")
c3.metric("Hedge Ratio (β)", f"{stats['beta']:.4f}")
c4.metric("ADF Spread (p)", f"{stats['adf_pvalue']:.4f}",
          delta="Estacionário" if stats['adf_pvalue'] < 0.05 else "Não estacionário",
          delta_color="normal" if stats['adf_pvalue'] < 0.05 else "inverse")
c5.metric("Meia-vida (dias)", f"{stats['half_life']:.1f}" if stats['half_life'] < 1000 else "∞")

# --- Charts ---
st.markdown("---")

# Prices normalized
fig_prices = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                           row_heights=[0.35, 0.3, 0.35],
                           subplot_titles=[
                               f"Preços Normalizados ({col_a} vs {col_b})",
                               "Spread",
                               "Z-Score + Sinais de Entrada/Saída",
                           ])

a_norm = (df_analyzed[col_a] - df_analyzed[col_a].mean()) / df_analyzed[col_a].std()
b_norm = (df_analyzed[col_b] - df_analyzed[col_b].mean()) / df_analyzed[col_b].std()

fig_prices.add_trace(go.Scatter(x=df_analyzed.index, y=a_norm, name=col_a, line=dict(color="#636EFA")), row=1, col=1)
fig_prices.add_trace(go.Scatter(x=df_analyzed.index, y=b_norm, name=col_b, line=dict(color="#EF553B")), row=1, col=1)

# Spread
fig_prices.add_trace(go.Scatter(x=df_analyzed.index, y=df_analyzed["Spread"], name="Spread",
                                line=dict(color="#FFA15A")), row=2, col=1)
fig_prices.add_hline(y=df_analyzed["Spread"].mean(), line_dash="dash", line_color="gray", row=2, col=1)

# Z-Score
fig_prices.add_trace(go.Scatter(x=df_analyzed.index, y=df_analyzed["Z_Score"], name="Z-Score",
                                line=dict(color="#636EFA")), row=3, col=1)
fig_prices.add_hline(y=0, line_dash="dash", line_color="gray", row=3, col=1)
fig_prices.add_hline(y=entry_z, line_dash="dash", line_color="red", row=3, col=1,
                     annotation_text=f"Venda ({entry_z}σ)")
fig_prices.add_hline(y=-entry_z, line_dash="dash", line_color="green", row=3, col=1,
                     annotation_text=f"Compra (-{entry_z}σ)")
if exit_z != 0:
    fig_prices.add_hline(y=exit_z, line_dash="dot", line_color="orange", row=3, col=1)
    fig_prices.add_hline(y=-exit_z, line_dash="dot", line_color="orange", row=3, col=1)

fig_prices.update_layout(height=750, template="plotly_dark", showlegend=True,
                         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig_prices, use_container_width=True)

# --- Backtest ---
st.markdown("## 📊 Backtest")

df_bt, metrics, trades = run_backtest(df_analyzed, col_a, col_b, entry_z, exit_z, stop_z, stats["beta"])

# Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Retorno Total", f"{metrics['total_return']*100:.2f}%",
          delta_color="normal" if metrics['total_return'] >= 0 else "inverse")
m2.metric("Sharpe Ratio", f"{metrics['sharpe']:.2f}")
m3.metric("Max Drawdown", f"{metrics['max_drawdown']*100:.2f}%")
m4.metric("Nº Trades", f"{metrics['n_trades']}")

m5, m6, m7, m8 = st.columns(4)
m5.metric("Win Rate", f"{metrics['win_rate']*100:.1f}%")
m6.metric("Retorno Médio/Trade", f"{metrics['avg_trade']*100:.3f}%")
m7.metric("Exposição ao Mercado", f"{metrics['exposure']*100:.1f}%")
m8.metric("Dias Analisados", f"{metrics['n_days']}")

# Equity curve
fig_bt = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                       row_heights=[0.6, 0.4],
                       subplot_titles=["Curva de Equity", "Posição"])

fig_bt.add_trace(go.Scatter(x=df_bt.index, y=df_bt["Cum_Return"], name="Estratégia",
                             line=dict(color="#00CC96", width=2),
                             fill="tozeroy", fillcolor="rgba(0,204,150,0.1)"), row=1, col=1)
fig_bt.add_trace(go.Scatter(x=df_bt.index, y=df_bt["BH_A"], name=f"Buy & Hold {col_a}",
                             line=dict(color="#636EFA", width=1, dash="dot")), row=1, col=1)

# Drawdown shading
cum_max = df_bt["Cum_Return"].cummax()
dd = (df_bt["Cum_Return"] - cum_max) / cum_max
fig_bt.add_trace(go.Scatter(x=df_bt.index, y=dd, name="Drawdown",
                             line=dict(color="red", width=0),
                             fill="tozeroy", fillcolor="rgba(255,0,0,0.15)"), row=1, col=1)

# Position
colors = df_bt["Position"].map({1: "green", -1: "red", 0: "gray"}).fillna("gray")
fig_bt.add_trace(go.Bar(x=df_bt.index, y=df_bt["Position"], name="Posição",
                         marker_color=colors.tolist()), row=2, col=1)

# Trade markers
for t in trades:
    entry_date = df_bt.index[t["entry"]]
    exit_date = df_bt.index[t["exit"]]
    entry_val = df_bt["Cum_Return"].iloc[t["entry"]]
    exit_val = df_bt["Cum_Return"].iloc[t["exit"]]
    fig_bt.add_trace(go.Scatter(x=[entry_date], y=[entry_val], mode="markers",
                                marker=dict(symbol="triangle-up" if t["side"] == "long" else "triangle-down",
                                            size=10, color="lime" if t["side"] == "long" else "red"),
                                showlegend=False), row=1, col=1)
    fig_bt.add_trace(go.Scatter(x=[exit_date], y=[exit_val], mode="markers",
                                marker=dict(symbol="x", size=8, color="white"),
                                showlegend=False), row=1, col=1)

fig_bt.update_layout(height=600, template="plotly_dark", showlegend=True,
                     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
fig_bt.update_yaxes(title_text="Retorno Acumulado", row=1, col=1)
fig_bt.update_yaxes(title_text="Posição", row=2, col=1)

st.plotly_chart(fig_bt, use_container_width=True)

# --- Trade Log ---
if trades:
    with st.expander(f"📋 Log de Trades ({len(trades)} operações)", expanded=False):
        trade_data = []
        for i, t in enumerate(trades):
            entry_date = df_bt.index[t["entry"]]
            exit_date = df_bt.index[t["exit"]]
            entry_z_val = df_bt["Z_Score"].iloc[t["entry"]]
            exit_z_val = df_bt["Z_Score"].iloc[t["exit"]]
            entry_eq = df_bt["Cum_Return"].iloc[t["entry"]]
            exit_eq = df_bt["Cum_Return"].iloc[t["exit"]]
            pnl = (exit_eq - entry_eq) / entry_eq * 100
            duration = (exit_date - entry_date).days
            trade_data.append({
                "#": i + 1,
                "Lado": "Long" if t["side"] == "long" else "Short",
                "Entrada": entry_date.strftime("%Y-%m-%d"),
                "Saída": exit_date.strftime("%Y-%m-%d"),
                "Dias": duration,
                "Z Entrada": f"{entry_z_val:.2f}",
                "Z Saída": f"{exit_z_val:.2f}",
                "P&L (%)": f"{pnl:.3f}%",
                "Resultado": "✅" if pnl > 0 else "❌",
            })
        st.dataframe(pd.DataFrame(trade_data), use_container_width=True, hide_index=True)

# --- Raw Data ---
with st.expander("📁 Dados Brutos"):
    st.dataframe(df_bt[[col_a, col_b, "Spread", "Z_Score", "Position", "Strategy_Ret", "Cum_Return"]],
                 use_container_width=True)

# --- Footer ---
st.markdown("---")
st.caption("⚠️ Fins educacionais. Não constitui recomendação de investimento. | B3 Pairs Trading Dashboard")
