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
    return df[['Close']]

def get_difut_proxy(start_date, end_date):
    print(f"Buscando proxy DIFUT (DI1) de {start_date} até {end_date}...")
    
    available_dates = yd.di1.available_trade_dates()
    start_dt = pd.to_datetime(start_date).date()
    end_dt = pd.to_datetime(end_date).date()
    
    target_dates = [d for d in available_dates if start_dt <= d <= end_dt]
    # Pegar os últimos 60 dias
    target_dates = target_dates[-60:]
    
    di_data = []
    
    print(f"Buscando dados para {len(target_dates)} datas...")
    for date in target_dates:
        try:
            df_di = yd.di1.data(dates=date)
            if not df_di.is_empty():
                df_pd = df_di.to_pandas()
                # Escolher vencimento próximo a 2 anos (500 dias úteis)
                # Coluna: BDaysToExp, Taxa: SettlementRate
                if 'BDaysToExp' in df_pd.columns:
                    df_pd['diff'] = abs(df_pd['BDaysToExp'] - 500)
                    closest = df_pd.sort_values('diff').iloc[0]
                    di_data.append({'Date': date, 'DI_Rate': closest['SettlementRate']})
        except Exception as e:
            continue
            
    if not di_data:
        return pd.DataFrame(columns=['DI_Rate'])
        
    df = pd.DataFrame(di_data).set_index('Date')
    return df

if __name__ == "__main__":
    end = datetime.now()
    start = end - timedelta(days=180)
    
    win_df = get_winfut_proxy(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    di_df = get_difut_proxy(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    
    # Merge data
    combined = win_df.join(di_df, how='inner')
    combined.columns = ['WINFUT', 'DIFUT']
    
    print(f"Dados combinados: {len(combined)} linhas")
    if not combined.empty:
        print(combined.head())
        combined.to_csv("historical_data.csv")
        print("Dados salvos em historical_data.csv")
    else:
        print("Nenhum dado combinado encontrado.")
