"""
Logging utility for AI Trading Bot
Provides colored console output and file logging
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

class TradingLogger:
    """Custom logger for trading bot"""
    
    def __init__(self, name='TradingBot', log_file='logs/trading_bot.log', level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
            
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(levelname)-8s | %(message)s'
        )
        
        # File handler
        log_path = Path(log_file)
        log_path.parent.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self):
        return self.logger
    
    def log_trade(self, action, symbol, quantity, price, reasoning):
        """Log a trade with structured format"""
        trade_log = (
            f"\n{'='*80}\n"
            f"TRADE EXECUTED\n"
            f"{'='*80}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Action: {action}\n"
            f"Symbol: {symbol}\n"
            f"Quantity: {quantity}\n"
            f"Price: ${price:.2f}\n"
            f"AI Reasoning:\n{reasoning}\n"
            f"{'='*80}\n"
        )
        self.logger.info(trade_log)
    
    def log_decision(self, decision_type, data):
        """Log AI decision with context"""
        decision_log = (
            f"\n{'-'*80}\n"
            f"AI DECISION: {decision_type}\n"
            f"{'-'*80}\n"
            f"{data}\n"
            f"{'-'*80}\n"
        )
        self.logger.info(decision_log)
    
    def log_performance(self, metrics):
        """Log performance metrics"""
        perf_log = (
            f"\n{'*'*80}\n"
            f"PERFORMANCE UPDATE\n"
            f"{'*'*80}\n"
        )
        for key, value in metrics.items():
            perf_log += f"{key}: {value}\n"
        perf_log += f"{'*'*80}\n"
        self.logger.info(perf_log)

# Create default logger instance
logger = TradingLogger().get_logger()
