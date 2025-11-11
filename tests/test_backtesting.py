"""
Test Backtesting Framework
Runs backtests on 10 years of historical data
"""
import sys
sys.path.insert(0, '/Users/cebrailergisi/Documents/projects/ai-trading-bot')

from src.backtesting.backtest_engine import BacktestEngine
from datetime import datetime, timedelta


def test_single_strategy():
    """Test a single strategy on 10 years of data"""
    print("\n" + "="*70)
    print("  TEST 1: Single Strategy Backtest (10 Years)")
    print("="*70)

    engine = BacktestEngine(initial_capital=10000)

    # Calculate dates (10 years back)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10*365)

    # Run buy-and-hold strategy on AAPL
    result = engine.run_simple_strategy(
        symbol='AAPL',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        strategy='buy_and_hold'
    )

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False

    # Print results
    print("\n📈 RESULTS:")
    print(f"   Initial Capital: ${result['initial_capital']:,.2f}")
    print(f"   Final Value: ${result['final_value']:,.2f}")
    print(f"   Total Return: {result['total_return_pct']:.2f}%")

    if 'metrics' in result:
        metrics = result['metrics']
        print(f"\n📊 METRICS:")
        print(f"   Annual Return: {metrics.get('annual_return_pct', 0):.2f}%")
        print(f"   Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"   Max Drawdown: {metrics.get('max_drawdown_pct', 0):.2f}%")
        print(f"   Number of Trades: {metrics.get('num_trades', 0)}")
        print(f"   Win Rate: {metrics.get('win_rate_pct', 0):.2f}%")

    return True


def test_strategy_comparison():
    """Compare multiple strategies on the same data"""
    print("\n" + "="*70)
    print("  TEST 2: Strategy Comparison (All 3 Strategies)")
    print("="*70)

    engine = BacktestEngine(initial_capital=10000)

    # Calculate dates (10 years back)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10*365)

    # Run comparison
    results = engine.compare_strategies(
        symbol='AAPL',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

    return len(results) == 3


def test_crypto_backtesting():
    """Test backtesting on crypto data"""
    print("\n" + "="*70)
    print("  TEST 3: Crypto Backtesting (BTC - 5 Years)")
    print("="*70)

    engine = BacktestEngine(initial_capital=10000)

    # 5 years for BTC (it's more volatile)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)

    result = engine.run_simple_strategy(
        symbol='BTC-USD',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        strategy='momentum'
    )

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False

    print("\n📈 BTC MOMENTUM STRATEGY RESULTS:")
    print(f"   Total Return: {result['total_return_pct']:.2f}%")
    print(f"   Final Value: ${result['final_value']:,.2f}")

    return True


def main():
    """Run all backtesting tests"""
    print("\n" + "="*70)
    print("  🔄 BACKTESTING FRAMEWORK TEST SUITE")
    print("="*70)
    print(f"\nStarting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests_passed = 0
    tests_failed = 0

    # Test 1: Single strategy
    try:
        if test_single_strategy():
            tests_passed += 1
            print("\n✅ TEST 1 PASSED")
        else:
            tests_failed += 1
            print("\n❌ TEST 1 FAILED")
    except Exception as e:
        tests_failed += 1
        print(f"\n❌ TEST 1 FAILED: {e}")

    # Test 2: Strategy comparison
    try:
        if test_strategy_comparison():
            tests_passed += 1
            print("\n✅ TEST 2 PASSED")
        else:
            tests_failed += 1
            print("\n❌ TEST 2 FAILED")
    except Exception as e:
        tests_failed += 1
        print(f"\n❌ TEST 2 FAILED: {e}")

    # Test 3: Crypto backtesting
    try:
        if test_crypto_backtesting():
            tests_passed += 1
            print("\n✅ TEST 3 PASSED")
        else:
            tests_failed += 1
            print("\n❌ TEST 3 FAILED")
    except Exception as e:
        tests_failed += 1
        print(f"\n❌ TEST 3 FAILED: {e}")

    # Print summary
    print("\n" + "="*70)
    print("  📊 BACKTESTING TEST SUMMARY")
    print("="*70)
    total_tests = tests_passed + tests_failed
    pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"\nTotal Tests: {total_tests}")
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"Pass Rate: {pass_rate:.1f}%")

    if tests_failed == 0:
        print("\n🎉 ALL BACKTESTING TESTS PASSED!")
        print("The backtesting framework is ready to use.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please review the failures above.")

    print("="*70 + "\n")


if __name__ == "__main__":
    main()
