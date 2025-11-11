"""
Alpaca Broker Implementation
"""
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from typing import Dict, Optional, List
from .base_broker import BaseBroker
from ..utils.logger import logger


class AlpacaBroker(BaseBroker):
    """Alpaca broker implementation"""

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        """
        Initialize Alpaca broker

        Args:
            api_key: Alpaca API key
            secret_key: Alpaca secret key
            paper: Whether to use paper trading (default: True)
        """
        super().__init__(api_key, secret_key, paper)
        self.trading_client = None
        self.data_client = None

    def connect(self) -> bool:
        """Connect to Alpaca and verify credentials"""
        try:
            # Initialize Alpaca clients
            self.trading_client = TradingClient(
                api_key=self.api_key,
                secret_key=self.secret_key,
                paper=self.paper
            )

            self.data_client = StockHistoricalDataClient(
                api_key=self.api_key,
                secret_key=self.secret_key
            )

            # Test connection
            account = self.trading_client.get_account()
            logger.info(f"✅ Connected to {self.broker_name} ({'Paper' if self.paper else 'Live'} Trading)")
            logger.info(f"   Account Value: ${float(account.portfolio_value):.2f}")
            logger.info(f"   Buying Power: ${float(account.buying_power):.2f}")

            return True

        except Exception as e:
            logger.error(f"Failed to connect to {self.broker_name}: {e}")
            return False

    def get_account_info(self) -> Dict:
        """Get current account information"""
        try:
            account = self.trading_client.get_account()
            return {
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'equity': float(account.equity),
                'last_equity': float(account.last_equity),
                'daytrade_count': int(account.daytrade_count),
                'pattern_day_trader': account.pattern_day_trader
            }
        except Exception as e:
            logger.error(f"Error getting account info from {self.broker_name}: {e}")
            return {}

    def get_positions(self) -> Dict[str, Dict]:
        """Get current positions"""
        try:
            positions = self.trading_client.get_all_positions()
            return {
                pos.symbol: {
                    'symbol': pos.symbol,
                    'quantity': int(pos.qty),
                    'entry_price': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price),
                    'market_value': float(pos.market_value),
                    'cost_basis': float(pos.cost_basis),
                    'unrealized_pnl': float(pos.unrealized_pl),
                    'unrealized_pnl_pct': float(pos.unrealized_plpc) * 100
                }
                for pos in positions
            }
        except Exception as e:
            logger.error(f"Error getting positions from {self.broker_name}: {e}")
            return {}

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quote = self.data_client.get_stock_latest_quote(request)

            if symbol in quote:
                return float(quote[symbol].ask_price)
            return None
        except Exception as e:
            logger.error(f"Error getting price for {symbol} from {self.broker_name}: {e}")
            return None

    def execute_buy(self, symbol: str, quantity: int, limit_price: Optional[float] = None) -> Optional[Dict]:
        """
        Execute a buy order

        Args:
            symbol: Stock symbol
            quantity: Number of shares
            limit_price: Optional limit price (uses market order if None)

        Returns:
            Order details or None if failed
        """
        try:
            if limit_price:
                # Limit order
                order_request = LimitOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY,
                    limit_price=limit_price
                )
                logger.info(f"[{self.broker_name}] Submitting LIMIT BUY: {quantity} {symbol} @ ${limit_price:.2f}")
            else:
                # Market order
                order_request = MarketOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                )
                logger.info(f"[{self.broker_name}] Submitting MARKET BUY: {quantity} {symbol}")

            order = self.trading_client.submit_order(order_request)

            logger.info(f"✅ [{self.broker_name}] BUY order submitted: {order.id}")

            return {
                'order_id': str(order.id),
                'symbol': order.symbol,
                'quantity': int(order.qty),
                'side': 'BUY',
                'type': 'limit' if limit_price else 'market',
                'status': order.status,
                'submitted_at': str(order.submitted_at)
            }

        except Exception as e:
            logger.error(f"[{self.broker_name}] Error executing BUY order for {symbol}: {e}")
            return None

    def execute_sell(self, symbol: str, quantity: int, limit_price: Optional[float] = None) -> Optional[Dict]:
        """
        Execute a sell order

        Args:
            symbol: Stock symbol
            quantity: Number of shares
            limit_price: Optional limit price (uses market order if None)

        Returns:
            Order details or None if failed
        """
        try:
            if limit_price:
                # Limit order
                order_request = LimitOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY,
                    limit_price=limit_price
                )
                logger.info(f"[{self.broker_name}] Submitting LIMIT SELL: {quantity} {symbol} @ ${limit_price:.2f}")
            else:
                # Market order
                order_request = MarketOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
                logger.info(f"[{self.broker_name}] Submitting MARKET SELL: {quantity} {symbol}")

            order = self.trading_client.submit_order(order_request)

            logger.info(f"✅ [{self.broker_name}] SELL order submitted: {order.id}")

            return {
                'order_id': str(order.id),
                'symbol': order.symbol,
                'quantity': int(order.qty),
                'side': 'SELL',
                'type': 'limit' if limit_price else 'market',
                'status': order.status,
                'submitted_at': str(order.submitted_at)
            }

        except Exception as e:
            logger.error(f"[{self.broker_name}] Error executing SELL order for {symbol}: {e}")
            return None

    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """Get status of an order"""
        try:
            order = self.trading_client.get_order_by_id(order_id)
            return {
                'order_id': str(order.id),
                'status': order.status,
                'filled_qty': int(order.filled_qty) if order.filled_qty else 0,
                'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else 0
            }
        except Exception as e:
            logger.error(f"[{self.broker_name}] Error getting order status: {e}")
            return None

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            self.trading_client.cancel_order_by_id(order_id)
            logger.info(f"✅ [{self.broker_name}] Cancelled order: {order_id}")
            return True
        except Exception as e:
            logger.error(f"[{self.broker_name}] Error cancelling order: {e}")
            return False

    def get_open_orders(self) -> List:
        """Get all open orders"""
        try:
            return self.trading_client.get_orders()
        except Exception as e:
            logger.error(f"[{self.broker_name}] Error getting open orders: {e}")
            return []

    def close_all_positions(self) -> bool:
        """Close all open positions (emergency use)"""
        try:
            self.trading_client.close_all_positions(cancel_orders=True)
            logger.warning(f"⚠️ [{self.broker_name}] Closed all positions")
            return True
        except Exception as e:
            logger.error(f"[{self.broker_name}] Error closing all positions: {e}")
            return False

    @property
    def broker_name(self) -> str:
        """Return the broker name"""
        return "Alpaca"
