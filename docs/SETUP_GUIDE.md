# 🔧 Detailed Setup Guide

This guide will walk you through setting up the AI Trading Bot step-by-step.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Getting API Keys](#getting-api-keys)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Running the Bot](#running-the-bot)

## System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: Version 3.9 or higher
- **Internet Connection**: Required for API calls
- **Time**: ~30 minutes for full setup

## Getting API Keys

### 1. Alpaca Trading API (Required)

Alpaca provides free paper trading accounts.

**Steps:**
1. Go to https://alpaca.markets
2. Click "Sign Up" (top right)
3. Choose "Individual" account type
4. Fill in your information
5. Verify your email
6. Once logged in, click "Go to Paper Account" (important!)
7. Navigate to "Your API Keys" in the left sidebar
8. Click "Generate New Key"
9. **IMPORTANT**: Copy both:
   - API Key ID (starts with PK...)
   - Secret Key (starts with ...)
10. Store them safely - you'll need them in a moment

**Notes:**
- Paper trading is 100% free
- You get $100,000 in paper money to test
- No real money is involved
- Resets if you run out

### 2. DeepSeek AI API (Required)

DeepSeek provides AI models for trading decisions.

**Steps:**
1. Go to https://platform.deepseek.com
2. Click "Sign Up"
3. Verify your email
4. Log in and go to "API Keys"
5. Click "Create API Key"
6. Copy the key (starts with sk-...)
7. Store it safely

**Pricing:**
- Pay-as-you-go pricing
- ~$0.01-0.10 per decision
- Recommend starting with $5 credit
- Should last weeks/months

### 3. News API (Optional but Recommended)

News API provides market news for better decisions.

**Steps:**
1. Go to https://newsapi.org
2. Click "Get API Key"
3. Sign up (free plan)
4. Copy your API key
5. Free plan: 100 requests/day (enough for testing)

## Installation

### Step 1: Install Python

**Check if you have Python:**
```bash
python3 --version
```

If you see "Python 3.9" or higher, you're good!

**If not, install Python:**

**macOS:**
```bash
brew install python3
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**Windows:**
Download from https://www.python.org/downloads/

### Step 2: Set Up Project

```bash
# Navigate to where you want the project
cd ~

# The files are already in /home/claude/ai-trading-bot
# If you need to copy them somewhere:
# cp -r /home/claude/ai-trading-bot ~/my-trading-bot
cd /home/claude/ai-trading-bot
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip3 install -r requirements.txt
```

This will install:
- alpaca-py (trading API)
- openai (for DeepSeek API)
- yfinance (market data)
- pandas, numpy (data analysis)
- ta (technical indicators)
- and more...

**Troubleshooting:**
- If you get permission errors, try: `pip3 install --user -r requirements.txt`
- On Windows, use `pip` instead of `pip3`

## Configuration

### Step 1: Create Environment File

```bash
# Copy the example file
cp .env.example .env
```

### Step 2: Edit Configuration

```bash
# Open in your favorite editor
nano .env
# or
vim .env
# or
code .env  # if you have VS Code
```

### Step 3: Add Your API Keys

Update these lines with your actual keys:

```bash
# Replace 'your_deepseek_api_key_here' with your actual key
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Replace with your Alpaca keys
ALPACA_API_KEY=PKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Add News API key
NEWS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**CRITICAL: Keep paper trading enabled!**
```bash
ALPACA_BASE_URL=https://paper-api.alpaca.markets
TRADING_MODE=paper
```

### Step 4: Customize Settings (Optional)

You can adjust these in .env:

```bash
# Starting capital (paper money)
INITIAL_CAPITAL=1000

# How often to check markets (in minutes)
# 60 = every hour, 15 = every 15 minutes
TRADING_INTERVAL_MINUTES=60

# Risk settings (recommended to leave as-is initially)
MAX_POSITION_SIZE_PCT=20
PER_TRADE_RISK_PCT=2
DAILY_LOSS_LIMIT_PCT=3
MAX_DRAWDOWN_PCT=15
```

### Step 5: Save and Exit

- In nano: `Ctrl+X`, then `Y`, then `Enter`
- In vim: `:wq`

## Testing

### Test 1: Check Configuration

```bash
python3 -c "from config.config import Config; print('✅ Configuration loaded successfully')"
```

If you see the success message, great! If not:
- Check that .env file exists
- Verify API keys have no extra spaces
- Make sure .env is in the same directory as main.py

### Test 2: Test Alpaca Connection

```bash
python3 -c "from src.executors.trade_executor import TradeExecutor; te = TradeExecutor(); print('✅ Alpaca connected')"
```

You should see:
```
✅ Connected to Alpaca (Paper Trading)
Account Value: $100000.00
Buying Power: $100000.00
✅ Alpaca connected
```

### Test 3: Test AI Connection

```bash
python3 -c "from src.agents.ai_agent import AITradingAgent; agent = AITradingAgent(); print('✅ AI agent initialized')"
```

If this works without errors, you're ready!

### Test 4: Test Data Collection

```bash
python3 -c "from src.collectors.data_collector import MarketDataCollector; mdc = MarketDataCollector(); prices = mdc.get_current_prices(); print(f'✅ Got prices for {len(prices)} symbols')"
```

## Running the Bot

### First Run

```bash
python3 main.py
```

You should see:
```
================================================================================
🤖 AI TRADING BOT STARTING UP
================================================================================
Initializing components...
✅ All components initialized successfully
Trading Mode: PAPER
Initial Capital: $1000.00
Trading Interval: 60 minutes
```

The bot will:
1. Start collecting market data
2. Get AI trading decision
3. Log everything it does
4. Wait 60 minutes
5. Repeat

### Watch It Work

Open a second terminal and watch the logs:
```bash
tail -f logs/trading_bot.log
```

### Let It Run

- Let it run for at least a few hours
- Check logs to see AI reasoning
- Watch for any trades it makes
- Monitor your Alpaca paper account

### Stop the Bot

Press `Ctrl+C` in the terminal where bot is running.

## Common Issues

### Issue: "Module not found"
**Solution:** Make sure you're in the right directory and ran `pip3 install -r requirements.txt`

### Issue: "API key invalid"
**Solution:** Double-check your keys in .env - no spaces, no quotes

### Issue: "Connection timeout"
**Solution:** Check internet connection, might be firewall

### Issue: Bot says "HOLD" every time
**Solution:** This is normal! It's being cautious. Market conditions might not be ideal for trading.

### Issue: "Trading paused: Daily loss limit"
**Solution:** This is working correctly! Wait until tomorrow or adjust limits in .env

## Next Steps

1. **Let it run for 24 hours** - See how it behaves
2. **Review the logs** - Understand AI reasoning
3. **Check Alpaca dashboard** - See trades executed
4. **Adjust settings** - Tune based on observations
5. **Run for weeks** - Gather performance data

## Safety Checklist

Before going further, verify:

- [ ] Using paper trading (not live)
- [ ] .env file is secured (don't share it!)
- [ ] Understand risk management settings
- [ ] Read the logs and understand AI decisions
- [ ] Have tested for at least a week
- [ ] Know how to stop the bot (Ctrl+C)

## Getting Help

If you run into issues:

1. Check logs: `cat logs/trading_bot.log`
2. Verify configuration: `cat .env`
3. Test individual components (see Test sections above)
4. Check Alpaca status: https://status.alpaca.markets/
5. Review API documentation

---

**You're now ready to start paper trading! Remember to monitor it closely at first.**
