"""
Binance Broker Implementation
Supports crypto trading on Binance (including testnet for paper trading)
"""
from binance.client import Client
from binance.enums import *
from typing import Dict, Optional, List
from decimal import Decimal
from .base_broker import BaseBroker
from ..utils.logger import logger


class BinanceBroker(BaseBroker):
    """Binance crypto broker implementation"""

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        """
        Initialize Binance broker

        Args:
            api_key: Binance API key
            secret_key: Binance secret key
            paper: Whether to use testnet (paper trading) (default: True)
        """
        super().__init__(api_key, secret_key, paper)
        self.client = None
        self.testnet = paper

    def connect(self) -> bool:
        """Connect to Binance and verify credentials"""
        try:
            # Initialize Binance client
            self.client = Client(
                api_key=self.api_key,
                api_secret=self.secret_key,
                testnet=self.testnet  # Use testnet for paper trading
            )

            # Test connection by getting account info
            account = self.client.get_account()

            # Get total balance in USDT equivalent
            total_value = self._calculate_total_value(account)

            logger.info(f"✅ Connected to {self.broker_name} ({'Testnet' if self.testnet else 'Live'} Trading)")
            logger.info(f"   Account Value: ${total_value:.2f} USDT")
            logger.info(f"   Can Trade: {account['canTrade']}")
            logger.info(f"   Can Withdraw: {account['canWithdraw']}")

            return True

        except Exception as e:
            logger.error(f"Failed to connect to {self.broker_name}: {e}")
            return False

    def _calculate_total_value(self, account: Dict) -> float:
        """Calculate total account value in USDT"""
        try:
            total = 0.0
            for balance in account['balances']:
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total_asset = free + locked

                if total_asset > 0:
                    if asset == 'USDT':
                        total += total_asset
                    else:
                        # Try to get price in USDT
                        try:
                            symbol = f"{asset}USDT"
                            ticker = self.client.get_symbol_ticker(symbol=symbol)
                            price = float(ticker['price'])
                            total += total_asset * price
                        except:
                            # If we can't get USDT price, skip this asset
                            pass
            return total
        except Exception as e:
            logger.warning(f"Could not calculate total value: {e}")
            return 0.0

    def get_account_info(self) -> Dict:
        """Get current account information"""
        try:
            account = self.client.get_account()

            # Find USDT balance
            usdt_balance = 0.0
            for balance in account['balances']:
                if balance['asset'] == 'USDT':
                    usdt_balance = float(balance['free']) + float(balance['locked'])
                    break

            total_value = self._calculate_total_value(account)

            return {
                'cash': usdt_balance,  # USDT available
                'portfolio_value': total_value,  # Total value in USDT
                'buying_power': usdt_balance,  # Same as cash for crypto
                'equity': total_value,
                'last_equity': total_value,  # Binance doesn't track this
                'daytrade_count': 0,  # Not applicable for crypto
                'pattern_day_trader': False  # Not applicable for crypto
            }
        except Exception as e:
            logger.error(f"Error getting account info from {self.broker_name}: {e}")
            return {}

    def get_positions(self) -> Dict[str, Dict]:
        """Get all current positions"""
        try:
            account = self.client.get_account()
            positions = {}

            for balance in account['balances']:
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked

                # Only include non-zero balances (excluding USDT which is "cash")
                if total > 0 and asset != 'USDT':
                    symbol = f"{asset}USDT"

                    try:
                        # Get current price
                        ticker = self.client.get_symbol_ticker(symbol=symbol)
                        current_price = float(ticker['price'])
                        market_value = total * current_price

                        # We don't have entry price from Binance API
                        # Would need to track this separately in production
                        positions[symbol] = {
                            'symbol': symbol,
                            'quantity': total,
                            'entry_price': current_price,  # Approximation
                            'current_price': current_price,
                            'market_value': market_value,
                            'cost_basis': market_value,  # Approximation
                            'unrealized_pnl': 0.0,  # Need historical data
                            'unrealized_pnl_pct': 0.0
                        }
                    except Exception as e:
                        logger.warning(f"Could not get price for {symbol}: {e}")
                        continue

            return positions
        except Exception as e:
            logger.error(f"Error getting positions from {self.broker_name}: {e}")
            return {}

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a symbol

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT', 'ETHUSDT')
        """
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Error getting price for {symbol} from {self.broker_name}: {e}")
            return None

    def _format_quantity(self, symbol: str, quantity: float) -> str:
        """Format quantity according to symbol's precision requirements"""
        try:
            # Get symbol info to know precision
            info = self.client.get_symbol_info(symbol)

            # Find LOT_SIZE filter
            for f in info['filters']:
                if f['filterType'] == 'LOT_SIZE':
                    step_size = f['stepSize']
                    # Count decimal places in step size
                    precision = len(step_size.rstrip('0').split('.')[-1])
                    return f"{quantity:.{precision}f}"

            return str(quantity)
        except:
            # Default to 8 decimal places for crypto
            return f"{quantity:.8f}"

    def execute_buy(self, symbol: str, quantity: int, limit_price: Optional[float] = None) -> Optional[Dict]:
        """
        Execute a buy order

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            quantity: Amount to buy (in base currency, or USDT if negative)
            limit_price: Optional limit price (uses market order if None)
        """
        try:
            # For crypto, if quantity is given as shares, we need to format it properly
            formatted_qty = self._format_quantity(symbol, abs(quantity))

            if limit_price:
                # Limit order
                order = self.client.create_order(
                    symbol=symbol,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=formatted_qty,
                    price=f"{limit_price:.8f}"
                )
                logger.info(f"[{self.broker_name}] Submitting LIMIT BUY: {formatted_qty} {symbol} @ ${limit_price:.2f}")
            else:
                # Market order
                order = self.client.create_order(
                    symbol=symbol,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_MARKET,
                    quantity=formatted_qty
                )
                logger.info(f"[{self.broker_name}] Submitting MARKET BUY: {formatted_qty} {symbol}")

            logger.info(f"✅ [{self.broker_name}] BUY order submitted: {order['orderId']}")

            return {
                'order_id': str(order['orderId']),
                'symbol': order['symbol'],
                'quantity': float(order['origQty']),
                'side': 'BUY',
                'type': 'limit' if limit_price else 'market',
                'status': order['status'].lower(),
                'submitted_at': str(order['transactTime'])
            }

        except Exception as e:
            logger.error(f"[{self.broker_name}] Error executing BUY order for {symbol}: {e}")
            return None

    def execute_sell(self, symbol: str, quantity: int, limit_price: Optional[float] = None) -> Optional[Dict]:
        """
        Execute a sell order

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            quantity: Amount to sell
            limit_price: Optional limit price (uses market order if None)
        """
        try:
            formatted_qty = self._format_quantity(symbol, abs(quantity))

            if limit_price:
                # Limit order
                order = self.client.create_order(
                    symbol=symbol,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=formatted_qty,
                    price=f"{limit_price:.8f}"
                )
                logger.info(f"[{self.broker_name}] Submitting LIMIT SELL: {formatted_qty} {symbol} @ ${limit_price:.2f}")
            else:
                # Market order
                order = self.client.create_order(
                    symbol=symbol,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quantity=formatted_qty
                )
                logger.info(f"[{self.broker_name}] Submitting MARKET SELL: {formatted_qty} {symbol}")

            logger.info(f"✅ [{self.broker_name}] SELL order submitted: {order['orderId']}")

            return {
                'order_id': str(order['orderId']),
                'symbol': order['symbol'],
                'quantity': float(order['origQty']),
                'side': 'SELL',
                'type': 'limit' if limit_price else 'market',
                'status': order['status'].lower(),
                'submitted_at': str(order['transactTime'])
            }

        except Exception as e:
            logger.error(f"[{self.broker_name}] Error executing SELL order for {symbol}: {e}")
            return None

    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """Get status of an order - NOTE: Requires symbol parameter in Binance"""
        try:
            # Binance requires symbol to query order
            # This is a limitation - we'd need to store symbol with order_id
            # For now, get all open orders and search
            orders = self.client.get_open_orders()

            for order in orders:
                if str(order['orderId']) == order_id:
                    return {
                        'order_id': str(order['orderId']),
                        'status': order['status'].lower(),
                        'filled_qty': float(order['executedQty']),
                        'filled_avg_price': float(order['price']) if order.get('price') else 0.0
                    }

            # If not in open orders, it might be filled or cancelled
            return {
                'order_id': order_id,
                'status': 'unknown',
                'filled_qty': 0,
                'filled_avg_price': 0.0
            }
        except Exception as e:
            logger.error(f"[{self.broker_name}] Error getting order status: {e}")
            return None

    def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        """
        Cancel an order

        Args:
            order_id: Order identifier
            symbol: Trading pair (required for Binance)
        """
        try:
            if not symbol:
                logger.error(f"[{self.broker_name}] Symbol required to cancel order on Binance")
                return False

            self.client.cancel_order(symbol=symbol, orderId=order_id)
            logger.info(f"✅ [{self.broker_name}] Cancelled order: {order_id}")
            return True
        except Exception as e:
            logger.error(f"[{self.broker_name}] Error cancelling order: {e}")
            return False

    def get_open_orders(self) -> List:
        """Get all open orders"""
        try:
            return self.client.get_open_orders()
        except Exception as e:
            logger.error(f"[{self.broker_name}] Error getting open orders: {e}")
            return []

    def close_all_positions(self) -> bool:
        """Close all open positions (emergency use)"""
        try:
            account = self.client.get_account()
            closed_count = 0

            for balance in account['balances']:
                asset = balance['asset']
                free = float(balance['free'])

                if free > 0 and asset != 'USDT':
                    symbol = f"{asset}USDT"
                    try:
                        # Market sell all
                        formatted_qty = self._format_quantity(symbol, free)
                        self.client.create_order(
                            symbol=symbol,
                            side=SIDE_SELL,
                            type=ORDER_TYPE_MARKET,
                            quantity=formatted_qty
                        )
                        closed_count += 1
                        logger.info(f"[{self.broker_name}] Closed position: {symbol}")
                    except Exception as e:
                        logger.error(f"[{self.broker_name}] Error closing {symbol}: {e}")

            logger.warning(f"⚠️ [{self.broker_name}] Closed {closed_count} positions")
            return True

        except Exception as e:
            logger.error(f"[{self.broker_name}] Error closing all positions: {e}")
            return False

    @property
    def broker_name(self) -> str:
        """Return the broker name"""
        return "Binance"
