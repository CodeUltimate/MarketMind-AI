# 📖 Quick Reference Guide

## Essential Commands

### Starting the Bot
```bash
# Start with default settings (from .env)
python3 main.py

# Run in background (Linux/Mac)
nohup python3 main.py > bot_output.log 2>&1 &

# Run in background (with screen)
screen -S trading-bot
python3 main.py
# Press Ctrl+A, then D to detach
# Reconnect with: screen -r trading-bot
```

### Stopping the Bot
```bash
# If running in foreground
Ctrl+C

# If running in background
ps aux | grep main.py
kill <process_id>

# Or use screen
screen -r trading-bot
Ctrl+C
```

### Monitoring

#### Watch Live Logs
```bash
# Follow logs in real-time
tail -f logs/trading_bot.log

# Last 100 lines
tail -n 100 logs/trading_bot.log

# Search for trades
grep "TRADE EXECUTED" logs/trading_bot.log

# Search for AI decisions
grep "AI DECISION" logs/trading_bot.log

# Search for errors
grep "ERROR" logs/trading_bot.log
```

#### Check Portfolio State
```bash
# View portfolio (formatted)
cat data/portfolio_state.json | python3 -m json.tool

# Quick stats
python3 -c "import json; data=json.load(open('data/portfolio_state.json')); print(f'Cash: \${data[\"cash\"]:.2f}'); print(f'Positions: {len(data[\"positions\"])}')"

# Trade count
python3 -c "import json; data=json.load(open('data/portfolio_state.json')); print(f'Total trades: {len(data[\"trade_history\"])}')"
```

#### Check Account on Alpaca
```bash
# Log into: https://app.alpaca.markets/paper/dashboard/overview
# Or use CLI:
python3 -c "from src.executors.trade_executor import TradeExecutor; te = TradeExecutor(); print(te.get_account_info())"
```

## Configuration

### Update API Keys
```bash
nano .env
# Update the keys, save with Ctrl+X, Y, Enter
```

### Change Trading Interval
```bash
# Edit .env
TRADING_INTERVAL_MINUTES=30  # Check every 30 minutes
```

### Adjust Risk Settings
```bash
# Edit .env
MAX_POSITION_SIZE_PCT=15     # Lower position sizes
PER_TRADE_RISK_PCT=1         # More conservative risk
DAILY_LOSS_LIMIT_PCT=2       # Tighter loss limit
```

## Troubleshooting

### Test Components Individually

#### Test Configuration
```bash
python3 -c "from config.config import Config; Config.validate(); print('✅ Config OK')"
```

#### Test Alpaca Connection
```bash
python3 -c "from src.executors.trade_executor import TradeExecutor; te = TradeExecutor(); acc = te.get_account_info(); print(f'✅ Connected. Balance: \${acc[\"portfolio_value\"]:.2f}')"
```

#### Test AI Agent
```bash
python3 -c "from src.agents.ai_agent import AITradingAgent; agent = AITradingAgent(); print('✅ AI Agent initialized')"
```

#### Test Data Collection
```bash
python3 -c "from src.collectors.data_collector import MarketDataCollector; mdc = MarketDataCollector(['AAPL']); prices = mdc.get_current_prices(); print(f'✅ AAPL: \${prices.get(\"AAPL\", 0):.2f}')"
```

### Reset Portfolio
```bash
# Backup first!
cp data/portfolio_state.json data/portfolio_state.backup.json

# Delete to reset
rm data/portfolio_state.json

# Bot will create new one on next run with INITIAL_CAPITAL
```

### Clear Logs
```bash
# Backup logs
cp logs/trading_bot.log logs/trading_bot.backup.log

# Clear current logs
> logs/trading_bot.log

# Or delete
rm logs/trading_bot.log
```

### Check for Errors
```bash
# Find all errors
grep -i "error" logs/trading_bot.log

# Count errors
grep -i "error" logs/trading_bot.log | wc -l

# Last 10 errors
grep -i "error" logs/trading_bot.log | tail -n 10
```

## Performance Analysis

### Win Rate
```bash
python3 << EOF
import json
data = json.load(open('data/portfolio_state.json'))
trades = [t for t in data['trade_history'] if t['action'] == 'SELL']
if trades:
    wins = sum(1 for t in trades if t['pnl'] > 0)
    print(f"Win Rate: {wins/len(trades)*100:.1f}% ({wins}/{len(trades)})")
else:
    print("No closed trades yet")
EOF
```

### Total P&L
```bash
python3 << EOF
import json
data = json.load(open('data/portfolio_state.json'))
trades = [t for t in data['trade_history'] if t['action'] == 'SELL']
total_pnl = sum(t['pnl'] for t in trades)
print(f"Total P&L: \${total_pnl:.2f}")
EOF
```

### Best and Worst Trades
```bash
python3 << EOF
import json
data = json.load(open('data/portfolio_state.json'))
trades = [t for t in data['trade_history'] if t['action'] == 'SELL']
if trades:
    best = max(trades, key=lambda x: x['pnl'])
    worst = min(trades, key=lambda x: x['pnl'])
    print(f"Best: {best['symbol']} \${best['pnl']:.2f} ({best['pnl_pct']:.1f}%)")
    print(f"Worst: {worst['symbol']} \${worst['pnl']:.2f} ({worst['pnl_pct']:.1f}%)")
EOF
```

### Performance Timeline
```bash
python3 << EOF
import json
data = json.load(open('data/portfolio_state.json'))
for day in data['daily_values'][-7:]:  # Last 7 days
    print(f"{day['date']}: \${day['value']:.2f} ({day['return_pct']:+.2f}%)")
EOF
```

## Maintenance

### Update Dependencies
```bash
pip3 install --upgrade -r requirements.txt
```

### Backup Everything
```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Copy important files
cp data/portfolio_state.json backups/$(date +%Y%m%d)/
cp logs/trading_bot.log backups/$(date +%Y%m%d)/
cp .env backups/$(date +%Y%m%d)/
```

### Schedule Regular Runs (Cron)
```bash
# Edit crontab
crontab -e

# Add line to run every hour at minute 0
# Example: 0 * * * * cd /path/to/ai-trading-bot && python3 main.py >> logs/cron.log 2>&1

# Or use screen/tmux for persistent session
```

## Emergency Procedures

### Close All Positions Immediately
```bash
python3 << EOF
from src.executors.trade_executor import TradeExecutor
te = TradeExecutor()
te.close_all_positions()
print("✅ All positions closed")
EOF
```

### Pause Trading (Circuit Breaker)
```bash
# Edit .env
DAILY_LOSS_LIMIT_PCT=0  # Will trigger immediately
# Or just stop the bot with Ctrl+C
```

### Export Trade History
```bash
python3 << EOF
import json
import csv
data = json.load(open('data/portfolio_state.json'))
with open('trade_history.csv', 'w', newline='') as f:
    if data['trade_history']:
        writer = csv.DictWriter(f, fieldnames=data['trade_history'][0].keys())
        writer.writeheader()
        writer.writerows(data['trade_history'])
print("✅ Exported to trade_history.csv")
EOF
```

## Useful Python Snippets

### Run Single Trading Cycle (No Loop)
```python
from main import AITradingBot
bot = AITradingBot()
bot.run_trading_cycle()  # Run once and exit
```

### Check What AI Would Decide
```python
from main import AITradingBot
bot = AITradingBot()
market_data = bot.collect_market_data()
portfolio_state = bot.get_portfolio_state()
decision = bot.ai_agent.get_trading_decision(market_data, portfolio_state)
print(decision)
```

### Manually Execute Trade
```python
from src.executors.trade_executor import TradeExecutor
te = TradeExecutor()

# Buy
order = te.execute_buy(symbol='AAPL', quantity=1)
print(order)

# Sell
order = te.execute_sell(symbol='AAPL', quantity=1)
print(order)
```

## Environment Variables Reference

```bash
# Required
DEEPSEEK_API_KEY=your_key
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_key

# Optional
NEWS_API_KEY=your_key

# Trading
INITIAL_CAPITAL=1000
TRADING_MODE=paper  # or live
TRADING_INTERVAL_MINUTES=60

# Risk
MAX_POSITION_SIZE_PCT=20
MAX_PORTFOLIO_RISK_PCT=10
PER_TRADE_RISK_PCT=2
DAILY_LOSS_LIMIT_PCT=3
MAX_DRAWDOWN_PCT=15

# AI
AI_MODEL=deepseek-chat
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=1000

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## Watchlist Management

### Change Symbols
Edit `main.py`, line ~30:
```python
self.watchlist = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA']
```

### Add More Symbols
```python
self.watchlist = [
    # ETFs
    'SPY', 'QQQ', 'IWM',
    # Tech
    'AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD',
    # Growth
    'TSLA', 'AMZN', 'NFLX'
]
```

---

## Help Commands

### Get Python Path
```bash
which python3
```

### Check Python Version
```bash
python3 --version
```

### List Installed Packages
```bash
pip3 list | grep alpaca
pip3 list | grep openai
```

### Check Disk Space
```bash
du -sh logs/
du -sh data/
```

### Find Process
```bash
ps aux | grep python3
ps aux | grep main.py
```

---

**Remember:** Always test on paper trading first! 📝
