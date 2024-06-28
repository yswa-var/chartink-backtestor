import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def calculate_percentage_change(row, column):
    return (row[column] - row['start price']) / row['start price'] * 100


def process_data(df):
    # Calculate percentage changes
    for days in [5, 10, 20, 30]:
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

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df = process_data(df)

        st.subheader('Data Preview')
        st.write(df.head())

        st.subheader('Sector Analysis')
        sector_fig = plot_sector_analysis(df)
        st.plotly_chart(sector_fig)

        st.subheader('Market Cap Analysis')
        marketcap_fig = plot_marketcap_analysis(df)
        st.plotly_chart(marketcap_fig)

        st.subheader('Analysis Report')
        st.write("""
        This analysis report provides insights into the performance of the scanner across different sectors and market capitalizations.

        1. Sector Performance:
           - The bar chart shows the average percentage change for highs and lows across different time periods (5, 10, 20, and 30 days) for each sector.
           - Sectors with higher positive bars for 'High' indicate better performance in terms of price increases.
           - Sectors with lower negative bars for 'Low' indicate better performance in terms of minimizing price decreases.

        2. Market Cap Performance:
           - Similar to the sector analysis, this chart shows the average percentage change for highs and lows across different time periods for each market cap category.
           - This helps identify which market cap segments (e.g., Large Cap, Mid Cap) tend to perform better with this scanner.

        3. Interpretation:
           - Look for sectors and market cap categories with consistently high positive changes for 'High' bars and minimal negative changes for 'Low' bars.
           - These represent areas where the scanner seems to be most effective in identifying stocks with potential for price increases and limited downside.

        4. Recommendations:
           - Focus on sectors and market cap categories that show the best overall performance.
           - Consider adjusting the scanner parameters or creating separate scanners optimized for the top-performing sectors or market caps.
           - Regularly update this analysis as new data becomes available to track changes in performance over time.

        Remember that past performance doesn't guarantee future results, and always combine these insights with other forms of analysis and risk management strategies.
        """)


if __name__ == "__main__":
    main()