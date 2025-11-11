"""
Simple Backtesting Example
Run this to see how backtesting works with your own symbols
"""
import sys
sys.path.insert(0, '/Users/cebrailergisi/Documents/projects/ai-trading-bot')

from src.backtesting import BacktestEngine
from datetime import datetime, timedelta


def main():
    print("\n" + "="*70)
    print("  📊 SIMPLE BACKTESTING EXAMPLE")
    print("="*70)

    # Create backtesting engine with $10,000 starting capital
    engine = BacktestEngine(initial_capital=10000)

    # Set up dates (last 5 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)

    print(f"\n📅 Testing period: {start_date.date()} to {end_date.date()}")
    print(f"💵 Initial capital: $10,000")

    # Test 1: Buy and Hold Strategy
    print("\n" + "-"*70)
    print("Test 1: Buy and Hold Strategy (AAPL)")
    print("-"*70)

    result = engine.run_simple_strategy(
        symbol='AAPL',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        strategy='buy_and_hold'
    )

    if 'error' not in result:
        print(f"\n✅ Results:")
        print(f"   Final Value: ${result['final_value']:,.2f}")
        print(f"   Total Return: {result['total_return_pct']:.2f}%")
        print(f"   Annual Return: {result['metrics']['annual_return_pct']:.2f}%")
        print(f"   Sharpe Ratio: {result['metrics']['sharpe_ratio']:.2f}")

    # Test 2: Momentum Strategy
    print("\n" + "-"*70)
    print("Test 2: Momentum Strategy (TSLA)")
    print("-"*70)

    result = engine.run_simple_strategy(
        symbol='TSLA',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        strategy='momentum'
    )

    if 'error' not in result:
        print(f"\n✅ Results:")
        print(f"   Final Value: ${result['final_value']:,.2f}")
        print(f"   Total Return: {result['total_return_pct']:.2f}%")
        print(f"   Number of Trades: {result['metrics']['num_trades']}")
        print(f"   Win Rate: {result['metrics']['win_rate_pct']:.2f}%")

    # Test 3: Compare Strategies on Same Symbol
    print("\n" + "-"*70)
    print("Test 3: Strategy Comparison (SPY)")
    print("-"*70)

    engine.compare_strategies(
        symbol='SPY',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

    print("\n" + "="*70)
    print("  ✅ BACKTESTING COMPLETE!")
    print("="*70)
    print("\nNext Steps:")
    print("1. Try different symbols by editing this file")
    print("2. Adjust the time period (change 5*365 to 10*365 for 10 years)")
    print("3. Read BACKTESTING_GUIDE.md to implement your own strategies")
    print("4. Compare your results against buy-and-hold baseline")
    print("\n")


if __name__ == "__main__":
    main()
