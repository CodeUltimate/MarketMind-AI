"""
Portfolio Manager Module
Tracks positions, cash, and performance metrics
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from ..utils.logger import logger

class PortfolioManager:
    """Manages portfolio state and performance tracking"""
    
    def __init__(self, initial_capital: float, data_file: str = 'data/portfolio_state.json'):
        self.data_file = Path(data_file)
        self.initial_capital = initial_capital
        
        # Load existing state or initialize
        if self.data_file.exists():
            self.load_state()
        else:
            self.initialize_portfolio()
    
    def initialize_portfolio(self):
        """Initialize new portfolio"""
        self.state = {
            'cash': self.initial_capital,
            'positions': {},
            'trade_history': [],
            'daily_values': [],
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        self.save_state()
        logger.info(f"✅ Initialized portfolio with ${self.initial_capital:.2f}")
    
    def load_state(self):
        """Load portfolio state from file"""
        try:
            with open(self.data_file, 'r') as f:
                self.state = json.load(f)
            logger.info("✅ Loaded existing portfolio state")
        except Exception as e:
            logger.error(f"Error loading portfolio state: {e}")
            self.initialize_portfolio()
    
    def save_state(self):
        """Save portfolio state to file"""
        try:
            self.state['last_updated'] = datetime.now().isoformat()
            self.data_file.parent.mkdir(exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving portfolio state: {e}")
    
    def add_position(self, symbol: str, quantity: int, entry_price: float, 
                     stop_loss: Optional[float] = None, 
                     take_profit: Optional[float] = None,
                     reasoning: str = ""):
        """Add or update a position"""
        self.state['positions'][symbol] = {
            'symbol': symbol,
            'quantity': quantity,
            'entry_price': entry_price,
            'entry_date': datetime.now().isoformat(),
            'current_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'unrealized_pnl': 0,
            'unrealized_pnl_pct': 0,
            'reasoning': reasoning
        }
        
        # Deduct from cash
        cost = quantity * entry_price
        self.state['cash'] -= cost
        
        # Record trade
        self.record_trade('BUY', symbol, quantity, entry_price, reasoning)
        self.save_state()
        
        logger.info(f"✅ Added position: {quantity} shares of {symbol} @ ${entry_price:.2f}")
    
    def close_position(self, symbol: str, exit_price: float, reasoning: str = ""):
        """Close a position"""
        if symbol not in self.state['positions']:
            logger.error(f"Cannot close {symbol}: position not found")
            return
        
        position = self.state['positions'][symbol]
        quantity = position['quantity']
        entry_price = position['entry_price']
        
        # Calculate P&L
        proceeds = quantity * exit_price
        cost = quantity * entry_price
        pnl = proceeds - cost
        pnl_pct = (pnl / cost) * 100
        
        # Add to cash
        self.state['cash'] += proceeds
        
        # Record trade
        self.record_trade('SELL', symbol, quantity, exit_price, reasoning, pnl, pnl_pct)
        
        # Remove position
        del self.state['positions'][symbol]
        self.save_state()
        
        logger.info(f"✅ Closed position: {symbol} | P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)")
        
        return {
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'proceeds': proceeds
        }
    
    def update_position_prices(self, prices: Dict[str, float]):
        """Update current prices for all positions"""
        for symbol, position in self.state['positions'].items():
            if symbol in prices:
                current_price = prices[symbol]
                entry_price = position['entry_price']
                quantity = position['quantity']
                
                position['current_price'] = current_price
                position['unrealized_pnl'] = (current_price - entry_price) * quantity
                position['unrealized_pnl_pct'] = ((current_price - entry_price) / entry_price) * 100
        
        self.save_state()
    
    def record_trade(self, action: str, symbol: str, quantity: int, price: float, 
                     reasoning: str = "", pnl: float = 0, pnl_pct: float = 0):
        """Record a trade in history"""
        trade = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'value': quantity * price,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reasoning': reasoning
        }
        self.state['trade_history'].append(trade)
    
    def record_daily_value(self, total_value: float):
        """Record daily portfolio value for tracking"""
        today = datetime.now().date().isoformat()
        
        # Only record once per day
        if not self.state['daily_values'] or self.state['daily_values'][-1]['date'] != today:
            self.state['daily_values'].append({
                'date': today,
                'value': total_value,
                'return_pct': ((total_value - self.initial_capital) / self.initial_capital) * 100
            })
            self.save_state()
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value"""
        self.update_position_prices(current_prices)
        
        positions_value = sum(
            pos['quantity'] * pos['current_price']
            for pos in self.state['positions'].values()
        )
        
        return self.state['cash'] + positions_value
    
    def get_portfolio_state(self, current_prices: Dict[str, float]) -> Dict:
        """Get complete portfolio state"""
        total_value = self.get_portfolio_value(current_prices)
        positions_value = total_value - self.state['cash']
        
        # Calculate today's P&L
        daily_pnl = 0
        daily_pnl_pct = 0
        if self.state['daily_values']:
            yesterday_value = self.state['daily_values'][-1]['value']
            daily_pnl = total_value - yesterday_value
            daily_pnl_pct = (daily_pnl / yesterday_value) * 100 if yesterday_value > 0 else 0
        
        return {
            'cash': self.state['cash'],
            'positions': list(self.state['positions'].values()),
            'num_positions': len(self.state['positions']),
            'positions_value': positions_value,
            'total_value': total_value,
            'initial_capital': self.initial_capital,
            'total_return': total_value - self.initial_capital,
            'total_return_pct': ((total_value - self.initial_capital) / self.initial_capital) * 100,
            'daily_pnl': daily_pnl,
            'daily_pnl_pct': daily_pnl_pct,
            'num_trades': len(self.state['trade_history'])
        }
    
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.state['trade_history']:
            return {}
        
        trades = self.state['trade_history']
        closed_trades = [t for t in trades if t['action'] == 'SELL']
        
        if not closed_trades:
            return {
                'total_trades': len(trades),
                'closed_trades': 0
            }
        
        winning_trades = [t for t in closed_trades if t['pnl'] > 0]
        losing_trades = [t for t in closed_trades if t['pnl'] < 0]
        
        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0
        
        avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        total_pnl = sum(t['pnl'] for t in closed_trades)
        
        return {
            'total_trades': len(trades),
            'closed_trades': len(closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_pnl': total_pnl,
            'best_trade': max(closed_trades, key=lambda x: x['pnl'])['pnl'] if closed_trades else 0,
            'worst_trade': min(closed_trades, key=lambda x: x['pnl'])['pnl'] if closed_trades else 0
        }
    
    def get_trade_history(self, limit: int = 10) -> List[Dict]:
        """Get recent trade history"""
        return self.state['trade_history'][-limit:]
