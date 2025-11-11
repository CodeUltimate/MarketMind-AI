"""
Mock Broker for Testing
Simulates trading without real API calls
"""
from typing import Dict, Optional, List
import random
from datetime import datetime
from .base_broker import BaseBroker
from ..utils.logger import logger


class MockBroker(BaseBroker):
    """Mock broker for testing - simulates trading without API calls"""

    def __init__(self, api_key: str = "mock", secret_key: str = "mock", paper: bool = True):
        """Initialize mock broker with simulated data"""
        super().__init__(api_key, secret_key, paper)

        # Simulated account
        self.cash = 10000.0
        self.positions = {}
        self.orders = []
        self.order_counter = 1000

        # Simulated market prices (will fluctuate)
        self.prices = {
            'BTCUSDT': 100000.0,
            'ETHUSDT': 3500.0,
            'BNBUSDT': 600.0,
            'AAPL': 180.0,
            'TSLA': 250.0,
            'SPY': 450.0
        }

        self.connected = False

    def connect(self) -> bool:
        """Simulate connection"""
        logger.info(f"✅ Connected to {self.broker_name} (Mock Trading)")
        logger.info(f"   Account Value: ${self.cash:.2f}")
        logger.info(f"   Mode: Simulation")
        self.connected = True
        return True

    def get_account_info(self) -> Dict:
        """Get simulated account info"""
        portfolio_value = self.cash
        for symbol, pos in self.positions.items():
            current_price = self.get_current_price(symbol)
            if current_price:
                portfolio_value += pos['quantity'] * current_price

        return {
            'cash': self.cash,
            'portfolio_value': portfolio_value,
            'buying_power': self.cash,
            'equity': portfolio_value,
            'last_equity': portfolio_value,
            'daytrade_count': 0,
            'pattern_day_trader': False
        }

    def get_positions(self) -> Dict[str, Dict]:
        """Get simulated positions"""
        result = {}
        for symbol, pos in self.positions.items():
            current_price = self.get_current_price(symbol)
            if current_price:
                market_value = pos['quantity'] * current_price
                cost_basis = pos['quantity'] * pos['entry_price']
                unrealized_pnl = market_value - cost_basis
                unrealized_pnl_pct = (unrealized_pnl / cost_basis) * 100 if cost_basis > 0 else 0

                result[symbol] = {
                    'symbol': symbol,
                    'quantity': pos['quantity'],
                    'entry_price': pos['entry_price'],
                    'current_price': current_price,
                    'market_value': market_value,
                    'cost_basis': cost_basis,
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pnl_pct': unrealized_pnl_pct
                }
        return result

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get simulated price with random fluctuation"""
        if symbol not in self.prices:
            # Generate a random price for unknown symbols
            self.prices[symbol] = random.uniform(1, 1000)

        # Simulate small price movements (-1% to +1%)
        base_price = self.prices[symbol]
        fluctuation = random.uniform(-0.01, 0.01)
        current_price = base_price * (1 + fluctuation)

        # Update stored price
        self.prices[symbol] = current_price

        return current_price

    def execute_buy(self, symbol: str, quantity: int, limit_price: Optional[float] = None) -> Optional[Dict]:
        """Simulate buy order"""
        current_price = limit_price or self.get_current_price(symbol)
        if not current_price:
            return None

        cost = quantity * current_price

        if cost > self.cash:
            logger.error(f"[{self.broker_name}] Insufficient funds: need ${cost:.2f}, have ${self.cash:.2f}")
            return None

        # Execute the buy
        self.cash -= cost

        if symbol in self.positions:
            # Add to existing position (average price)
            existing = self.positions[symbol]
            total_qty = existing['quantity'] + quantity
            avg_price = ((existing['quantity'] * existing['entry_price']) + (quantity * current_price)) / total_qty
            self.positions[symbol] = {
                'quantity': total_qty,
                'entry_price': avg_price
            }
        else:
            self.positions[symbol] = {
                'quantity': quantity,
                'entry_price': current_price
            }

        order_id = f"MOCK_{self.order_counter}"
        self.order_counter += 1

        logger.info(f"[{self.broker_name}] ✅ BUY: {quantity} {symbol} @ ${current_price:.2f} = ${cost:.2f}")

        return {
            'order_id': order_id,
            'symbol': symbol,
            'quantity': quantity,
            'side': 'BUY',
            'type': 'limit' if limit_price else 'market',
            'status': 'filled',
            'submitted_at': str(datetime.now())
        }

    def execute_sell(self, symbol: str, quantity: int, limit_price: Optional[float] = None) -> Optional[Dict]:
        """Simulate sell order"""
        if symbol not in self.positions:
            logger.error(f"[{self.broker_name}] No position in {symbol} to sell")
            return None

        if self.positions[symbol]['quantity'] < quantity:
            logger.error(f"[{self.broker_name}] Insufficient quantity: have {self.positions[symbol]['quantity']}, trying to sell {quantity}")
            return None

        current_price = limit_price or self.get_current_price(symbol)
        if not current_price:
            return None

        proceeds = quantity * current_price
        self.cash += proceeds

        # Update position
        self.positions[symbol]['quantity'] -= quantity
        if self.positions[symbol]['quantity'] == 0:
            del self.positions[symbol]

        order_id = f"MOCK_{self.order_counter}"
        self.order_counter += 1

        logger.info(f"[{self.broker_name}] ✅ SELL: {quantity} {symbol} @ ${current_price:.2f} = ${proceeds:.2f}")

        return {
            'order_id': order_id,
            'symbol': symbol,
            'quantity': quantity,
            'side': 'SELL',
            'type': 'limit' if limit_price else 'market',
            'status': 'filled',
            'submitted_at': str(datetime.now())
        }

    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """Get simulated order status"""
        return {
            'order_id': order_id,
            'status': 'filled',
            'filled_qty': 1,
            'filled_avg_price': 100.0
        }

    def cancel_order(self, order_id: str) -> bool:
        """Simulate order cancellation"""
        logger.info(f"[{self.broker_name}] Cancelled order: {order_id}")
        return True

    def get_open_orders(self) -> List:
        """Get simulated open orders"""
        return []

    def close_all_positions(self) -> bool:
        """Close all simulated positions"""
        for symbol in list(self.positions.keys()):
            quantity = self.positions[symbol]['quantity']
            self.execute_sell(symbol, quantity)

        logger.warning(f"⚠️ [{self.broker_name}] Closed all positions")
        return True

    @property
    def broker_name(self) -> str:
        """Return the broker name"""
        return "MockBroker"

    def set_price(self, symbol: str, price: float):
        """Set a specific price for testing"""
        self.prices[symbol] = price

    def simulate_market_movement(self, volatility: float = 0.02):
        """Simulate market price movements"""
        for symbol in self.prices:
            change = random.uniform(-volatility, volatility)
            self.prices[symbol] *= (1 + change)
