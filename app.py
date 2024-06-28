from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


def backtest(df, days_forward_list):
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
                'start price': float(stock_data.iloc[0]['Adj Close']),
                'max high': float(stock_data['High'].max()),
                'max low': float(stock_data['Low'].min())
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


def calculate_percentage_change(row, column):
    return (row[column] - row['start price']) / row['start price'] * 100


def process_data(df, days_forward_list):
    # Calculate percentage changes
    for days in days_forward_list:
        df[f'high_{days}_days_change'] = df.apply(
            lambda row: calculate_percentage_change(row, f'high_after_{days}_days'), axis=1)
        df[f'low_{days}_days_change'] = df.apply(lambda row: calculate_percentage_change(row, f'low_after_{days}_days'),
                                                 axis=1)

    return df


def plot_sector_analysis(df):
    sector_high = df.groupby('sector')[
        ['high_5_days_change', 'high_10_days_change', 'high_20_days_change', 'high_30_days_change']].mean().sort_values(
        'high_30_days_change', ascending=False)
    sector_low = df.groupby('sector')[
        ['low_5_days_change', 'low_10_days_change', 'low_20_days_change', 'low_30_days_change']].mean().sort_values(
        'low_30_days_change', ascending=False)

    fig = go.Figure()
    for col in sector_high.columns:
        fig.add_trace(
            go.Bar(x=sector_high.index, y=sector_high[col], name=f'High {col.split("_")[1]} days', marker_color='green',
                   opacity=0.6))
    for col in sector_low.columns:
        fig.add_trace(
            go.Bar(x=sector_low.index, y=sector_low[col], name=f'Low {col.split("_")[1]} days', marker_color='red',
                   opacity=0.6))

    fig.update_layout(
        title='Average Percentage Change by Sector',
        xaxis_title='Sector',
        yaxis_title='Average Percentage Change',
        barmode='group'
    )

    return fig


def plot_marketcap_analysis(df):
    marketcap_high = df.groupby('marketcapname')[
        ['high_5_days_change', 'high_10_days_change', 'high_20_days_change', 'high_30_days_change']].mean().sort_values(
        'high_30_days_change', ascending=False)
    marketcap_low = df.groupby('marketcapname')[
        ['low_5_days_change', 'low_10_days_change', 'low_20_days_change', 'low_30_days_change']].mean().sort_values(
        'low_30_days_change', ascending=False)

    fig = go.Figure()
    for col in marketcap_high.columns:
        fig.add_trace(go.Bar(x=marketcap_high.index, y=marketcap_high[col], name=f'High {col.split("_")[1]} days',
                             marker_color='green', opacity=0.6))
    for col in marketcap_low.columns:
        fig.add_trace(go.Bar(x=marketcap_low.index, y=marketcap_low[col], name=f'Low {col.split("_")[1]} days',
                             marker_color='red', opacity=0.6))

    fig.update_layout(
        title='Average Percentage Change by Market Cap',
        xaxis_title='Market Cap',
        yaxis_title='Average Percentage Change',
        barmode='group'
    )

    return fig


def main():
    st.title('Backtest Analysis')
    # -------------------------------------
    days_forward_list = [5, 10, 20, 30]
    # ------------------------------------
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')

        df = backtest(df, days_forward_list)

        df = process_data(df, days_forward_list)
        st.subheader('Data Preview')
        st.write(df.head())

        st.subheader('Sector Analysis')
        sector_fig = plot_sector_analysis(df)
        st.plotly_chart(sector_fig)

        st.subheader('Market Cap Analysis')
        marketcap_fig = plot_marketcap_analysis(df)
        st.plotly_chart(marketcap_fig)

        st.subheader('Analysis Report')



if __name__ == "__main__":
    main()
