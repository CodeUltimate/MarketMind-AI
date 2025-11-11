# 🏗️ System Architecture & Design

## Overview

The AI Trading Bot is built with a modular architecture where each component has a single responsibility. This makes it easy to test, debug, and upgrade individual pieces.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER                                     │
│                    (Monitors logs)                               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MAIN TRADING BOT                             │
│                    (main.py orchestrates)                        │
└────┬──────┬──────┬──────┬──────┬──────┬──────────────────────┘
     │      │      │      │      │      │
     ▼      ▼      ▼      ▼      ▼      ▼
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌──────┐
│Data │ │ AI  │ │Risk │ │Port │ │Exec │ │Logger│
│Coll │ │Agent│ │Mgr  │ │folio│ │utor │ │      │
└─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └──────┘
   │       │       │       │       │         │
   ▼       ▼       ▼       ▼       ▼         ▼
┌─────────────────────────────────────────────────┐
│           EXTERNAL SERVICES                     │
│  • Yahoo Finance (market data)                  │
│  • DeepSeek API (AI decisions)                  │
│  • News API (sentiment)                         │
│  • Alpaca API (trade execution)                 │
└─────────────────────────────────────────────────┘
```

## Component Details

### 1. Main Trading Bot (main.py)

**Purpose**: Orchestrates all components and executes trading cycles

**Responsibilities**:
- Initialize all components
- Run trading cycles at defined intervals
- Coordinate data flow between components
- Handle errors and logging
- Provide graceful shutdown

**Key Methods**:
- `collect_market_data()` - Gathers all market information
- `get_portfolio_state()` - Gets current portfolio status
- `check_stop_losses_and_targets()` - Monitors existing positions
- `run_trading_cycle()` - Executes one complete cycle
- `run()` - Main loop that runs continuously

### 2. Data Collector (collectors/data_collector.py)

**Purpose**: Collects market data, indicators, and news

**Components**:

**MarketDataCollector**:
- Gets current prices for watchlist symbols
- Calculates technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Analyzes market sentiment (VIX, SPY trends)
- Classifies market regime (Bull, Bear, Range-Bound, Crisis)

**NewsCollector**:
- Fetches recent market news
- Gets symbol-specific news
- Provides sentiment context to AI

**Data Flow**:
```
Watchlist → Yahoo Finance → Historical Data → Calculate Indicators → Format for AI
                                ↓
                         Market Sentiment
                                ↓
                         News Headlines
```

### 3. AI Agent (agents/ai_agent.py)

**Purpose**: Makes trading decisions using AI models

**Key Features**:
- Sends formatted prompts to DeepSeek API
- Parses AI responses into structured decisions
- Validates AI output format
- Provides default HOLD decision on errors

**Decision Format**:
```json
{
    "action": "BUY" | "SELL" | "HOLD",
    "symbol": "AAPL",
    "confidence": 0.85,
    "reasoning": "Strong uptrend with RSI...",
    "stop_loss_pct": 2.0,
    "take_profit_pct": 6.0,
    "position_size_pct": 15.0
}
```

**Prompt Strategy**:
- System prompt: Defines AI role as expert trader
- User prompt: Provides market data, indicators, news
- Response format: Strictly enforced JSON structure

### 4. Risk Manager (risk/risk_manager.py)

**Purpose**: Manages all risk and protects capital

**Circuit Breakers**:
1. **Daily Loss Limit** (default: -3%)
   - Pauses trading if daily loss exceeds limit
   - Resets at midnight
   
2. **Maximum Drawdown** (default: -15%)
   - Stops all trading if total drawdown exceeds limit
   - Requires manual restart after review

**Position Sizing**:
```
Risk-Based Size = (Portfolio * Risk%) / Stop Loss Distance
Max Size = Portfolio * Max Position%
Confidence Adjusted = Base Size * Confidence
Final Size = MIN(Risk-Based, Max, Confidence-Adjusted)
```

**Trade Validation**:
- Checks if trading is paused
- Validates position size limits
- Prevents over-concentration
- Ensures stop losses are set
- Verifies sufficient cash

### 5. Portfolio Manager (portfolio/portfolio_manager.py)

**Purpose**: Tracks positions, cash, and performance

**State Management**:
```json
{
    "cash": 850.00,
    "positions": {
        "AAPL": {
            "quantity": 5,
            "entry_price": 150.00,
            "current_price": 155.00,
            "stop_loss": 147.00,
            "take_profit": 159.00,
            "unrealized_pnl": 25.00
        }
    },
    "trade_history": [...],
    "daily_values": [...]
}
```

**Persistence**:
- Saves state to `data/portfolio_state.json`
- Loads on startup
- Updates after every trade
- Tracks daily values for performance analysis

**Performance Metrics**:
- Win rate
- Profit factor (Avg Win / Avg Loss)
- Total P&L
- Best/worst trades
- Number of trades

### 6. Trade Executor (executors/trade_executor.py)

**Purpose**: Executes trades through Alpaca broker

**Order Types**:
1. **Market Orders**: Execute immediately at current price
2. **Limit Orders**: Execute only at specified price or better

**Features**:
- Real-time order status tracking
- Position monitoring
- Account info retrieval
- Emergency position closing
- Paper vs Live trading modes

**Safety**:
- All orders default to paper trading
- Requires explicit config change for live
- Validates orders before submission
- Logs all trade attempts

### 7. Logger (utils/logger.py)

**Purpose**: Provides structured logging

**Log Levels**:
- DEBUG: Detailed diagnostic info
- INFO: General operational messages
- WARNING: Potential issues
- ERROR: Serious problems

**Special Logging**:
- Trade logs: Detailed trade execution info
- Decision logs: AI reasoning and decisions
- Performance logs: Metrics summaries

**Outputs**:
- Console: Formatted, colored output
- File: `logs/trading_bot.log` with full detail

## Data Flow - Complete Trading Cycle

```
1. START CYCLE
   │
   ▼
2. CHECK POSITIONS
   - Monitor stop losses
   - Monitor take profits
   │
   ▼
3. GET PORTFOLIO STATE
   - Current cash
   - Position values
   - Daily P&L
   │
   ▼
4. CHECK CIRCUIT BREAKERS
   - Daily loss limit
   - Max drawdown
   │ (If triggered → PAUSE)
   ▼
5. COLLECT MARKET DATA
   - Prices for watchlist
   - Technical indicators
   - Market sentiment
   - News headlines
   │
   ▼
6. AI DECISION
   - Format prompt with data
   - Send to DeepSeek API
   - Parse response
   │
   ▼
7. VALIDATE DECISION
   - Check confidence threshold
   - Validate against risk limits
   - Ensure stop loss set
   │
   ▼
8. CALCULATE POSITION SIZE
   - Risk-based sizing
   - Apply confidence multiplier
   - Respect position limits
   │
   ▼
9. EXECUTE TRADE
   - Submit order to Alpaca
   - Update portfolio state
   - Log trade with reasoning
   │
   ▼
10. RECORD METRICS
    - Save daily value
    - Update performance stats
    - Log risk metrics
    │
    ▼
11. WAIT
    - Sleep for interval
    - Then repeat from Step 1
```

## Error Handling Strategy

### Graceful Degradation
1. **API Failure**: Default to HOLD decision
2. **Data Unavailable**: Skip that symbol
3. **Order Rejection**: Log error, don't retry
4. **Network Issues**: Log and continue next cycle

### Fail-Safe Mechanisms
- All trades require explicit validation
- Circuit breakers auto-pause trading
- Portfolio state persists to disk
- Logs capture all errors with stack traces

## Extension Points

### Adding New AI Models

```python
# In ai_agent.py
class AITradingAgent:
    def __init__(self, model_type='deepseek'):
        if model_type == 'deepseek':
            self.client = OpenAI(base_url="https://api.deepseek.com")
        elif model_type == 'gpt':
            self.client = OpenAI()  # OpenAI default
        elif model_type == 'claude':
            # Add Anthropic client
            pass
```

### Adding New Indicators

```python
# In data_collector.py
def calculate_indicators(self, symbol):
    # Add your indicator
    indicators['Custom_Indicator'] = your_calculation(df)
```

### Adding Alternative Data

```python
# In data_collector.py
class SocialSentimentCollector:
    def get_reddit_sentiment(self, symbol):
        # Scrape Reddit WSB
        pass
    
    def get_twitter_sentiment(self, symbol):
        # Analyze Twitter mentions
        pass
```

### Ensemble AI Voting

```python
# In main.py
def get_ensemble_decision(self, market_data, portfolio_state):
    decisions = [
        self.deepseek_agent.get_decision(market_data, portfolio_state),
        self.gpt_agent.get_decision(market_data, portfolio_state),
        self.claude_agent.get_decision(market_data, portfolio_state)
    ]
    # Vote on action, weight by confidence
    return self._aggregate_decisions(decisions)
```

## Performance Considerations

### API Rate Limits
- DeepSeek: ~100 requests/min
- Alpaca: 200 requests/min
- Yahoo Finance: No strict limit
- News API: 100 requests/day (free tier)

### Latency
- Market data: ~1-2 seconds
- AI decision: ~2-5 seconds
- Order execution: ~0.5-1 seconds
- Total cycle: ~10-15 seconds

### Resource Usage
- Memory: ~100-200 MB
- CPU: <5% (mostly idle)
- Disk: <10 MB (logs + state)
- Network: ~1-5 MB/hour

## Security Considerations

### API Keys
- Stored in .env file (not in code)
- Never committed to version control
- .gitignore includes .env
- Use environment variables in production

### Paper vs Live Trading
- Default to paper trading
- Explicit config change required for live
- Multiple safety checks before execution
- Clear warnings in logs

### Data Privacy
- No personal data stored
- Only trade data and portfolio state
- Logs contain no sensitive info
- API keys never logged

## Testing Strategy

### Unit Tests (Future)
- Test each component in isolation
- Mock external API calls
- Validate risk calculations
- Test decision parsing

### Integration Tests
- Test full cycle with mock data
- Verify order flow
- Check state persistence
- Validate error handling

### Backtesting (Future Enhancement)
- Run on historical data
- Validate strategy performance
- Optimize parameters
- Test different market conditions

---

This architecture is designed to be **modular**, **testable**, **safe**, and **extensible**.
