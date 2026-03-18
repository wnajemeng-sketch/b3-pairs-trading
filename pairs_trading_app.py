import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import numpy as np
import yfinance as yf
import pyield as yd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import threading

class PairsTradingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Pairs Trading Analyzer - B3")
        self.geometry("1200x800")
        ctk.set_appearance_mode("dark")
        ctk.set_color_scheme("blue")
        
        # Variables
        self.ticker1 = ctk.StringVar(value="^BVSP")
        self.ticker2 = ctk.StringVar(value="USDBRL=X")
        self.days_back = ctk.StringVar(value="60")
        self.results = {}
        self.df_data = None
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Input frame
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(input_frame, text="Ativo 1 (Ticker):", font=("Arial", 12)).pack(side="left", padx=5)
        ctk.CTkEntry(input_frame, textvariable=self.ticker1, width=150).pack(side="left", padx=5)
        
        ctk.CTkLabel(input_frame, text="Ativo 2 (Ticker):", font=("Arial", 12)).pack(side="left", padx=5)
        ctk.CTkEntry(input_frame, textvariable=self.ticker2, width=150).pack(side="left", padx=5)
        
        ctk.CTkLabel(input_frame, text="Dias para trás:", font=("Arial", 12)).pack(side="left", padx=5)
        ctk.CTkEntry(input_frame, textvariable=self.days_back, width=80).pack(side="left", padx=5)
        
        ctk.CTkButton(input_frame, text="Analisar", command=self.analyze_pair).pack(side="left", padx=5)
        
        # Results frame
        results_frame = ctk.CTkFrame(main_frame)
        results_frame.pack(fill="both", expand=True, pady=10)
        
        # Left side - Results text
        left_frame = ctk.CTkFrame(results_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(left_frame, text="Resultados da Análise:", font=("Arial", 14, "bold")).pack(anchor="w")
        
        self.results_text = ctk.CTkTextbox(left_frame, height=400, width=400)
        self.results_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Right side - Chart
        right_frame = ctk.CTkFrame(results_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(right_frame, text="Gráfico Z-Score:", font=("Arial", 14, "bold")).pack(anchor="w")
        
        self.canvas_frame = ctk.CTkFrame(right_frame)
        self.canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Bottom frame - Export button
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(bottom_frame, text="Exportar Resultados (CSV)", command=self.export_results).pack(side="left", padx=5)
        ctk.CTkButton(bottom_frame, text="Limpar", command=self.clear_results).pack(side="left", padx=5)
        
    def analyze_pair(self):
        try:
            ticker1 = self.ticker1.get().upper()
            ticker2 = self.ticker2.get().upper()
            days = int(self.days_back.get())
            
            if not ticker1 or not ticker2:
                messagebox.showerror("Erro", "Por favor, insira ambos os tickers.")
                return
            
            # Show loading message
            self.results_text.delete("1.0", "end")
            self.results_text.insert("end", "Carregando dados... Por favor aguarde.\n")
            self.update()
            
            # Run analysis in thread to avoid freezing
            thread = threading.Thread(target=self._run_analysis, args=(ticker1, ticker2, days))
            thread.daemon = True
            thread.start()
            
        except ValueError:
            messagebox.showerror("Erro", "Dias deve ser um número inteiro.")
    
    def _run_analysis(self, ticker1, ticker2, days):
        try:
            end = datetime.now()
            start = end - timedelta(days=days)
            
            # Fetch data
            self.results_text.delete("1.0", "end")
            self.results_text.insert("end", f"Buscando dados para {ticker1} e {ticker2}...\n")
            self.update()
            
            df1 = yf.download(ticker1, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), progress=False)
            df2 = yf.download(ticker2, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), progress=False)
            
            if isinstance(df1.columns, pd.MultiIndex):
                df1.columns = df1.columns.get_level_values(0)
            if isinstance(df2.columns, pd.MultiIndex):
                df2.columns = df2.columns.get_level_values(0)
            
            df1.index = pd.to_datetime(df1.index).date
            df2.index = pd.to_datetime(df2.index).date
            
            df_combined = df1[["Close"]].join(df2[["Close"]], how="inner")
            df_combined.columns = [ticker1, ticker2]
            
            if df_combined.empty:
                messagebox.showerror("Erro", "Nenhum dado encontrado para os tickers especificados.")
                return
            
            self.df_data = df_combined
            
            # Correlation
            correlation = df_combined[ticker1].corr(df_combined[ticker2])
            
            # Cointegration test
            score, p_value, _ = coint(df_combined[ticker1], df_combined[ticker2])
            
            # Hedge ratio
            Y = df_combined[ticker1]
            X = df_combined[ticker2]
            X = sm.add_constant(X)
            model = sm.OLS(Y, X).fit()
            beta = model.params[ticker2]
            intercept = model.params["const"]
            
            # Spread and Z-Score
            df_combined["Spread"] = df_combined[ticker1] - (beta * df_combined[ticker2] + intercept)
            spread_mean = df_combined["Spread"].mean()
            spread_std = df_combined["Spread"].std()
            df_combined["Z-Score"] = (df_combined["Spread"] - spread_mean) / spread_std
            
            # Calculate margin
            last_row = df_combined.tail(1)
            last_asset1 = last_row[ticker1].values[0]
            last_asset2 = last_row[ticker2].values[0]
            target_asset1 = (beta * last_asset2 + intercept) + spread_mean
            margin_pct = (target_asset1 / last_asset1 - 1) * 100
            
            # Display results
            self.results_text.delete("1.0", "end")
            results_text = f"""
ANÁLISE DE PAIRS TRADING
{'='*50}

Ativos Analisados:
  Ativo 1: {ticker1}
  Ativo 2: {ticker2}
  Período: {days} dias

ESTATÍSTICAS:
{'='*50}
Correlação de Pearson: {correlation:.4f}
P-valor Cointegração: {p_value:.4f}
Cointegrado (95%): {'SIM' if p_value < 0.05 else 'NÃO'}

Hedge Ratio (Beta): {beta:.4f}
Intercepto: {intercept:.4f}

SITUAÇÃO ATUAL:
{'='*50}
Preço {ticker1}: {last_asset1:.4f}
Preço {ticker2}: {last_asset2:.4f}
Spread Atual: {df_combined['Spread'].iloc[-1]:.4f}
Spread Médio: {spread_mean:.4f}
Desvio Padrão: {spread_std:.4f}

Z-Score do Spread: {df_combined['Z-Score'].iloc[-1]:.4f}

MARGEM DE MOVIMENTO:
{'='*50}
Preço-Alvo {ticker1}: {target_asset1:.4f}
Margem de Subida: {margin_pct:.2f}%

INTERPRETAÇÃO:
{'='*50}
"""
            
            if df_combined['Z-Score'].iloc[-1] > 2:
                results_text += f"{ticker1} está SOBRECOMPRADO em relação a {ticker2}.\nEspera-se queda de {ticker1} ou alta de {ticker2}."
            elif df_combined['Z-Score'].iloc[-1] < -2:
                results_text += f"{ticker1} está SOBREVENDIDO em relação a {ticker2}.\nEspera-se alta de {ticker1} ou queda de {ticker2}.\nMargem potencial de subida: {abs(margin_pct):.2f}%"
            else:
                results_text += "O spread está próximo da média. Sem sinal claro de entrada."
            
            self.results_text.insert("end", results_text)
            self.results = {
                "ticker1": ticker1,
                "ticker2": ticker2,
                "correlation": correlation,
                "p_value": p_value,
                "beta": beta,
                "intercept": intercept,
                "zscore": df_combined['Z-Score'].iloc[-1],
                "margin_pct": margin_pct
            }
            
            # Plot Z-Score
            self.plot_zscore(df_combined)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao analisar: {str(e)}")
    
    def plot_zscore(self, df):
        # Clear previous canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        # Create figure
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.plot(df["Z-Score"], color="blue", linewidth=2)
        ax.axhline(0, color="black", linestyle="--", alpha=0.5)
        ax.axhline(2, color="red", linestyle="--", alpha=0.5, label="Sobrecomprado (+2)")
        ax.axhline(-2, color="green", linestyle="--", alpha=0.5, label="Sobrevendido (-2)")
        ax.fill_between(range(len(df)), 2, 10, alpha=0.1, color="red")
        ax.fill_between(range(len(df)), -10, -2, alpha=0.1, color="green")
        
        ax.set_title("Z-Score do Spread")
        ax.set_ylabel("Z-Score")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def export_results(self):
        if self.df_data is None:
            messagebox.showwarning("Aviso", "Realize uma análise primeiro.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.df_data.to_csv(file_path)
            messagebox.showinfo("Sucesso", f"Dados exportados para {file_path}")
    
    def clear_results(self):
        self.results_text.delete("1.0", "end")
        self.df_data = None
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = PairsTradingApp()
    app.mainloop()
