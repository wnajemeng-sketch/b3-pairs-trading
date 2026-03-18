import yfinance as yf
import pandas as pd
import pyield as yd
from datetime import datetime, timedelta

def get_winfut_proxy(start_date, end_date):
    print(f"Buscando proxy WINFUT (^BVSP) de {start_date} até {end_date}...")
    df = yf.download("^BVSP", start=start_date, end=end_date)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index).date
    return df[["Close"]]

def get_wdofut_proxy(start_date, end_date):
    print(f"Buscando proxy WDOFUT (USDBRL=X) de {start_date} até {end_date}...")
    df = yf.download("USDBRL=X", start=start_date, end=end_date)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index).date
    return df[["Close"]]

def get_difut_proxy(start_date, end_date):
    print(f"Buscando proxy DIFUT (DI1) de {start_date} até {end_date}...")
    
    available_dates = yd.di1.available_trade_dates()
    start_dt = pd.to_datetime(start_date).date()
    end_dt = pd.to_datetime(end_date).date()
    
    target_dates = [d for d in available_dates if start_dt <= d <= end_dt]
    target_dates = target_dates[-60:]
    
    di_data = []
    
    print(f"Buscando dados para {len(target_dates)} datas...")
    for date in target_dates:
        try:
            df_di = yd.di1.data(dates=date)
            if not df_di.is_empty():
                df_pd = df_di.to_pandas()
                if "BDaysToExp" in df_pd.columns:
                    df_pd["diff"] = abs(df_pd["BDaysToExp"] - 500)
                    closest = df_pd.sort_values("diff").iloc[0]
                    di_data.append({"Date": date, "DI_Rate": closest["SettlementRate"]})
        except Exception as e:
            continue
            
    if not di_data:
        return pd.DataFrame(columns=["DI_Rate"])
        
    df = pd.DataFrame(di_data).set_index("Date")
    return df

if __name__ == "__main__":
    end = datetime.now()
    start = end - timedelta(days=180)
    
    # Coleta para WINFUT e DIFUT
    win_df = get_winfut_proxy(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    di_df = get_difut_proxy(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    
    combined_win_di = win_df.join(di_df, how="inner")
    combined_win_di.columns = ["WINFUT", "DIFUT"]
    
    print(f"Dados combinados WINFUT/DIFUT: {len(combined_win_di)} linhas")
    if not combined_win_di.empty:
        print(combined_win_di.head())
        combined_win_di.to_csv("historical_data_win_di.csv")
        print("Dados WINFUT/DIFUT salvos em historical_data_win_di.csv")
    else:
        print("Nenhum dado combinado WINFUT/DIFUT encontrado.")

    # Coleta para WDOFUT e DIFUT
    wdo_df = get_wdofut_proxy(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    
    combined_wdo_di = wdo_df.join(di_df, how="inner")
    combined_wdo_di.columns = ["WDOFUT", "DIFUT"]
    
    print(f"Dados combinados WDOFUT/DIFUT: {len(combined_wdo_di)} linhas")
    if not combined_wdo_di.empty:
        print(combined_wdo_di.head())
        combined_wdo_di.to_csv("historical_data_wdo_di.csv")
        print("Dados WDOFUT/DIFUT salvos em historical_data_wdo_di.csv")
    else:
        print("Nenhum dado combinado WDOFUT/DIFUT encontrado.")
