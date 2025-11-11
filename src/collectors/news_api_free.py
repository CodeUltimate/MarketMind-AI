"""
Free News API Integration
Supports multiple free news API providers
"""
import requests
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class FreeNewsAPI:
    """
    Multi-provider news API client
    Supports: Alpaca, Finnhub, Alpha Vantage, Marketaux
    """

    def __init__(self):
        """Initialize with API keys from environment"""
        # Alpaca (you already have this!)
        self.alpaca_key = os.getenv('ALPACA_API_KEY')
        self.alpaca_secret = os.getenv('ALPACA_SECRET_KEY')

        # Finnhub (free: 60 calls/min)
        self.finnhub_key = os.getenv('FINNHUB_API_KEY')

        # Alpha Vantage (free: 25 calls/day)
        self.alphavantage_key = os.getenv('ALPHAVANTAGE_API_KEY')

        # Marketaux (free: 100 calls/day)
        self.marketaux_key = os.getenv('MARKETAUX_API_KEY')

    def get_news_alpaca(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Get news from Alpaca (UNLIMITED with paper account!)

        Best for: US stocks
        Rate limit: Unlimited with paper account
        """
        if not self.alpaca_key:
            return []

        try:
            url = "https://data.alpaca.markets/v1beta1/news"
            headers = {
                "APCA-API-KEY-ID": self.alpaca_key,
                "APCA-API-SECRET-KEY": self.alpaca_secret
            }

            params = {
                "symbols": symbol,
                "limit": limit,
                "sort": "desc"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            news_items = response.json().get('news', [])

            return [{
                'title': item.get('headline'),
                'summary': item.get('summary'),
                'source': item.get('source'),
                'url': item.get('url'),
                'published_at': item.get('created_at'),
                'symbols': item.get('symbols', []),
                'provider': 'alpaca'
            } for item in news_items]

        except Exception as e:
            print(f"Alpaca news error: {e}")
            return []

    def get_news_finnhub(self, symbol: str, days_back: int = 7) -> List[Dict]:
        """
        Get news from Finnhub (60 calls/min FREE)

        Best for: Stocks + Crypto + Global
        Rate limit: 60 calls/min
        """
        if not self.finnhub_key:
            return []

        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            url = "https://finnhub.io/api/v1/company-news"
            params = {
                "symbol": symbol,
                "from": start_date.strftime('%Y-%m-%d'),
                "to": end_date.strftime('%Y-%m-%d'),
                "token": self.finnhub_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            news_items = response.json()

            return [{
                'title': item.get('headline'),
                'summary': item.get('summary'),
                'source': item.get('source'),
                'url': item.get('url'),
                'published_at': datetime.fromtimestamp(item.get('datetime')).isoformat() if item.get('datetime') else None,
                'symbols': [symbol],
                'provider': 'finnhub'
            } for item in news_items]

        except Exception as e:
            print(f"Finnhub news error: {e}")
            return []

    def get_news_alphavantage(self, symbol: str, limit: int = 50) -> List[Dict]:
        """
        Get news + sentiment from Alpha Vantage (25 calls/day FREE)

        Best for: Sentiment analysis
        Rate limit: 25 calls/day
        """
        if not self.alphavantage_key:
            return []

        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": symbol,
                "apikey": self.alphavantage_key,
                "limit": limit
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            news_items = data.get('feed', [])

            return [{
                'title': item.get('title'),
                'summary': item.get('summary'),
                'source': item.get('source'),
                'url': item.get('url'),
                'published_at': item.get('time_published'),
                'symbols': [t['ticker'] for t in item.get('ticker_sentiment', [])],
                'sentiment_score': item.get('overall_sentiment_score', 0),
                'sentiment_label': item.get('overall_sentiment_label', 'neutral'),
                'provider': 'alphavantage'
            } for item in news_items]

        except Exception as e:
            print(f"Alpha Vantage news error: {e}")
            return []

    def get_news_marketaux(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Get news from Marketaux (100 calls/day FREE)

        Best for: Global coverage
        Rate limit: 100 calls/day
        """
        if not self.marketaux_key:
            return []

        try:
            url = "https://api.marketaux.com/v1/news/all"
            params = {
                "symbols": symbol,
                "limit": limit,
                "api_token": self.marketaux_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            news_items = data.get('data', [])

            return [{
                'title': item.get('title'),
                'summary': item.get('description'),
                'source': item.get('source'),
                'url': item.get('url'),
                'published_at': item.get('published_at'),
                'symbols': item.get('entities', []),
                'sentiment': item.get('sentiment'),
                'provider': 'marketaux'
            } for item in news_items]

        except Exception as e:
            print(f"Marketaux news error: {e}")
            return []

    def get_news(self, symbol: str, limit: int = 10, providers: List[str] = None) -> List[Dict]:
        """
        Get news from multiple providers (fallback chain)

        Args:
            symbol: Stock symbol
            limit: Number of articles
            providers: List of providers to try (default: all available)

        Returns:
            Combined list of news articles
        """
        if providers is None:
            # Try in order of best free tier
            providers = ['alpaca', 'finnhub', 'marketaux', 'alphavantage']

        all_news = []

        for provider in providers:
            try:
                if provider == 'alpaca' and self.alpaca_key:
                    news = self.get_news_alpaca(symbol, limit)
                    all_news.extend(news)
                    if len(all_news) >= limit:
                        break

                elif provider == 'finnhub' and self.finnhub_key:
                    news = self.get_news_finnhub(symbol)
                    all_news.extend(news)
                    if len(all_news) >= limit:
                        break

                elif provider == 'alphavantage' and self.alphavantage_key:
                    news = self.get_news_alphavantage(symbol, limit)
                    all_news.extend(news)
                    if len(all_news) >= limit:
                        break

                elif provider == 'marketaux' and self.marketaux_key:
                    news = self.get_news_marketaux(symbol, limit)
                    all_news.extend(news)
                    if len(all_news) >= limit:
                        break

            except Exception as e:
                print(f"Error with {provider}: {e}")
                continue

        # Remove duplicates by URL
        seen_urls = set()
        unique_news = []
        for item in all_news:
            url = item.get('url')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_news.append(item)

        return unique_news[:limit]


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  📰 FREE NEWS API TEST")
    print("="*70)

    api = FreeNewsAPI()

    # Test Alpaca (you already have this!)
    print("\n1. Testing Alpaca News API (should work with your existing keys)...")
    news = api.get_news_alpaca('AAPL', limit=5)
    if news:
        print(f"   ✅ Retrieved {len(news)} articles from Alpaca")
        print(f"   Sample: {news[0]['title']}")
    else:
        print("   ⚠️  No Alpaca news (check API keys)")

    # Test others (need API keys)
    print("\n2. Testing other providers (need API keys)...")
    if api.finnhub_key:
        print("   Finnhub: ✅ Key found")
    else:
        print("   Finnhub: ⚠️  No key (get free key at https://finnhub.io/)")

    if api.alphavantage_key:
        print("   Alpha Vantage: ✅ Key found")
    else:
        print("   Alpha Vantage: ⚠️  No key (get free key at https://www.alphavantage.co/)")

    if api.marketaux_key:
        print("   Marketaux: ✅ Key found")
    else:
        print("   Marketaux: ⚠️  No key (get free key at https://www.marketaux.com/)")

    print("\n" + "="*70)
    print("Next steps:")
    print("1. Alpaca already works (using your existing keys)")
    print("2. Sign up for Finnhub (60 calls/min FREE): https://finnhub.io/")
    print("3. Add FINNHUB_API_KEY to .env file")
    print("="*70 + "\n")
