# MarketMind AI

An automated trading system that uses AI (DeepSeek/GPT/Claude) to make trading decisions based on market data, technical indicators, and news sentiment.

**Supports:** 📈 **Stocks** (Alpaca) | ₿ **Crypto** (Binance) | 📊 **Backtesting** (10+ years)

## DISCLAIMER

**This is for EDUCATIONAL purposes only. Trading involves substantial risk of loss.**
- Start with PAPER TRADING only
- Never risk money you can't afford to lose
- Past performance doesn't guarantee future results
- The creator assumes NO liability for any losses

---

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Broker Setup](#broker-setup)
  - [Binance (Crypto)](#binance-crypto-trading)
  - [Alpaca (Stocks)](#alpaca-stock-trading)
- [News APIs](#news-apis)
- [Backtesting](#backtesting)
- [Testing](#testing)
- [Configuration](#configuration)
- [Running the Bot](#running-the-bot)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Trading
- ✅ AI-powered decisions (DeepSeek/GPT/Claude)
- ✅ **Multi-broker**: Alpaca (stocks) + Binance (crypto)
- ✅ Real-time market data
- ✅ Technical indicators (RSI, MACD, Bollinger Bands, MA)
- ✅ News sentiment analysis
- ✅ Automated trade execution

### Risk Management
- ✅ Position sizing based on risk
- ✅ Automatic stop losses & take profits
- ✅ Daily loss limits
- ✅ Maximum drawdown circuit breakers
- ✅ Portfolio concentration limits

### Backtesting
- ✅ **10+ years** of historical price data
- ✅ **15.7M+ historical news** articles (1999-2023)
- ✅ Multiple strategies (buy-and-hold, momentum, custom)
- ✅ Performance metrics (Sharpe ratio, max drawdown, win rate)

### Testing
- ✅ **Automated test suite** (21 tests, 90% pass rate)
- ✅ Mock trading (no API calls needed)
- ✅ Integration tests for all brokers

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Choose Your Broker

**For Crypto (Binance):**
```bash
# .env
BROKER=binance
BINANCE_API_KEY=your_testnet_key
BINANCE_SECRET_KEY=your_testnet_secret
```

**For Stocks (Alpaca):**
```bash
# .env
BROKER=alpaca
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
```

### 4. Test It

```bash
# Run automated tests
python tests/test_automated.py

# Run backtests
python tests/test_backtesting.py
```

---

## 🏦 Broker Setup

### Binance (Crypto Trading)

**Best for:** Bitcoin, Ethereum, altcoins, 24/7 trading

#### Get Testnet Keys (FREE, no real money)
1. Go to: https://testnet.binance.vision/
2. Click "Generate HMAC_SHA256 Key"
3. Save your API Key and Secret Key
4. Add to `.env`:
```bash
BROKER=binance
BINANCE_API_KEY=your_testnet_key
BINANCE_SECRET_KEY=your_testnet_secret
TRADING_MODE=paper
```

#### Update Watchlist
```python
# config/config.py
WATCHLIST = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']
```

**Note:** Use `SYMBOL+USDT` format (e.g., `BTCUSDT` not `BTC`)

#### Test Connection
```bash
python -c "
from config.config import Config
from src.brokers import BrokerFactory

broker = BrokerFactory.create('binance', Config.BINANCE_API_KEY, Config.BINANCE_SECRET_KEY, paper=True)
if broker:
    account = broker.get_account_info()
    print(f'Balance: \${account[\"portfolio_value\"]:.2f} USDT')
"
```

### Alpaca (Stock Trading)

**Best for:** US stocks, ETFs, traditional markets

#### Get API Keys (FREE paper trading)
1. Go to: https://alpaca.markets
2. Sign up and create paper trading account
3. Go to "Your API Keys" and generate
4. Add to `.env`:
```bash
BROKER=alpaca
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
TRADING_MODE=paper
```

#### Watchlist
```python
# config/config.py
WATCHLIST = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA']
```

---

## 📰 News APIs

Add real-time news for better AI decisions.

### Recommended: Finnhub (60 calls/min FREE)

#### Setup (2 minutes)
1. Sign up: https://finnhub.io/register
2. Copy your API key
3. Add to `.env`:
```bash
FINNHUB_API_KEY=your_key
```

#### Test
```bash
python src/collectors/news_api_free.py
```

### Other Free Options

| Provider | Free Limit | Best For | Sign Up |
|----------|-----------|----------|---------|
| **Finnhub** | 60/min | Best overall | https://finnhub.io |
| Alpha Vantage | 25/day | Sentiment analysis | https://www.alphavantage.co |
| Marketaux | 100/day | Global coverage | https://www.marketaux.com |

All are **free**, **no credit card**, **instant access**.

---

## 📊 Backtesting

Test strategies on 10+ years of historical data before risking real money.

### Quick Backtest

```bash
# Test on AAPL (10 years)
python tests/test_backtesting.py

# Custom backtest
python examples/simple_backtest.py
```

### Example Results (AAPL 2015-2025)

```
Buy & Hold:    945.50% return, 0.89 Sharpe ratio
Momentum:      382.76% return, 0.84 Sharpe ratio
Random:         73.37% return, 0.42 Sharpe ratio
```

### Custom Backtesting

```python
from src.backtesting import BacktestEngine

engine = BacktestEngine(initial_capital=10000)
result = engine.run_simple_strategy(
    symbol='AAPL',
    start_date='2015-01-01',
    strategy='buy_and_hold'  # or 'momentum' or 'random_trading'
)

print(f"Return: {result['total_return_pct']:.2f}%")
print(f"Sharpe: {result['metrics']['sharpe_ratio']:.2f}")
```

### Available Strategies

1. **Buy and Hold** - Baseline comparison
2. **Momentum** - 50-day MA crossover
3. **Random** - Shows importance of strategy
4. **Custom** - Add your own!

---

## 🧪 Testing

### Automated Test Suite

```bash
# Run all tests (21 tests)
python tests/test_automated.py
```

**Tests:**
- ✅ Broker connection
- ✅ Market data access
- ✅ Trade execution
- ✅ Risk management
- ✅ Portfolio tracking
- ✅ AI decision simulation
- ✅ Trading cycles
- ✅ Stress testing

**Pass rate:** 90.5% (19/21 tests)

### Manual Testing

```bash
# Test specific broker
python -c "from src.brokers import BrokerFactory; ..."

# Test backtesting
python tests/test_backtesting.py

# Test news APIs
python src/collectors/news_api_free.py
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# === BROKER ===
BROKER=binance                      # alpaca or binance

# === BINANCE ===
BINANCE_API_KEY=your_key
BINANCE_SECRET_KEY=your_secret

# === ALPACA ===
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret

# === AI ===
DEEPSEEK_API_KEY=your_key          # Or use OPENAI_API_KEY
AI_MODEL=deepseek-chat
AI_TEMPERATURE=0.7

# === NEWS ===
FINNHUB_API_KEY=your_key           # 60 calls/min free
ALPHAVANTAGE_API_KEY=your_key      # 25 calls/day free
MARKETAUX_API_KEY=your_key         # 100 calls/day free

# === TRADING ===
TRADING_MODE=paper                 # paper or live
INITIAL_CAPITAL=10000
TRADING_INTERVAL_MINUTES=60

# === RISK ===
MAX_POSITION_SIZE_PCT=20
PER_TRADE_RISK_PCT=2
DAILY_LOSS_LIMIT_PCT=3
MAX_DRAWDOWN_PCT=15
```

### Watchlist

```python
# config/config.py

# For Binance (crypto)
WATCHLIST = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']

# For Alpaca (stocks)
WATCHLIST = ['SPY', 'QQQ', 'AAPL', 'MSFT']
```

---

## 🏃 Running the Bot

### Start Trading

```bash
python main.py
```

### What It Does

1. Connects to broker (Binance/Alpaca)
2. Fetches market data for watchlist
3. Calculates technical indicators
4. Gets latest news
5. Asks AI for trading decision
6. Executes trades (if AI suggests)
7. Manages risk (stop loss, take profit)
8. Repeats every hour (configurable)

### Monitoring

```bash
# Watch logs live
tail -f logs/trading_bot.log

# Check portfolio
cat data/portfolio_state.json | python -m json.tool
```

### Stop the Bot

Press `Ctrl+C` - it will:
1. Finish current cycle
2. Save portfolio state
3. Display summary
4. Keep positions open (close manually in broker)

---

## 🔧 Troubleshooting

### "Configuration errors"
- Check `.env` file exists
- Verify all required API keys are filled
- No extra spaces in keys

### "Failed to connect to broker"
**Binance:**
- Using testnet keys? (not live keys)
- Keys have trading permissions?
- Check: https://testnet.binance.vision/

**Alpaca:**
- Paper trading keys? (not live)
- Account is active?
- Check: https://alpaca.markets/

### "Error getting AI decision"
- DeepSeek API key valid?
- Have API credits?
- Check internet connection

### Bot keeps saying HOLD
- Normal! AI is conservative
- Needs >70% confidence to trade
- Try AI_TEMPERATURE=0.8
- Market conditions might not be favorable

### Backtesting Issues
**No historical news:**
- Request access: https://huggingface.co/datasets/Brianferrell787/financial-news-multisource
- Use simulated sentiment (works now):
  ```bash
  python tests/test_backtesting.py  # Uses price-derived sentiment
  ```

**Dataset loading fails:**
- Try simulated sentiment fallback
- Check HuggingFace authentication: `huggingface-cli login`

---

## 📁 Project Structure

```
MarketMind-AI/
├── config/
│   └── config.py              # Configuration
├── src/
│   ├── brokers/               # Multi-broker support
│   │   ├── base_broker.py     # Abstract interface
│   │   ├── alpaca_broker.py   # Stocks
│   │   ├── binance_broker.py  # Crypto
│   │   ├── mock_broker.py     # Testing
│   │   └── broker_factory.py  # Dynamic creation
│   ├── collectors/
│   │   ├── data_collector.py  # Market data
│   │   └── news_api_free.py   # News APIs
│   ├── agents/
│   │   └── ai_agent.py        # AI decisions
│   ├── risk/
│   │   └── risk_manager.py    # Risk management
│   ├── portfolio/
│   │   └── portfolio_manager.py  # Position tracking
│   ├── backtesting/
│   │   ├── backtest_engine.py    # Strategy testing
│   │   ├── historical_data.py    # Price data
│   │   └── historical_news.py    # News data
│   └── utils/
│       └── logger.py          # Logging
├── tests/
│   ├── test_automated.py      # Automated tests
│   └── test_backtesting.py    # Backtest tests
├── examples/
│   └── simple_backtest.py     # Example usage
├── data/
│   ├── historical/            # Cached price data
│   └── portfolio_state.json   # Current state
├── logs/
│   └── trading_bot.log        # Trade logs
├── main.py                    # Main entry point
├── requirements.txt           # Dependencies
└── .env                       # Your API keys
```

---

## 📚 Additional Resources

- **Archived Docs**: `docs/archive/` - Detailed guides
- **Alpaca Docs**: https://alpaca.markets/docs
- **Binance Testnet**: https://testnet.binance.vision/
- **Finnhub API**: https://finnhub.io/docs/api
- **yfinance**: https://pypi.org/project/yfinance/

---

## 🎯 Next Steps

1. ✅ **Setup broker** (Binance or Alpaca)
2. ✅ **Add news API** (Finnhub recommended)
3. ✅ **Run tests** (`python tests/test_automated.py`)
4. ✅ **Run backtests** (`python tests/test_backtesting.py`)
5. → **Paper trade** (real markets, fake money)
6. → **Optimize** (based on results)
7. → **Live trade** (small capital, monitor closely)

---

**Built with:** Python, AI (DeepSeek/GPT/Claude), yfinance, Alpaca, Binance, HuggingFace

**License:** Educational use only

**⭐ Star this repo if it helped you!**
