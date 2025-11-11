"""
Historical News Provider - OPTIMIZED FOR HIGH RAM
Uses aggressive caching and memory loading for 128GB+ RAM systems
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import json


class HistoricalNewsProviderOptimized:
    """
    Optimized for systems with 128GB+ RAM
    Loads entire dataset into memory for maximum speed
    """

    def __init__(self, cache_dir: str = "data/historical_news"):
        """Initialize news provider with aggressive caching"""
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.dataset = None
        self.df = None  # Load entire dataset into pandas DataFrame
        self._initialized = False

    def _initialize_dataset(self):
        """
        Load dataset with AGGRESSIVE settings for high RAM systems
        """
        if self._initialized:
            return True

        try:
            from datasets import load_dataset

            print("\n📰 Initializing historical news dataset (OPTIMIZED MODE)...")
            print("   🚀 Using aggressive RAM loading for 128GB+ systems...")

            # Check if we have a local cache
            cache_file = f"{self.cache_dir}/fnspid_full_dataset.parquet"

            if os.path.exists(cache_file):
                print(f"   📁 Loading from local cache: {cache_file}")
                self.df = pd.read_parquet(cache_file)
                print(f"   ✅ Loaded {len(self.df):,} articles from cache!")
                self._initialized = True
                return True

            print("   📥 Downloading full dataset (this will be cached)...")
            print("   ⚠️  First run: May download 20-30GB of data")
            print("   💾 With 128GB RAM, we'll load it ALL into memory!")

            # Try FNSPID dataset first (ungated, 15.7M articles, 1999-2023)
            try:
                print("   Trying FNSPID dataset (ungated)...")

                # Load WITHOUT streaming for high-RAM systems
                # This downloads everything at once
                self.dataset = load_dataset(
                    "Zihan1004/FNSPID",
                    split="train",
                    streaming=False,  # ← Changed from True! Load all into RAM
                    cache_dir=self.cache_dir
                )

                print("   🔄 Converting to pandas DataFrame...")
                self.df = self.dataset.to_pandas()

                # Cache it locally as parquet for instant future loads
                print(f"   💾 Caching to {cache_file}...")
                self.df.to_parquet(cache_file, compression='snappy')

                print(f"   ✅ Loaded {len(self.df):,} articles into RAM!")

            except Exception as e:
                print(f"   ⚠️  FNSPID failed: {e}")
                print("   Trying financial-news-multisource (requires access)...")

                self.dataset = load_dataset(
                    "Brianferrell787/financial-news-multisource",
                    split="train",
                    streaming=False,  # Load all into RAM
                    cache_dir=self.cache_dir
                )

                self.df = self.dataset.to_pandas()
                self.df.to_parquet(cache_file, compression='snappy')

            self._initialized = True
            print("   ✅ Historical news dataset ready in RAM!")
            return True

        except Exception as e:
            print(f"   ❌ Could not load historical news: {e}")
            return False

    def get_news_for_date_range(self,
                                 start_date: str,
                                 end_date: str,
                                 symbol: Optional[str] = None,
                                 limit: int = 10000) -> List[Dict]:  # Higher limit!
        """
        Get historical news - FAST with in-memory DataFrame
        """
        if not self._initialize_dataset():
            return []

        print(f"\n📥 Fetching historical news: {start_date} to {end_date}")
        if symbol:
            print(f"   Symbol: {symbol}")

        # Convert dates
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)

        # Filter DataFrame (FAST with pandas)
        df = self.df.copy()

        # Parse dates if needed
        if 'date' in df.columns:
            df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')

            # Filter by date range
            mask = (df['date_parsed'] >= start_dt) & (df['date_parsed'] <= end_dt)
            df = df[mask]

            # Filter by symbol if provided
            if symbol:
                # This is fast with pandas
                symbol_mask = df['text'].str.contains(symbol, case=False, na=False)
                df = df[symbol_mask]

            # Limit results
            df = df.head(limit)

            # Convert to list of dicts
            articles = df.to_dict('records')

            print(f"   ✅ Retrieved {len(articles):,} articles")
            return articles

        return []

    def simulate_sentiment_from_price(self, price_change_pct: float) -> Dict:
        """
        Fallback: Simulate news sentiment based on price movements
        """
        if price_change_pct > 5:
            sentiment = "very_positive"
            score = 0.8
        elif price_change_pct > 2:
            sentiment = "positive"
            score = 0.6
        elif price_change_pct > -2:
            sentiment = "neutral"
            score = 0.5
        elif price_change_pct > -5:
            sentiment = "negative"
            score = 0.3
        else:
            sentiment = "very_negative"
            score = 0.2

        return {
            'sentiment': sentiment,
            'score': score,
            'source': 'price_derived',
            'articles_count': 0
        }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  📰 OPTIMIZED HISTORICAL NEWS PROVIDER TEST")
    print("  🚀 Designed for 128GB+ RAM systems")
    print("="*70)

    provider = HistoricalNewsProviderOptimized()

    # This will download and cache the full dataset
    # First run: ~20-30GB download
    # Future runs: Instant from cache

    print("\n⚠️  WARNING: First run will download 20-30GB of data")
    print("   With your 128GB RAM, this is fine!")
    print("   Future runs will be INSTANT from cache\n")

    articles = provider.get_news_for_date_range(
        start_date='2020-01-01',
        end_date='2020-01-07',
        limit=100
    )

    if articles:
        print(f"\n✅ SUCCESS! Retrieved {len(articles)} articles")
        print(f"\nSample article:")
        print(f"Date: {articles[0].get('date', 'N/A')}")
        print(f"Text: {str(articles[0].get('text', 'N/A'))[:200]}...")
    else:
        print("\n⚠️  Using simulated sentiment fallback")

    print("\n" + "="*70)
