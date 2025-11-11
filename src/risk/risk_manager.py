"""
Risk Management Module
Handles position sizing, stop losses, and portfolio risk limits
"""
from typing import Dict, Optional, Tuple
from datetime import datetime, date
from ..utils.logger import logger
from config.config import Config

class RiskManager:
    """Manages trading risk and position sizing"""
    
    def __init__(self):
        self.max_position_size_pct = Config.MAX_POSITION_SIZE_PCT
        self.max_portfolio_risk_pct = Config.MAX_PORTFOLIO_RISK_PCT
        self.per_trade_risk_pct = Config.PER_TRADE_RISK_PCT
        self.daily_loss_limit_pct = Config.DAILY_LOSS_LIMIT_PCT
        self.max_drawdown_pct = Config.MAX_DRAWDOWN_PCT
        
        self.daily_starting_value = None
        self.peak_value = None
        self.trading_paused = False
        self.pause_reason = None
        
    def check_circuit_breakers(self, portfolio_value: float, daily_pnl_pct: float) -> Tuple[bool, Optional[str]]:
        """
        Check if any circuit breakers should halt trading
        
        Returns:
            (should_halt, reason)
        """
        # Initialize daily tracking
        if self.daily_starting_value is None or datetime.now().date() > getattr(self, 'last_check_date', date.min):
            self.daily_starting_value = portfolio_value
            self.last_check_date = datetime.now().date()
            self.trading_paused = False
            self.pause_reason = None
        
        # Initialize peak tracking
        if self.peak_value is None or portfolio_value > self.peak_value:
            self.peak_value = portfolio_value
        
        # Check daily loss limit
        if daily_pnl_pct <= -self.daily_loss_limit_pct:
            self.trading_paused = True
            self.pause_reason = f"Daily loss limit hit: {daily_pnl_pct:.2f}% (limit: {self.daily_loss_limit_pct}%)"
            logger.warning(f"🚨 CIRCUIT BREAKER: {self.pause_reason}")
            return True, self.pause_reason
        
        # Check maximum drawdown
        current_drawdown_pct = ((self.peak_value - portfolio_value) / self.peak_value) * 100
        if current_drawdown_pct >= self.max_drawdown_pct:
            self.trading_paused = True
            self.pause_reason = f"Maximum drawdown hit: {current_drawdown_pct:.2f}% (limit: {self.max_drawdown_pct}%)"
            logger.warning(f"🚨 CIRCUIT BREAKER: {self.pause_reason}")
            return True, self.pause_reason
        
        return False, None
    
    def calculate_position_size(self, 
                                portfolio_value: float,
                                entry_price: float,
                                stop_loss_pct: float,
                                confidence: float = 0.8,
                                ai_suggested_size_pct: Optional[float] = None) -> Dict:
        """
        Calculate optimal position size based on risk parameters
        
        Returns:
            {
                'shares': int,
                'position_value': float,
                'risk_amount': float,
                'position_size_pct': float
            }
        """
        # Calculate risk-based position size
        risk_amount = portfolio_value * (self.per_trade_risk_pct / 100)
        stop_loss_distance = entry_price * (stop_loss_pct / 100)
        
        # Shares based on risk
        risk_based_shares = int(risk_amount / stop_loss_distance) if stop_loss_distance > 0 else 0
        
        # Calculate maximum shares based on position size limit
        max_position_value = portfolio_value * (self.max_position_size_pct / 100)
        max_shares = int(max_position_value / entry_price)
        
        # Use AI suggested size if provided, but cap it
        if ai_suggested_size_pct:
            ai_position_value = portfolio_value * (min(ai_suggested_size_pct, self.max_position_size_pct) / 100)
            ai_shares = int(ai_position_value / entry_price)
        else:
            ai_shares = risk_based_shares
        
        # Scale by confidence (lower confidence = smaller position)
        confidence_multiplier = confidence if confidence >= 0.7 else 0.5
        adjusted_shares = int(ai_shares * confidence_multiplier)
        
        # Take the minimum of all constraints
        final_shares = min(risk_based_shares, max_shares, adjusted_shares)
        
        # Ensure at least 1 share if we're trading
        final_shares = max(1, final_shares) if final_shares > 0 else 0
        
        position_value = final_shares * entry_price
        position_size_pct = (position_value / portfolio_value) * 100 if portfolio_value > 0 else 0
        
        return {
            'shares': final_shares,
            'position_value': position_value,
            'risk_amount': risk_amount,
            'position_size_pct': position_size_pct,
            'stop_loss_price': entry_price * (1 - stop_loss_pct / 100),
            'confidence_applied': confidence_multiplier
        }
    
    def validate_trade(self, 
                       action: str,
                       symbol: str,
                       shares: int,
                       price: float,
                       portfolio_value: float,
                       current_positions: Dict) -> Tuple[bool, str]:
        """
        Validate if a trade meets risk requirements
        
        Returns:
            (is_valid, reason)
        """
        if self.trading_paused:
            return False, f"Trading paused: {self.pause_reason}"
        
        if action == 'BUY':
            # Check if we have enough cash
            trade_value = shares * price
            
            # Check position size
            position_pct = (trade_value / portfolio_value) * 100
            if position_pct > self.max_position_size_pct:
                return False, f"Position size {position_pct:.1f}% exceeds limit {self.max_position_size_pct}%"
            
            # Check portfolio concentration
            num_positions = len(current_positions)
            if num_positions >= 5:  # Max 5 positions at once
                return False, "Maximum number of positions reached (5)"
            
            # Check if already have position in this symbol
            if symbol in current_positions:
                return False, f"Already have position in {symbol}"
        
        elif action == 'SELL':
            # Check if we have the position
            if symbol not in current_positions:
                return False, f"No position in {symbol} to sell"
            
            position = current_positions[symbol]
            if position['quantity'] < shares:
                return False, f"Insufficient shares: have {position['quantity']}, trying to sell {shares}"
        
        return True, "Trade validated"
    
    def calculate_stop_loss(self, entry_price: float, stop_loss_pct: float) -> float:
        """Calculate stop loss price"""
        return entry_price * (1 - stop_loss_pct / 100)
    
    def calculate_take_profit(self, entry_price: float, take_profit_pct: float) -> float:
        """Calculate take profit price"""
        return entry_price * (1 + take_profit_pct / 100)
    
    def check_stop_loss_hit(self, position: Dict, current_price: float) -> bool:
        """Check if stop loss has been hit"""
        if 'stop_loss' in position and position['stop_loss']:
            return current_price <= position['stop_loss']
        return False
    
    def check_take_profit_hit(self, position: Dict, current_price: float) -> bool:
        """Check if take profit has been hit"""
        if 'take_profit' in position and position['take_profit']:
            return current_price >= position['take_profit']
        return False
    
    def get_risk_metrics(self, portfolio_value: float) -> Dict:
        """Get current risk metrics"""
        daily_pnl_pct = 0
        if self.daily_starting_value:
            daily_pnl_pct = ((portfolio_value - self.daily_starting_value) / self.daily_starting_value) * 100
        
        drawdown_pct = 0
        if self.peak_value:
            drawdown_pct = ((self.peak_value - portfolio_value) / self.peak_value) * 100
        
        return {
            'daily_pnl_pct': daily_pnl_pct,
            'daily_loss_limit_pct': self.daily_loss_limit_pct,
            'days_loss_remaining_pct': self.daily_loss_limit_pct - abs(daily_pnl_pct),
            'current_drawdown_pct': drawdown_pct,
            'max_drawdown_pct': self.max_drawdown_pct,
            'drawdown_remaining_pct': self.max_drawdown_pct - drawdown_pct,
            'trading_paused': self.trading_paused,
            'pause_reason': self.pause_reason,
            'peak_value': self.peak_value,
            'daily_starting_value': self.daily_starting_value
        }
