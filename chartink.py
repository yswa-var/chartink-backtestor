import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


def backtest(csv_file, days_forward):
    df = pd.read_csv(csv_file)

    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')

    df = df.sort_values('date')
    results = []

    for _, row in df.iterrows():
        symbol = row['symbol']
        date = row['date']

        end_date = date + timedelta(days=days_forward)

        stock_data = yf.download(f"{symbol}.NS", start=date, end=end_date)

        if not stock_data.empty:
            high_after_x_days = stock_data['High'].max()
            low_after_x_days = stock_data['Low'].min()

            results.append({
                'date': date,
                'symbol': symbol,
                'start price': int(stock_data.iloc[0]['Adj Close']),
                'sector': row['sector'],
                'marketcapname': row['marketcapname'],
                'high_after_x_days': high_after_x_days,
                'low_after_x_days': low_after_x_days
            })

    results_df = pd.DataFrame(results)

    return results_df


csv_file = 'try1.csv'
days_forward = 25

results = backtest(csv_file, days_forward)
print(results)

results.to_csv(f'{csv_file}_{days_forward}_days.csv', index=False)