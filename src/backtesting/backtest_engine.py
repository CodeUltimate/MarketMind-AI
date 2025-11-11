"""
Backtesting Engine
Simulates trading strategy on historical data
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from .historical_data import HistoricalDataProvider
from ..risk.risk_manager import RiskManager
from ..portfolio.portfolio_manager import PortfolioManager


class BacktestEngine:
    """Backtests trading strategies on historical data"""

    def __init__(self, initial_capital: float = 10000):
        """Initialize backtest engine"""
        self.initial_capital = initial_capital
        self.data_provider = HistoricalDataProvider()
        self.risk_manager = RiskManager()

        # Results tracking
        self.results = {
            'trades': [],
            'daily_values': [],
            'metrics': {}
        }

    def run_simple_strategy(self, symbol: str, start_date: str, end_date: str = None,
                           strategy: str = "buy_and_hold") -> Dict:
        """
        Run a simple strategy backtest

        Args:
            symbol: Symbol to trade
            start_date: Start date 'YYYY-MM-DD'
            end_date: End date 'YYYY-MM-DD'
            strategy: 'buy_and_hold' or 'random_trading' or 'momentum'

        Returns:
            Dictionary with backtest results
        """
        print(f"\n{'='*70}")
        print(f"  BACKTESTING: {strategy.upper()} - {symbol}")
        print(f"{'='*70}")

        # Get historical data
        data = self.data_provider.get_stock_data(symbol, start_date, end_date)
        if data is None or data.empty:
            return {'error': 'No data available'}

        print(f"📊 Data: {len(data)} days from {data.index[0].date()} to {data.index[-1].date()}")

        # Initialize portfolio
        portfolio_manager = PortfolioManager(self.initial_capital)
        cash = self.initial_capital
        shares = 0
        trades = []
        daily_values = []

        # Run strategy
        if strategy == "buy_and_hold":
            result = self._run_buy_and_hold(data, symbol, cash)
        elif strategy == "momentum":
            result = self._run_momentum_strategy(data, symbol, cash)
        elif strategy == "random_trading":
            result = self._run_random_strategy(data, symbol, cash)
        else:
            return {'error': f'Unknown strategy: {strategy}'}

        # Calculate metrics
        result['metrics'] = self._calculate_metrics(result, data)

        return result

    def _run_buy_and_hold(self, data: pd.DataFrame, symbol: str, initial_cash: float) -> Dict:
        """Simple buy and hold strategy"""
        print(f"\n📈 Strategy: Buy on day 1, hold until end")

        # Buy on first day
        first_price = data['Close'].iloc[0]
        shares = int(initial_cash / first_price)
        cash = initial_cash - (shares * first_price)

        print(f"   Day 1: BUY {shares} shares @ ${first_price:.2f}")
        print(f"   Remaining cash: ${cash:.2f}")

        # Track daily values
        daily_values = []
        for date, row in data.iterrows():
            value = cash + (shares * row['Close'])
            daily_values.append({
                'date': date,
                'value': value,
                'price': row['Close']
            })

        # Sell on last day
        last_price = data['Close'].iloc[-1]
        final_value = cash + (shares * last_price)

        print(f"   Last day: Portfolio value ${final_value:.2f}")
        print(f"   Final price: ${last_price:.2f}")

        return {
            'strategy': 'buy_and_hold',
            'symbol': symbol,
            'initial_capital': initial_cash,
            'final_value': final_value,
            'total_return_pct': ((final_value - initial_cash) / initial_cash) * 100,
            'daily_values': daily_values,
            'trades': [
                {'date': data.index[0], 'action': 'BUY', 'shares': shares, 'price': first_price},
                {'date': data.index[-1], 'action': 'SELL', 'shares': shares, 'price': last_price}
            ]
        }

    def _run_momentum_strategy(self, data: pd.DataFrame, symbol: str, initial_cash: float) -> Dict:
        """
        Momentum strategy: Buy when price crosses above 50-day MA, sell when crosses below

        This is a SIMPLE example - the AI bot would make smarter decisions!
        """
        print(f"\n📈 Strategy: Momentum (50-day moving average crossover)")

        # Calculate moving average
        data['MA50'] = data['Close'].rolling(window=50).mean()

        cash = initial_cash
        shares = 0
        trades = []
        daily_values = []
        position_open = False

        for i, (date, row) in enumerate(data.iterrows()):
            if i < 50:  # Need 50 days for MA
                value = cash + (shares * row['Close'])
                daily_values.append({'date': date, 'value': value, 'price': row['Close']})
                continue

            price = row['Close']
            ma = row['MA50']

            # Buy signal: price crosses above MA
            if not position_open and price > ma and cash > price:
                shares_to_buy = int(cash * 0.95 / price)  # Use 95% of cash
                if shares_to_buy > 0:
                    cost = shares_to_buy * price
                    cash -= cost
                    shares += shares_to_buy
                    position_open = True
                    trades.append({
                        'date': date,
                        'action': 'BUY',
                        'shares': shares_to_buy,
                        'price': price,
                        'value': cost
                    })

            # Sell signal: price crosses below MA
            elif position_open and price < ma and shares > 0:
                proceeds = shares * price
                cash += proceeds
                trades.append({
                    'date': date,
                    'action': 'SELL',
                    'shares': shares,
                    'price': price,
                    'value': proceeds
                })
                shares = 0
                position_open = False

            # Track daily value
            value = cash + (shares * price)
            daily_values.append({'date': date, 'value': value, 'price': price})

        # Close any open position at end
        if shares > 0:
            last_price = data['Close'].iloc[-1]
            proceeds = shares * last_price
            cash += proceeds
            trades.append({
                'date': data.index[-1],
                'action': 'SELL',
                'shares': shares,
                'price': last_price,
                'value': proceeds
            })

        final_value = cash

        print(f"   Total trades: {len(trades)}")
        print(f"   Final value: ${final_value:.2f}")

        return {
            'strategy': 'momentum',
            'symbol': symbol,
            'initial_capital': initial_cash,
            'final_value': final_value,
            'total_return_pct': ((final_value - initial_cash) / initial_cash) * 100,
            'daily_values': daily_values,
            'trades': trades
        }

    def _run_random_strategy(self, data: pd.DataFrame, symbol: str, initial_cash: float) -> Dict:
        """
        Random trading strategy - for comparison
        Randomly buys/sells to show why strategy matters
        """
        print(f"\n🎲 Strategy: Random Trading (baseline comparison)")

        np.random.seed(42)  # For reproducibility
        cash = initial_cash
        shares = 0
        trades = []
        daily_values = []

        for date, row in data.iterrows():
            price = row['Close']

            # Random decision every 30 days
            if np.random.random() < 0.033:  # ~1/30 chance per day
                if shares == 0 and cash > price:
                    # Buy
                    shares_to_buy = int(cash * 0.5 / price)
                    if shares_to_buy > 0:
                        cost = shares_to_buy * price
                        cash -= cost
                        shares += shares_to_buy
                        trades.append({'date': date, 'action': 'BUY', 'shares': shares_to_buy, 'price': price})
                elif shares > 0:
                    # Sell
                    proceeds = shares * price
                    cash += proceeds
                    trades.append({'date': date, 'action': 'SELL', 'shares': shares, 'price': price})
                    shares = 0

            value = cash + (shares * price)
            daily_values.append({'date': date, 'value': value, 'price': price})

        # Close position
        if shares > 0:
            last_price = data['Close'].iloc[-1]
            cash += shares * last_price
            trades.append({'date': data.index[-1], 'action': 'SELL', 'shares': shares, 'price': last_price})

        final_value = cash

        print(f"   Total trades: {len(trades)}")
        print(f"   Final value: ${final_value:.2f}")

        return {
            'strategy': 'random',
            'symbol': symbol,
            'initial_capital': initial_cash,
            'final_value': final_value,
            'total_return_pct': ((final_value - initial_cash) / initial_cash) * 100,
            'daily_values': daily_values,
            'trades': trades
        }

    def _calculate_metrics(self, result: Dict, data: pd.DataFrame) -> Dict:
        """Calculate performance metrics"""
        if 'error' in result:
            return {}

        daily_values = pd.DataFrame(result['daily_values'])
        daily_values.set_index('date', inplace=True)

        # Calculate returns
        daily_values['returns'] = daily_values['value'].pct_change()

        # Calculate metrics
        total_return = result['total_return_pct']
        num_years = len(data) / 252  # Trading days per year
        annual_return = ((result['final_value'] / result['initial_capital']) ** (1 / num_years) - 1) * 100 if num_years > 0 else 0

        # Sharpe ratio (assuming 2% risk-free rate)
        excess_returns = daily_values['returns'] - (0.02 / 252)
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else 0

        # Max drawdown
        cumulative = (1 + daily_values['returns']).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100

        # Win rate
        trades = result.get('trades', [])
        if len(trades) >= 2:
            profitable_trades = 0
            total_trades = 0
            for i in range(0, len(trades) - 1, 2):
                if i + 1 < len(trades):
                    buy_price = trades[i]['price']
                    sell_price = trades[i + 1]['price']
                    if sell_price > buy_price:
                        profitable_trades += 1
                    total_trades += 1
            win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
        else:
            win_rate = 0

        return {
            'total_return_pct': total_return,
            'annual_return_pct': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': max_drawdown,
            'num_trades': len(trades),
            'win_rate_pct': win_rate,
            'total_days': len(data)
        }

    def compare_strategies(self, symbol: str, start_date: str, end_date: str = None):
        """
        Compare multiple strategies on the same data

        Args:
            symbol: Symbol to trade
            start_date: Start date
            end_date: End date
        """
        strategies = ['buy_and_hold', 'momentum', 'random_trading']
        results = {}

        for strategy in strategies:
            result = self.run_simple_strategy(symbol, start_date, end_date, strategy)
            results[strategy] = result

        # Print comparison
        self._print_comparison(results)

        return results

    def _print_comparison(self, results: Dict):
        """Print strategy comparison table"""
        print(f"\n{'='*70}")
        print(f"  📊 STRATEGY COMPARISON")
        print(f"{'='*70}\n")

        print(f"{'Strategy':<20} {'Return':<12} {'Annual':<12} {'Sharpe':<10} {'Max DD':<10}")
        print("-" * 70)

        for strategy, result in results.items():
            if 'error' in result:
                print(f"{strategy:<20} ERROR")
                continue

            metrics = result.get('metrics', {})
            print(f"{strategy:<20} "
                  f"{result.get('total_return_pct', 0):>10.2f}%  "
                  f"{metrics.get('annual_return_pct', 0):>10.2f}%  "
                  f"{metrics.get('sharpe_ratio', 0):>9.2f}  "
                  f"{metrics.get('max_drawdown_pct', 0):>9.2f}%")

        print("\n" + "="*70)
