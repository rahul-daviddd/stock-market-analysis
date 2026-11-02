import yfinance as yf

def fetch_historical_crypto(symbol: str):
    """
    Using Yahoo Finance as the primary Top-Tier Free provider. 
    It requires no API key, pulls directly from top exchanges (CoinMarketCap averages), 
    and gives you virtually unlimited requests for OHLCV data.
    """
    ticker = f"{symbol}-USD"
    crypto = yf.Ticker(ticker)
    
    # Get 1 year of daily data
    hist = crypto.history(period="1y")
    
    if hist.empty:
        raise ValueError(f"No data found for symbol {symbol}")
    
    return hist[['Open', 'High', 'Low', 'Close', 'Volume']].rename(
        columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}
    )
