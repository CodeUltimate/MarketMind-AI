"""
Broker Factory
Creates broker instances based on configuration
"""
from typing import Optional
from .base_broker import BaseBroker
from .alpaca_broker import AlpacaBroker
from .binance_broker import BinanceBroker
from ..utils.logger import logger


class BrokerFactory:
    """Factory for creating broker instances"""

    # Registry of available brokers
    _brokers = {
        'alpaca': AlpacaBroker,
        'binance': BinanceBroker,
        # Future brokers can be added here:
        # 'interactive_brokers': InteractiveBrokersBroker,
        # 'td_ameritrade': TDAmeritradeBroker,
        # 'robinhood': RobinhoodBroker,
        # 'webull': WebullBroker,
    }

    @classmethod
    def create(cls, broker_name: str, api_key: str, secret_key: str, paper: bool = True) -> Optional[BaseBroker]:
        """
        Create a broker instance

        Args:
            broker_name: Name of the broker ('alpaca', 'interactive_brokers', etc.)
            api_key: API key for the broker
            secret_key: Secret key for the broker
            paper: Whether to use paper trading (default: True)

        Returns:
            Broker instance or None if broker not found

        Raises:
            ValueError: If broker_name is not supported
        """
        broker_name_lower = broker_name.lower()

        if broker_name_lower not in cls._brokers:
            available = ', '.join(cls._brokers.keys())
            error_msg = f"Unsupported broker: '{broker_name}'. Available brokers: {available}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        broker_class = cls._brokers[broker_name_lower]
        logger.info(f"Creating {broker_name} broker instance...")

        try:
            broker = broker_class(api_key=api_key, secret_key=secret_key, paper=paper)

            # Attempt to connect
            if broker.connect():
                logger.info(f"✅ Successfully initialized {broker.broker_name} broker")
                return broker
            else:
                logger.error(f"Failed to connect to {broker_name}")
                return None

        except Exception as e:
            logger.error(f"Error creating {broker_name} broker: {e}")
            raise

    @classmethod
    def register_broker(cls, name: str, broker_class: type):
        """
        Register a new broker implementation

        This allows you to add custom brokers at runtime.

        Args:
            name: Name to register the broker under (e.g., 'my_custom_broker')
            broker_class: Class that inherits from BaseBroker

        Example:
            >>> from my_broker import MyCustomBroker
            >>> BrokerFactory.register_broker('custom', MyCustomBroker)
            >>> broker = BrokerFactory.create('custom', api_key, secret_key)
        """
        if not issubclass(broker_class, BaseBroker):
            raise TypeError(f"{broker_class.__name__} must inherit from BaseBroker")

        cls._brokers[name.lower()] = broker_class
        logger.info(f"Registered new broker: {name}")

    @classmethod
    def get_available_brokers(cls) -> list:
        """
        Get list of available broker names

        Returns:
            List of broker names that can be used with create()
        """
        return list(cls._brokers.keys())

    @classmethod
    def is_broker_available(cls, broker_name: str) -> bool:
        """
        Check if a broker is available

        Args:
            broker_name: Name of the broker to check

        Returns:
            True if broker is available, False otherwise
        """
        return broker_name.lower() in cls._brokers
