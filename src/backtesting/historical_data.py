"""
Historical Data Downloader
Downloads historical price data for backtesting
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional
import os


class HistoricalDataProvider:
    """Downloads and caches historical market data"""

    def __init__(self, cache_dir: str = "data/historical"):
        """Initialize data provider with cache directory"""
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get_stock_data(self, symbol: str, start_date: str, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Get historical stock data

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format (default: today)

        Returns:
            DataFrame with OHLCV data
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # Check cache first
        cache_file = f"{self.cache_dir}/{symbol}_{start_date}_{end_date}.csv"
        if os.path.exists(cache_file):
            print(f"📁 Loading {symbol} from cache...")
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)

        try:
            print(f"📥 Downloading {symbol} data from {start_date} to {end_date}...")
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)

            if df.empty:
                print(f"⚠️  No data available for {symbol}")
                return None

            # Save to cache
            df.to_csv(cache_file)
            print(f"✅ Downloaded {len(df)} days of {symbol} data")

            return df

        except Exception as e:
            print(f"❌ Error downloading {symbol}: {e}")
            return None

    def get_multiple_stocks(self, symbols: list, start_date: str, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        Get historical data for multiple stocks

        Args:
            symbols: List of stock symbols
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format

        Returns:
            Dictionary mapping symbol to DataFrame
        """
        data = {}
        for symbol in symbols:
            df = self.get_stock_data(symbol, start_date, end_date)
            if df is not None:
                data[symbol] = df

        return data

    def get_crypto_data(self, symbol: str, start_date: str, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Get historical crypto data

        Args:
            symbol: Crypto pair (e.g., 'BTC-USD')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format

        Returns:
            DataFrame with OHLCV data
        """
        # yfinance uses '-USD' suffix for crypto
        if 'USDT' in symbol:
            symbol = symbol.replace('USDT', '-USD')

        return self.get_stock_data(symbol, start_date, end_date)

    def calculate_available_range(self, symbol: str) -> tuple:
        """
        Calculate how far back data is available

        Returns:
            (earliest_date, latest_date) as strings
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="max")

            if df.empty:
                return None, None

            earliest = df.index[0].strftime('%Y-%m-%d')
            latest = df.index[-1].strftime('%Y-%m-%d')

            return earliest, latest

        except Exception as e:
            print(f"Error checking range for {symbol}: {e}")
            return None, None

    def get_past_n_years(self, symbol: str, years: int = 10) -> Optional[pd.DataFrame]:
        """
        Get data for the past N years

        Args:
            symbol: Symbol to download
            years: Number of years to go back

        Returns:
            DataFrame with historical data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)

        return self.get_stock_data(
            symbol,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )


if __name__ == "__main__":
    # Test the data provider
    provider = HistoricalDataProvider()

    print("\n" + "="*60)
    print("HISTORICAL DATA PROVIDER TEST")
    print("="*60)

    # Test stock data
    print("\n1. Testing Stock Data (AAPL - 10 years)")
    aapl = provider.get_past_n_years('AAPL', years=10)
    if aapl is not None:
        print(f"   ✅ Retrieved {len(aapl)} days of data")
        print(f"   📅 Range: {aapl.index[0]} to {aapl.index[-1]}")
        print(f"   💰 Price range: ${aapl['Close'].min():.2f} - ${aapl['Close'].max():.2f}")

    # Test crypto data
    print("\n2. Testing Crypto Data (BTC - max available)")
    earliest, latest = provider.calculate_available_range('BTC-USD')
    if earliest:
        print(f"   📅 BTC data available from {earliest} to {latest}")

    btc = provider.get_crypto_data('BTCUSDT', earliest, latest)
    if btc is not None:
        print(f"   ✅ Retrieved {len(btc)} days of BTC data")

    print("\n" + "="*60)
