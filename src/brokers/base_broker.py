"""
Base Broker Interface
Abstract base class that all broker implementations must inherit from
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List


class BaseBroker(ABC):
    """
    Abstract base class for broker implementations.
    All brokers (Alpaca, Interactive Brokers, TD Ameritrade, etc.) must implement these methods.
    """

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        """
        Initialize broker with credentials

        Args:
            api_key: API key for broker
            secret_key: Secret key for broker
            paper: Whether to use paper trading (default: True)
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.paper = paper

    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the broker and verify credentials

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def get_account_info(self) -> Dict:
        """
        Get current account information

        Returns:
            Dictionary with account details:
            {
                'cash': float,
                'portfolio_value': float,
                'buying_power': float,
                'equity': float,
                'last_equity': float,
                'daytrade_count': int,
                'pattern_day_trader': bool
            }
        """
        pass

    @abstractmethod
    def get_positions(self) -> Dict[str, Dict]:
        """
        Get all current positions

        Returns:
            Dictionary mapping symbol to position details:
            {
                'AAPL': {
                    'symbol': str,
                    'quantity': int,
                    'entry_price': float,
                    'current_price': float,
                    'market_value': float,
                    'cost_basis': float,
                    'unrealized_pnl': float,
                    'unrealized_pnl_pct': float
                }
            }
        """
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a symbol

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Current price or None if unavailable
        """
        pass

    @abstractmethod
    def execute_buy(self, symbol: str, quantity: int, limit_price: Optional[float] = None) -> Optional[Dict]:
        """
        Execute a buy order

        Args:
            symbol: Stock symbol
            quantity: Number of shares
            limit_price: Optional limit price (uses market order if None)

        Returns:
            Order details:
            {
                'order_id': str,
                'symbol': str,
                'quantity': int,
                'side': 'BUY',
                'type': 'market' or 'limit',
                'status': str,
                'submitted_at': str
            }
            Returns None if order fails
        """
        pass

    @abstractmethod
    def execute_sell(self, symbol: str, quantity: int, limit_price: Optional[float] = None) -> Optional[Dict]:
        """
        Execute a sell order

        Args:
            symbol: Stock symbol
            quantity: Number of shares
            limit_price: Optional limit price (uses market order if None)

        Returns:
            Order details (same structure as execute_buy)
            Returns None if order fails
        """
        pass

    @abstractmethod
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """
        Get status of an order

        Args:
            order_id: Order identifier

        Returns:
            Order status:
            {
                'order_id': str,
                'status': str,
                'filled_qty': int,
                'filled_avg_price': float
            }
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order

        Args:
            order_id: Order identifier

        Returns:
            True if cancelled successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_open_orders(self) -> List:
        """
        Get all open orders

        Returns:
            List of open orders
        """
        pass

    @abstractmethod
    def close_all_positions(self) -> bool:
        """
        Close all open positions (emergency use)

        Returns:
            True if successful, False otherwise
        """
        pass

    @property
    @abstractmethod
    def broker_name(self) -> str:
        """
        Return the name of the broker

        Returns:
            Broker name (e.g., 'Alpaca', 'Interactive Brokers')
        """
        pass
