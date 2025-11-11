"""
Data Collector Module
Gathers market data, news, and technical indicators
"""
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import ta
from ..utils.logger import logger

class MarketDataCollector:
    """Collects market data from various sources"""
    
    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL']
        
    def get_current_prices(self) -> Dict[str, float]:
        """Get current prices for watchlist symbols"""
        prices = {}
        for symbol in self.symbols:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='1d')
                if not data.empty:
                    prices[symbol] = data['Close'].iloc[-1]
            except Exception as e:
                logger.error(f"Error fetching price for {symbol}: {e}")
        return prices
    
    def get_historical_data(self, symbol: str, period: str = '1mo') -> pd.DataFrame:
        """Get historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            return ticker.history(period=period)
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_indicators(self, symbol: str) -> Dict[str, float]:
        """Calculate technical indicators"""
        try:
            df = self.get_historical_data(symbol, period='3mo')
            if df.empty:
                return {}
            
            # Calculate indicators
            indicators = {}
            
            # Moving Averages
            indicators['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20).iloc[-1]
            indicators['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50).iloc[-1]
            indicators['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12).iloc[-1]
            
            # RSI
            indicators['RSI'] = ta.momentum.rsi(df['Close'], window=14).iloc[-1]
            
            # MACD
            macd = ta.trend.MACD(df['Close'])
            indicators['MACD'] = macd.macd().iloc[-1]
            indicators['MACD_Signal'] = macd.macd_signal().iloc[-1]
            indicators['MACD_Diff'] = macd.macd_diff().iloc[-1]
            
            # Bollinger Bands
            bollinger = ta.volatility.BollingerBands(df['Close'])
            indicators['BB_High'] = bollinger.bollinger_hband().iloc[-1]
            indicators['BB_Low'] = bollinger.bollinger_lband().iloc[-1]
            indicators['BB_Mid'] = bollinger.bollinger_mavg().iloc[-1]
            
            # Volume
            indicators['Volume'] = df['Volume'].iloc[-1]
            indicators['Volume_SMA_20'] = df['Volume'].rolling(window=20).mean().iloc[-1]
            
            # Price action
            indicators['Current_Price'] = df['Close'].iloc[-1]
            indicators['Price_Change_1D'] = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100)
            indicators['Price_Change_5D'] = ((df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6] * 100) if len(df) > 6 else 0
            
            return indicators
        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            return {}
    
    def get_market_sentiment(self) -> Dict[str, any]:
        """Get overall market sentiment indicators"""
        try:
            # VIX for volatility
            vix = yf.Ticker('^VIX')
            vix_data = vix.history(period='1d')
            vix_level = vix_data['Close'].iloc[-1] if not vix_data.empty else None
            
            # SPY for market trend
            spy = yf.Ticker('SPY')
            spy_data = spy.history(period='3mo')
            
            sentiment = {}
            if not spy_data.empty:
                current_price = spy_data['Close'].iloc[-1]
                sma_200 = spy_data['Close'].rolling(window=200).mean().iloc[-1] if len(spy_data) >= 200 else None
                
                sentiment['VIX'] = vix_level
                sentiment['SPY_Price'] = current_price
                sentiment['SPY_vs_SMA200'] = 'Above' if sma_200 and current_price > sma_200 else 'Below'
                sentiment['Market_Regime'] = self._classify_regime(vix_level, current_price, sma_200)
            
            return sentiment
        except Exception as e:
            logger.error(f"Error getting market sentiment: {e}")
            return {}
    
    def _classify_regime(self, vix: Optional[float], price: float, sma_200: Optional[float]) -> str:
        """Classify market regime"""
        if vix is None or sma_200 is None:
            return 'Unknown'
        
        if vix > 30:
            return 'Crisis'
        elif vix > 20:
            return 'High Volatility'
        elif price > sma_200 and vix < 20:
            return 'Bull Trending'
        elif price < sma_200:
            return 'Bear Trending'
        else:
            return 'Range Bound'


class NewsCollector:
    """Collects news and sentiment data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = 'https://newsapi.org/v2'
    
    def get_market_news(self, query: str = 'stock market', max_articles: int = 5) -> List[Dict]:
        """Get recent market news"""
        if not self.api_key:
            logger.warning("News API key not configured, skipping news collection")
            return []
        
        try:
            url = f"{self.base_url}/everything"
            params = {
                'q': query,
                'apiKey': self.api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': max_articles
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            articles = response.json().get('articles', [])
            return [{
                'title': article['title'],
                'description': article['description'],
                'source': article['source']['name'],
                'published': article['publishedAt']
            } for article in articles]
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    def get_symbol_news(self, symbol: str, max_articles: int = 3) -> List[Dict]:
        """Get news for a specific symbol"""
        return self.get_market_news(query=symbol, max_articles=max_articles)
