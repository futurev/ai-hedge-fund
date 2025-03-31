import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def identify_candlestick_patterns(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify major candlestick patterns in the price data.
    
    Args:
        prices_df: DataFrame with OHLC data
    
    Returns:
        DataFrame with identified candlestick patterns
    """
    patterns = []

    for i in range(1, len(prices_df) - 3):
        current = prices_df.iloc[i]
        prev = prices_df.iloc[i - 1]
        next = prices_df.iloc[i + 1]
        next_next = prices_df.iloc[i + 2]
        next_next_next = prices_df.iloc[i + 3]

        # Bullish Single Candle Patterns
        if current['close'] > current['open'] and (current['open'] - current['low']) > 2 * (current['close'] - current['open']):
            patterns.append((current.name, 'Hammer'))
        elif current['close'] > current['open'] and (current['high'] - current['close']) > 2 * (current['close'] - current['open']):
            patterns.append((current.name, 'Inverted Hammer'))

        # Bearish Single Candle Patterns
        elif current['open'] > current['close'] and (current['high'] - current['open']) > 2 * (current['open'] - current['close']):
            patterns.append((current.name, 'Shooting Star'))
        elif current['open'] > current['close'] and (current['open'] - current['low']) > 2 * (current['open'] - current['close']):
            patterns.append((current.name, 'Hanging Man'))

        # Continuity Single Candle Patterns
        elif abs(current['close'] - current['open']) < (0.1 * (current['high'] - current['low'])):
            patterns.append((current.name, 'Doji'))
        elif abs(current['close'] - current['open']) < (0.1 * (current['high'] - current['low'])) and (current['high'] - current['low']) > 2 * abs(current['close'] - current['open']):
            patterns.append((current.name, 'Spinning Top'))

        # Bullish Set of Candles Patterns
        if prev['close'] < prev['open'] and current['close'] > current['open'] and current['close'] > prev['open'] and current['open'] < prev['close']:
            patterns.append((current.name, 'Bullish Engulfing'))
        elif prev['close'] < prev['open'] and current['close'] < current['open'] and next['close'] > next['open'] and next['close'] > (prev['close'] + prev['open']) / 2:
            patterns.append((next.name, 'Morning Star'))
        elif prev['close'] < prev['open'] and current['close'] > current['open'] and next['close'] > next['open'] and next_next['close'] > next_next['open']:
            patterns.append((next_next.name, 'Three White Soldiers'))

        # Bearish Set of Candles Patterns
        if prev['close'] > prev['open'] and current['close'] < current['open'] and current['open'] > prev['close'] and current['close'] < prev['open']:
            patterns.append((current.name, 'Bearish Engulfing'))
        elif prev['close'] > prev['open'] and current['close'] > current['open'] and next['close'] < next['open'] and next['close'] < (prev['close'] + prev['open']) / 2:
            patterns.append((next.name, 'Evening Star'))
        elif prev['close'] > prev['open'] and current['close'] < current['open'] and next['close'] < next['open'] and next_next['close'] < next_next['open']:
            patterns.append((next_next.name, 'Three Black Crows'))

        # Continuity Set of Candles Patterns
        if current['close'] > current['open'] and next['close'] < next['open'] and next_next['close'] < next_next['open'] and next_next_next['close'] > next_next_next['open']:
            patterns.append((next_next_next.name, 'Rising Three Methods'))
        elif current['close'] < current['open'] and next['close'] > next['open'] and next_next['close'] > next_next['open'] and next_next_next['close'] < next_next_next['open']:
            patterns.append((next_next_next.name, 'Falling Three Methods'))
    
    patterns_df = pd.DataFrame(patterns, columns=['Date', 'Pattern'])
    return patterns_df

def plot_candlestick_patterns(prices_df: pd.DataFrame, patterns_df: pd.DataFrame):
    """
    Plot candlestick patterns on the price chart.
    
    Args:
        prices_df: DataFrame with OHLC data
        patterns_df: DataFrame with identified candlestick patterns
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(prices_df.index, prices_df['close'], label='Close Price')
    
    for pattern in patterns_df.itertuples():
        date = pattern.Date
        name = pattern.Pattern
        ax.annotate(name, (mdates.date2num(date), prices_df.loc[date, 'close']),
                    xytext=(mdates.date2num(date), prices_df.loc[date, 'close'] + 2),
                    arrowprops=dict(facecolor='black', shrink=0.05),
                    fontsize=9, color='red')

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid()
    plt.title('Candlestick Patterns')
    plt.show()

# Example usage
if __name__ == "__main__":
    data = {
        "date": pd.date_range(start="2022-01-01", periods=100, freq="D"),
        "open": pd.Series(range(100), dtype="float"),
        "high": pd.Series(range(1, 101), dtype="float"),
        "low": pd.Series(range(100), dtype="float"),
        "close": pd.Series(range(1, 101), dtype="float"),
    }
    prices_df = pd.DataFrame(data)
    prices_df.set_index("date", inplace=True)

    # Identify candlestick patterns
    patterns_df = identify_candlestick_patterns(prices_df)
    print(patterns_df)

    # Plot the patterns
    plot_candlestick_patterns(prices_df, patterns_df)
