import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


def backtest(csv_file, days_forward_list):
    df = pd.read_csv(csv_file)

    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')

    df = df.sort_values('date')

    results = []

    for _, row in df.iterrows():
        symbol = row['symbol']
        date = row['date']

        max_days = max(days_forward_list)
        end_date = date + timedelta(days=max_days)

        stock_data = yf.download(f"{symbol}.NS", start=date, end=end_date)

        if not stock_data.empty:
            result = {
                'date': date,
                'symbol': symbol,
                'sector': row['sector'],
                'marketcapname': row['marketcapname'],
                'start price': int(stock_data.iloc[0]['Adj Close'])
            }

            for days in days_forward_list:
                relevant_data = stock_data[:days]
                if not relevant_data.empty:
                    high_after_x_days = relevant_data['High'].max()
                    low_after_x_days = relevant_data['Low'].min()

                    result[f'high_after_{days}_days'] = high_after_x_days
                    result[f'low_after_{days}_days'] = low_after_x_days
                else:
                    result[f'high_after_{days}_days'] = None
                    result[f'low_after_{days}_days'] = None

            results.append(result)

    results_df = pd.DataFrame(results)

    return results_df


csv_file = 'try1.csv'
days_forward_list = [5, 10, 20, 30]

results = backtest(csv_file, days_forward_list)
print(results)

results.to_csv(f'backtest_{csv_file}', index=False)