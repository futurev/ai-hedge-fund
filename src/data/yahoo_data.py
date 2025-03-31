import yfinance as yf
import pandas as pd
import os
import time
from datetime import datetime, timedelta
from newsapi import NewsApiClient

DATA_DIR = 'data_cache'  # Directory to save data
NEWS_API_KEY = 'your_news_api_key'  # Replace with your News API key

# Initialize News API client
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def fetch_ticker_data(ticker, interval='1d', period='1y'):
    """
    Fetch ticker data from Yahoo Finance API.
    
    Args:
        ticker (str): The ticker symbol.
        interval (str): Data interval (valid intervals: '1s', '1m', '1h', '1d', etc.).
        period (str): Data period (valid periods: '1d', '7d', '1mo', '6mo', '1y', '5y', 'max').
    
    Returns:
        pd.DataFrame: DataFrame with the ticker data.
    """
    ticker_data = yf.download(ticker, period=period, interval=interval)
    return ticker_data

def cache_ticker_data(ticker, data, interval='1d'):
    """
    Cache the fetched ticker data to disk.
    
    Args:
        ticker (str): The ticker symbol.
        data (pd.DataFrame): DataFrame with the ticker data.
        interval (str): Data interval.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    file_path = os.path.join(DATA_DIR, f'{ticker}_{interval}.csv')
    data.to_csv(file_path)

def estimate_disk_space_needed(data):
    """
    Estimate the disk space needed to store the data.
    
    Args:
        data (pd.DataFrame): DataFrame with the ticker data.
    
    Returns:
        float: Estimated disk space in MB.
    """
    csv_size = data.to_csv(None).encode('utf-8')
    size_in_mb = len(csv_size) / (1024 * 1024)
    return size_in_mb

def fetch_and_cache_all_data():
    """
    Fetch and cache data for all intervals for favorite tickers.
    """
    intervals = {'1s': '1d', '1m': '7d', '1h': '60d', '1d': '1y'}
    for ticker in FAVORITE_LIST:
        for interval, period in intervals.items():
            data = fetch_ticker_data(ticker, interval=interval, period=period)
            cache_ticker_data(ticker, data, interval=interval)

def fetch_all_historical_data(ticker):
    """
    Fetch all historical data for a ticker from Yahoo Finance.
    
    Args:
        ticker (str): The ticker symbol.
    
    Returns:
        pd.DataFrame: DataFrame with the ticker data.
    """
    ticker_data = yf.download(ticker, period="max")
    return ticker_data

def resample_and_cache_data(ticker):
    """
    Resample and cache data to different intervals.
    
    Args:
        ticker (str): The ticker symbol.
    """
    file_path = os.path.join(DATA_DIR, f'{ticker}_1s.csv')
    data = pd.read_csv(file_path, index_col='Datetime', parse_dates=True)
    
    # Resample to different intervals
    minute_data = data.resample('1T').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })
    hour_data = data.resample('1H').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })
    day_data = data.resample('1D').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })
    
    # Cache the resampled data
    minute_data.to_csv(os.path.join(DATA_DIR, f'{ticker}_1min.csv'))
    hour_data.to_csv(os.path.join(DATA_DIR, f'{ticker}_1h.csv'))
    day_data.to_csv(os.path.join(DATA_DIR, f'{ticker}_1d.csv'))

def fetch_and_cache_all_historical_data():
    """
    Fetch and cache all historical data for favorite tickers.
    """
    total_size = 0
    for ticker in FAVORITE_LIST:
        data = fetch_all_historical_data(ticker)
        cache_ticker_data(ticker, data)
        resample_and_cache_data(ticker)
        size = estimate_disk_space_needed(data)
        total_size += size
        print(f"Ticker: {ticker}, Estimated Size: {size:.2f} MB")
    
    print(f"Total Estimated Disk Space Needed: {total_size:.2f} MB")

def update_favorite_and_trending_stocks(trending_stocks):
    """
    Update and save data for favorite and trending stocks.
    
    Args:
        trending_stocks (list): List of trending stock tickers.
    """
    current_time = datetime.now()
    market_open = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
    
    while current_time < market_close:
        for ticker in FAVORITE_LIST + trending_stocks:
            data = fetch_ticker_data(ticker, interval='1m')
            cache_ticker_data(ticker, data, interval='1m')
        
        # Sleep for 1 minute before fetching the next batch of data
        time.sleep(60)
        current_time = datetime.now()

    # At market close, fetch all data intervals and cache them
    fetch_and_cache_all_data()

def get_news_sentiment(ticker):
    """
    Fetch news sentiment for a given ticker.
    
    Args:
        ticker (str): The ticker symbol.
    
    Returns:
        float: Average sentiment score of the news articles.
    """
    news = newsapi.get_everything(q=ticker, language='en', sort_by='relevancy', page_size=20)
    sentiment_score = 0
    if news['totalResults'] > 0:
        for article in news['articles']:
            # Simplified sentiment analysis (positive if title contains positive words)
            positive_words = ['up', 'rise', 'gains', 'positive', 'growth']
            negative_words = ['down', 'fall', 'loss', 'negative', 'decline']
            title = article['title'].lower()
            sentiment_score += sum(word in title for word in positive_words)
            sentiment_score -= sum(word in title for word in negative_words)
        sentiment_score /= news['totalResults']
    return sentiment_score

def fetch_nyse_nasdaq_tickers():
    """
    Fetch the list of tickers listed on NYSE and NASDAQ.
    
    Returns:
        list: List of tickers.
    """
    nyse_tickers = pd.read_csv('https://pkgstore.datahub.io/core/nyse-other-listings/nyse-listed_csv/data/nyse-listed_csv.csv')['ACT Symbol'].tolist()
    nasdaq_tickers = pd.read_csv('https://pkgstore.datahub.io/core/nasdaq-listings/nasdaq-listed_csv/data/nasdaq-listed_csv.csv')['Symbol'].tolist()
    return nyse_tickers + nasdaq_tickers

def identify_trending_stocks():
    """
    Identify trending stocks based on price change, trading volume, news sentiment, market capitalization, and price range.
    
    Returns:
        list: List of trending stock tickers.
    """
    tickers = fetch_nyse_nasdaq_tickers()
    trending_stocks = []
    
    for ticker in tickers:
        try:
            data = fetch_ticker_data(ticker, interval='1d', period='1mo')
            if len(data) < 2:
                continue
            latest_data = data.iloc[-1]
            prev_data = data.iloc[-2]
            
            price_change = (latest_data['Close'] - prev_data['Close']) / prev_data['Close']
            volume_change = (latest_data['Volume'] - prev_data['Volume']) / prev_data['Volume']
            news_sentiment = get_news_sentiment(ticker)
            market_cap = yf.Ticker(ticker).info['marketCap']
            
            if price_change > 0.05 and volume_change > 0.1 and news_sentiment > 0 and market_cap > 1e10:
                trending_stocks.append(ticker)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
    
    return trending_stocks

# Example usage
if __name__ == "__main__":
    trending_stocks = identify_trending_stocks()
    print(f"Trending Stocks: {trending_stocks}")
    update_favorite_and_trending_stocks(trending_stocks)
    fetch_and_cache_all_historical_data()
