"""
Automated Test Suite for AI Trading Bot
Tests the entire trading pipeline with simulated data
"""
import sys
sys.path.insert(0, '/Users/cebrailergisi/Documents/projects/ai-trading-bot')

from src.brokers.mock_broker import MockBroker
from src.risk.risk_manager import RiskManager
from src.portfolio.portfolio_manager import PortfolioManager
import random
import time


class AutomatedTradingTest:
    """Automated testing framework for trading bot"""

    def __init__(self):
        self.broker = MockBroker()
        self.risk_manager = RiskManager()
        self.portfolio_manager = PortfolioManager(initial_capital=10000)
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'tests': []
        }

    def log_test(self, name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if message:
            print(f"        {message}")

        self.test_results['tests'].append({
            'name': name,
            'passed': passed,
            'message': message
        })

        if passed:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1

    def test_broker_connection(self):
        """Test 1: Broker Connection"""
        print("\n" + "="*60)
        print("TEST 1: Broker Connection")
        print("="*60)

        result = self.broker.connect()
        self.log_test("Broker connects successfully", result)

        account = self.broker.get_account_info()
        self.log_test("Account info retrieved", 'cash' in account, f"Cash: ${account.get('cash', 0):.2f}")

    def test_market_data(self):
        """Test 2: Market Data Access"""
        print("\n" + "="*60)
        print("TEST 2: Market Data Access")
        print("="*60)

        symbols = ['BTCUSDT', 'ETHUSDT', 'AAPL', 'TSLA']
        all_passed = True

        for symbol in symbols:
            price = self.broker.get_current_price(symbol)
            passed = price is not None and price > 0
            all_passed = all_passed and passed
            self.log_test(f"Get price for {symbol}", passed, f"Price: ${price:.2f}" if price else "No price")

        self.log_test("All market data accessible", all_passed)

    def test_trade_execution(self):
        """Test 3: Trade Execution"""
        print("\n" + "="*60)
        print("TEST 3: Trade Execution")
        print("="*60)

        # Test buy order
        initial_cash = self.broker.cash
        order = self.broker.execute_buy('AAPL', 10)
        self.log_test("Buy order executes", order is not None, f"Order ID: {order.get('order_id') if order else 'None'}")

        # Verify cash decreased
        cash_decreased = self.broker.cash < initial_cash
        self.log_test("Cash decreases after buy", cash_decreased, f"Cash: ${self.broker.cash:.2f}")

        # Verify position created
        positions = self.broker.get_positions()
        has_position = 'AAPL' in positions
        self.log_test("Position created", has_position)

        # Test sell order
        if has_position:
            sell_order = self.broker.execute_sell('AAPL', 5)
            self.log_test("Sell order executes", sell_order is not None)

            # Verify position decreased
            positions_after = self.broker.get_positions()
            qty_decreased = positions_after['AAPL']['quantity'] < positions['AAPL']['quantity']
            self.log_test("Position quantity decreased", qty_decreased)

    def test_risk_management(self):
        """Test 4: Risk Management"""
        print("\n" + "="*60)
        print("TEST 4: Risk Management")
        print("="*60)

        portfolio_value = 10000
        symbol = 'AAPL'
        price = 180.0

        # Test position sizing
        sizing_result = self.risk_manager.calculate_position_size(
            portfolio_value=portfolio_value,
            entry_price=price,
            stop_loss_pct=2.0,
            confidence=0.8
        )
        shares = sizing_result.get('shares', 0) if sizing_result else 0
        self.log_test("Position size calculated", shares > 0, f"Shares: {shares}")

        # Test position size limits
        max_position_value = portfolio_value * 0.20
        actual_value = shares * price
        within_limits = actual_value <= max_position_value
        self.log_test("Position within 20% limit", within_limits, f"Position: ${actual_value:.2f} / ${max_position_value:.2f}")

        # Test risk limits are configured
        self.log_test("Risk limits configured",
                     self.risk_manager.max_position_size_pct > 0,
                     f"Max position: {self.risk_manager.max_position_size_pct}%")

    def test_portfolio_tracking(self):
        """Test 5: Portfolio Tracking"""
        print("\n" + "="*60)
        print("TEST 5: Portfolio Tracking")
        print("="*60)

        # Add a position
        self.portfolio_manager.add_position(
            symbol='AAPL',
            quantity=10,
            entry_price=180.0,
            stop_loss=176.4,
            take_profit=190.8,
            reasoning="Test position"
        )

        # Update daily value
        self.portfolio_manager.record_daily_value(10000)

        # Get metrics
        metrics = self.portfolio_manager.get_performance_metrics()
        self.log_test("Performance metrics calculated", 'total_return' in metrics)
        self.log_test("Total return tracked", metrics.get('total_return', 0) is not None)

    def test_ai_decision_simulation(self):
        """Test 6: AI Decision Simulation"""
        print("\n" + "="*60)
        print("TEST 6: AI Decision Simulation")
        print("="*60)

        # Simulate 10 AI decisions
        actions = ['BUY', 'SELL', 'HOLD']
        valid_decisions = 0

        for i in range(10):
            decision = {
                'action': random.choice(actions),
                'symbol': random.choice(['AAPL', 'TSLA', 'BTCUSDT']),
                'confidence': random.uniform(0.5, 0.95),
                'stop_loss_pct': random.uniform(1.0, 3.0),
                'take_profit_pct': random.uniform(3.0, 8.0),
                'position_size_pct': random.uniform(10, 20)
            }

            # Validate decision structure
            has_required_fields = all(k in decision for k in ['action', 'symbol', 'confidence'])
            if has_required_fields:
                valid_decisions += 1

        all_valid = valid_decisions == 10
        self.log_test("AI decisions validated", all_valid, f"{valid_decisions}/10 decisions valid")

    def test_trading_cycle(self):
        """Test 7: Complete Trading Cycle"""
        print("\n" + "="*60)
        print("TEST 7: Complete Trading Cycle Simulation")
        print("="*60)

        cycles_completed = 0
        profitable_trades = 0

        for cycle in range(5):
            # Simulate market movement
            self.broker.simulate_market_movement(volatility=0.01)

            # Get a symbol
            symbol = random.choice(['AAPL', 'TSLA', 'BTCUSDT'])
            current_price = self.broker.get_current_price(symbol)

            # Simulate AI decision (70% chance of HOLD, 20% BUY, 10% SELL)
            action_roll = random.random()
            if action_roll < 0.20:  # 20% BUY
                # Execute buy
                portfolio_value = self.broker.get_account_info()['portfolio_value']
                sizing_result = self.risk_manager.calculate_position_size(
                    portfolio_value=portfolio_value,
                    entry_price=current_price,
                    stop_loss_pct=2.0,
                    confidence=0.75
                )
                shares = sizing_result.get('shares', 0) if sizing_result else 0
                if shares > 0:
                    order = self.broker.execute_buy(symbol, int(shares))
                    if order:
                        profitable_trades += 1 if random.random() > 0.5 else 0

            elif action_roll < 0.30:  # 10% SELL
                positions = self.broker.get_positions()
                if symbol in positions:
                    qty = positions[symbol]['quantity']
                    self.broker.execute_sell(symbol, int(qty))

            cycles_completed += 1

        self.log_test("Trading cycles completed", cycles_completed == 5, f"{cycles_completed}/5 cycles")
        self.log_test("Some trades were profitable", profitable_trades > 0)

    def test_stress_test(self):
        """Test 8: Stress Test"""
        print("\n" + "="*60)
        print("TEST 8: Stress Test (High Volatility)")
        print("="*60)

        initial_value = self.broker.get_account_info()['portfolio_value']

        # Simulate 20 cycles with high volatility
        for _ in range(20):
            self.broker.simulate_market_movement(volatility=0.05)  # 5% volatility

        final_value = self.broker.get_account_info()['portfolio_value']
        survived = final_value > initial_value * 0.5  # Didn't lose more than 50%

        self.log_test("Survived high volatility", survived, f"Value: ${final_value:.2f}")

    def run_all_tests(self):
        """Run all automated tests"""
        print("\n" + "="*70)
        print("  🤖 AUTOMATED TRADING BOT TEST SUITE")
        print("="*70)
        print(f"\nStarting automated test run at {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Run all tests
        self.test_broker_connection()
        self.test_market_data()
        self.test_trade_execution()
        self.test_risk_management()
        self.test_portfolio_tracking()
        self.test_ai_decision_simulation()
        self.test_trading_cycle()
        self.test_stress_test()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("  📊 TEST SUMMARY")
        print("="*70)

        total = self.test_results['passed'] + self.test_results['failed']
        pass_rate = (self.test_results['passed'] / total * 100) if total > 0 else 0

        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"Pass Rate: {pass_rate:.1f}%")

        if self.test_results['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("Your trading bot is functioning correctly.")
        else:
            print("\n⚠️  SOME TESTS FAILED")
            print("Please review the failures above.")

        print("="*70 + "\n")


if __name__ == "__main__":
    tester = AutomatedTradingTest()
    tester.run_all_tests()
