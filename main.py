"""
Main Trading Bot
Orchestrates all components: data collection, AI decisions, risk management, execution
"""
import time
from datetime import datetime
from typing import Dict, List
from config.config import Config
from src.utils.logger import TradingLogger
from src.collectors.data_collector import MarketDataCollector, NewsCollector
from src.agents.ai_agent import AITradingAgent
from src.risk.risk_manager import RiskManager
from src.portfolio.portfolio_manager import PortfolioManager
from src.brokers.broker_factory import BrokerFactory

class AITradingBot:
    """Main trading bot that coordinates all components"""
    
    def __init__(self):
        # Initialize logger
        self.logger_instance = TradingLogger(log_file=Config.LOG_FILE)
        self.logger = self.logger_instance.get_logger()
        
        self.logger.info("="*80)
        self.logger.info("🤖 AI TRADING BOT STARTING UP")
        self.logger.info("="*80)
        
        # Initialize components
        self.logger.info("Initializing components...")
        
        # Watchlist of symbols to trade
        self.watchlist = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMD']
        
        self.data_collector = MarketDataCollector(symbols=self.watchlist)
        self.news_collector = NewsCollector(api_key=Config.NEWS_API_KEY)
        self.ai_agent = AITradingAgent()
        self.risk_manager = RiskManager()
        self.portfolio_manager = PortfolioManager(initial_capital=Config.INITIAL_CAPITAL)

        # Initialize broker using factory pattern
        # Select the correct API keys based on broker
        if Config.BROKER == 'alpaca':
            api_key = Config.ALPACA_API_KEY
            secret_key = Config.ALPACA_SECRET_KEY
        elif Config.BROKER == 'binance':
            api_key = Config.BINANCE_API_KEY
            secret_key = Config.BINANCE_SECRET_KEY
        else:
            raise ValueError(f"Unsupported broker: {Config.BROKER}")

        self.broker = BrokerFactory.create(
            broker_name=Config.BROKER,
            api_key=api_key,
            secret_key=secret_key,
            paper=(Config.TRADING_MODE == 'paper')
        )
        
        self.logger.info("✅ All components initialized successfully")
        self.logger.info(f"Trading Mode: {Config.TRADING_MODE.upper()}")
        self.logger.info(f"Initial Capital: ${Config.INITIAL_CAPITAL:.2f}")
        self.logger.info(f"Trading Interval: {Config.TRADING_INTERVAL_MINUTES} minutes")
        
    def collect_market_data(self) -> Dict:
        """Collect all market data for analysis"""
        self.logger.info("📊 Collecting market data...")
        
        market_data = {
            'timestamp': datetime.now().isoformat(),
            'symbols': [],
            'sentiment': {},
            'news': []
        }
        
        # Get market sentiment
        market_data['sentiment'] = self.data_collector.get_market_sentiment()
        
        # Get data for each symbol in watchlist
        for symbol in self.watchlist:
            indicators = self.data_collector.calculate_indicators(symbol)
            if indicators:
                market_data['symbols'].append({
                    'symbol': symbol,
                    'indicators': indicators
                })
        
        # Get recent news
        market_data['news'] = self.news_collector.get_market_news(max_articles=5)
        
        self.logger.info(f"✅ Data collected for {len(market_data['symbols'])} symbols")
        self.logger.info(f"   Market Regime: {market_data['sentiment'].get('Market_Regime', 'Unknown')}")
        self.logger.info(f"   VIX Level: {market_data['sentiment'].get('VIX', 'N/A')}")
        
        return market_data
    
    def get_portfolio_state(self) -> Dict:
        """Get current portfolio state"""
        # Get current prices
        prices = self.data_collector.get_current_prices()
        
        # Get portfolio state
        state = self.portfolio_manager.get_portfolio_state(prices)
        
        return state
    
    def check_stop_losses_and_targets(self):
        """Check if any positions hit stop loss or take profit"""
        self.logger.info("🎯 Checking stop losses and take profit targets...")
        
        prices = self.data_collector.get_current_prices()
        positions = self.portfolio_manager.state['positions']
        
        for symbol, position in list(positions.items()):
            if symbol not in prices:
                continue
            
            current_price = prices[symbol]
            
            # Check stop loss
            if self.risk_manager.check_stop_loss_hit(position, current_price):
                self.logger.warning(f"🛑 STOP LOSS HIT for {symbol} at ${current_price:.2f}")
                self.execute_sell(symbol, position['quantity'], "Stop loss triggered")
            
            # Check take profit
            elif self.risk_manager.check_take_profit_hit(position, current_price):
                self.logger.info(f"🎯 TAKE PROFIT HIT for {symbol} at ${current_price:.2f}")
                self.execute_sell(symbol, position['quantity'], "Take profit target reached")
    
    def execute_buy(self, symbol: str, quantity: int, price: float, 
                    stop_loss: float, take_profit: float, reasoning: str):
        """Execute a buy trade"""
        try:
            # Execute order through broker
            order = self.broker.execute_buy(symbol, quantity)
            
            if order:
                # Update portfolio
                self.portfolio_manager.add_position(
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    reasoning=reasoning
                )
                
                # Log the trade
                self.logger_instance.log_trade(
                    action='BUY',
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    reasoning=reasoning
                )
                
                return True
        except Exception as e:
            self.logger.error(f"Error executing BUY: {e}")
        
        return False
    
    def execute_sell(self, symbol: str, quantity: int, reasoning: str):
        """Execute a sell trade"""
        try:
            # Get current price
            current_price = self.broker.get_current_price(symbol)
            if not current_price:
                self.logger.error(f"Could not get price for {symbol}")
                return False
            
            # Execute order through broker
            order = self.broker.execute_sell(symbol, quantity)
            
            if order:
                # Update portfolio
                result = self.portfolio_manager.close_position(
                    symbol=symbol,
                    exit_price=current_price,
                    reasoning=reasoning
                )
                
                # Log the trade
                self.logger_instance.log_trade(
                    action='SELL',
                    symbol=symbol,
                    quantity=quantity,
                    price=current_price,
                    reasoning=f"{reasoning} | P&L: ${result['pnl']:.2f} ({result['pnl_pct']:+.2f}%)"
                )
                
                return True
        except Exception as e:
            self.logger.error(f"Error executing SELL: {e}")
        
        return False
    
    def run_trading_cycle(self):
        """Execute one complete trading cycle"""
        self.logger.info("\n" + "="*80)
        self.logger.info(f"🔄 STARTING TRADING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*80)
        
        try:
            # Step 1: Check existing positions for stop losses
            self.check_stop_losses_and_targets()
            
            # Step 2: Get portfolio state
            portfolio_state = self.get_portfolio_state()
            self.logger.info(f"\n💼 Portfolio Status:")
            self.logger.info(f"   Cash: ${portfolio_state['cash']:.2f}")
            self.logger.info(f"   Positions: {portfolio_state['num_positions']}")
            self.logger.info(f"   Total Value: ${portfolio_state['total_value']:.2f}")
            self.logger.info(f"   Total Return: ${portfolio_state['total_return']:.2f} ({portfolio_state['total_return_pct']:+.2f}%)")
            self.logger.info(f"   Daily P&L: ${portfolio_state['daily_pnl']:.2f} ({portfolio_state['daily_pnl_pct']:+.2f}%)")
            
            # Step 3: Check risk circuit breakers
            should_halt, reason = self.risk_manager.check_circuit_breakers(
                portfolio_state['total_value'],
                portfolio_state['daily_pnl_pct']
            )
            
            if should_halt:
                self.logger.warning(f"\n🚨 TRADING HALTED: {reason}")
                return
            
            # Step 4: Collect market data
            market_data = self.collect_market_data()
            
            # Step 5: Get AI decision
            self.logger.info("\n🤖 Requesting AI trading decision...")
            decision = self.ai_agent.get_trading_decision(market_data, portfolio_state)
            
            self.logger_instance.log_decision(
                decision_type=decision['action'],
                data=f"Symbol: {decision.get('symbol', 'N/A')}\n"
                     f"Confidence: {decision.get('confidence', 0):.2f}\n"
                     f"Reasoning: {decision.get('reasoning', 'N/A')}"
            )
            
            # Step 6: Validate and execute decision
            if decision['action'] == 'HOLD':
                self.logger.info("✋ AI Decision: HOLD - No action taken")
                
            elif decision['action'] == 'BUY':
                symbol = decision['symbol']
                confidence = decision.get('confidence', 0)
                
                # Validate decision
                is_valid, msg = self.ai_agent.validate_decision(
                    decision,
                    {'max_position_size_pct': Config.MAX_POSITION_SIZE_PCT}
                )
                
                if not is_valid:
                    self.logger.warning(f"❌ AI decision rejected: {msg}")
                    return
                
                # Get current price
                current_price = self.broker.get_current_price(symbol)
                if not current_price:
                    self.logger.error(f"Could not get price for {symbol}")
                    return
                
                # Calculate position size
                position_size = self.risk_manager.calculate_position_size(
                    portfolio_value=portfolio_state['total_value'],
                    entry_price=current_price,
                    stop_loss_pct=decision.get('stop_loss_pct', 2),
                    confidence=confidence,
                    ai_suggested_size_pct=decision.get('position_size_pct')
                )
                
                # Validate trade
                is_valid, msg = self.risk_manager.validate_trade(
                    action='BUY',
                    symbol=symbol,
                    shares=position_size['shares'],
                    price=current_price,
                    portfolio_value=portfolio_state['total_value'],
                    current_positions=self.portfolio_manager.state['positions']
                )
                
                if not is_valid:
                    self.logger.warning(f"❌ Trade rejected: {msg}")
                    return
                
                # Calculate stop loss and take profit
                stop_loss = self.risk_manager.calculate_stop_loss(
                    current_price,
                    decision.get('stop_loss_pct', 2)
                )
                take_profit = self.risk_manager.calculate_take_profit(
                    current_price,
                    decision.get('take_profit_pct', 6)
                )
                
                self.logger.info(f"\n📈 Executing BUY:")
                self.logger.info(f"   Symbol: {symbol}")
                self.logger.info(f"   Shares: {position_size['shares']}")
                self.logger.info(f"   Price: ${current_price:.2f}")
                self.logger.info(f"   Position Size: {position_size['position_size_pct']:.1f}%")
                self.logger.info(f"   Stop Loss: ${stop_loss:.2f}")
                self.logger.info(f"   Take Profit: ${take_profit:.2f}")
                
                # Execute the buy
                self.execute_buy(
                    symbol=symbol,
                    quantity=position_size['shares'],
                    price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    reasoning=decision['reasoning']
                )
            
            elif decision['action'] == 'SELL':
                symbol = decision['symbol']
                
                # Check if we have the position
                if symbol not in self.portfolio_manager.state['positions']:
                    self.logger.warning(f"❌ Cannot sell {symbol}: no position")
                    return
                
                position = self.portfolio_manager.state['positions'][symbol]
                
                self.logger.info(f"\n📉 Executing SELL:")
                self.logger.info(f"   Symbol: {symbol}")
                self.logger.info(f"   Shares: {position['quantity']}")
                
                # Execute the sell
                self.execute_sell(
                    symbol=symbol,
                    quantity=position['quantity'],
                    reasoning=decision['reasoning']
                )
            
            # Step 7: Record daily value
            self.portfolio_manager.record_daily_value(portfolio_state['total_value'])
            
            # Step 8: Log performance metrics
            risk_metrics = self.risk_manager.get_risk_metrics(portfolio_state['total_value'])
            perf_metrics = self.portfolio_manager.get_performance_metrics()
            
            self.logger.info(f"\n📊 Risk Metrics:")
            self.logger.info(f"   Daily P&L: {risk_metrics['daily_pnl_pct']:.2f}% (Limit: {risk_metrics['daily_loss_limit_pct']:.2f}%)")
            self.logger.info(f"   Drawdown: {risk_metrics['current_drawdown_pct']:.2f}% (Max: {risk_metrics['max_drawdown_pct']:.2f}%)")
            
            if perf_metrics.get('closed_trades', 0) > 0:
                self.logger.info(f"\n📈 Performance Metrics:")
                self.logger.info(f"   Win Rate: {perf_metrics['win_rate']*100:.1f}%")
                self.logger.info(f"   Profit Factor: {perf_metrics['profit_factor']:.2f}")
                self.logger.info(f"   Total P&L: ${perf_metrics['total_pnl']:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error in trading cycle: {e}", exc_info=True)
        
        self.logger.info("\n" + "="*80)
        self.logger.info("✅ TRADING CYCLE COMPLETE")
        self.logger.info("="*80 + "\n")
    
    def run(self, interval_minutes: int = None):
        """Run the trading bot continuously"""
        interval = interval_minutes or Config.TRADING_INTERVAL_MINUTES
        
        self.logger.info(f"🚀 Bot running with {interval} minute intervals")
        self.logger.info("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_trading_cycle()
                
                # Wait for next cycle
                self.logger.info(f"⏰ Waiting {interval} minutes until next cycle...\n")
                time.sleep(interval * 60)
                
        except KeyboardInterrupt:
            self.logger.info("\n\n🛑 Bot stopped by user")
            self.logger.info("="*80)
            
            # Final portfolio summary
            portfolio_state = self.get_portfolio_state()
            perf_metrics = self.portfolio_manager.get_performance_metrics()
            
            self.logger_instance.log_performance({
                'Final Portfolio Value': f"${portfolio_state['total_value']:.2f}",
                'Total Return': f"${portfolio_state['total_return']:.2f} ({portfolio_state['total_return_pct']:+.2f}%)",
                'Total Trades': perf_metrics.get('total_trades', 0),
                'Closed Trades': perf_metrics.get('closed_trades', 0),
                'Win Rate': f"{perf_metrics.get('win_rate', 0)*100:.1f}%",
                'Profit Factor': f"{perf_metrics.get('profit_factor', 0):.2f}"
            })

if __name__ == '__main__':
    bot = AITradingBot()
    bot.run()
