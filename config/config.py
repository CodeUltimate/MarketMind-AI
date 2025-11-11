"""
Configuration module for AI Trading Bot
Loads environment variables and provides validated config
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for trading bot"""
    
    # API Keys
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

    # Alpaca Keys
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

    # Binance Keys
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    
    # Broker Configuration
    BROKER = os.getenv('BROKER', 'alpaca').lower()  # Broker to use (alpaca, interactive_brokers, etc.)

    # Alpaca Configuration
    ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')

    # Trading Configuration
    INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', 1000))
    TRADING_MODE = os.getenv('TRADING_MODE', 'paper')
    TRADING_INTERVAL_MINUTES = int(os.getenv('TRADING_INTERVAL_MINUTES', 60))
    
    # Risk Management
    MAX_POSITION_SIZE_PCT = float(os.getenv('MAX_POSITION_SIZE_PCT', 20))
    MAX_PORTFOLIO_RISK_PCT = float(os.getenv('MAX_PORTFOLIO_RISK_PCT', 10))
    PER_TRADE_RISK_PCT = float(os.getenv('PER_TRADE_RISK_PCT', 2))
    DAILY_LOSS_LIMIT_PCT = float(os.getenv('DAILY_LOSS_LIMIT_PCT', 3))
    MAX_DRAWDOWN_PCT = float(os.getenv('MAX_DRAWDOWN_PCT', 15))
    
    # AI Configuration
    AI_MODEL = os.getenv('AI_MODEL', 'deepseek-chat')
    AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', 0.7))
    AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', 1000))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/trading_bot.log')
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    LOGS_DIR = BASE_DIR / 'logs'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []

        # AI API key is always required
        if not cls.DEEPSEEK_API_KEY:
            errors.append("DEEPSEEK_API_KEY is required")

        # Validate broker-specific keys
        if cls.BROKER == 'alpaca':
            if not cls.ALPACA_API_KEY:
                errors.append("ALPACA_API_KEY is required for Alpaca broker")
            if not cls.ALPACA_SECRET_KEY:
                errors.append("ALPACA_SECRET_KEY is required for Alpaca broker")
        elif cls.BROKER == 'binance':
            if not cls.BINANCE_API_KEY:
                errors.append("BINANCE_API_KEY is required for Binance broker")
            if not cls.BINANCE_SECRET_KEY:
                errors.append("BINANCE_SECRET_KEY is required for Binance broker")

        if cls.TRADING_MODE not in ['paper', 'live']:
            errors.append("TRADING_MODE must be 'paper' or 'live'")

        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))

        # Create directories
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)

        return True

# Validate on import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️  Configuration Error: {e}")
    print("Please copy .env.example to .env and fill in your API keys")
