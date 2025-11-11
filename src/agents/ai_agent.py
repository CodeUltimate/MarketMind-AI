"""
AI Agent Module
Interfaces with AI models (DeepSeek, GPT, Claude) for trading decisions
"""
import json
from typing import Dict, List, Optional
from openai import OpenAI
from ..utils.logger import logger
from config.config import Config

class AITradingAgent:
    """AI agent that makes trading decisions"""
    
    def __init__(self, model: str = None, api_key: str = None):
        self.model = model or Config.AI_MODEL
        self.api_key = api_key or Config.DEEPSEEK_API_KEY
        
        # Initialize OpenAI client (DeepSeek API is OpenAI-compatible)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"  # DeepSeek endpoint
        )
        
    def get_trading_decision(self, market_data: Dict, portfolio_state: Dict) -> Dict:
        """
        Get trading decision from AI based on market data and portfolio state
        
        Returns:
            {
                'action': 'BUY' | 'SELL' | 'HOLD',
                'symbol': str,
                'confidence': float (0-1),
                'reasoning': str,
                'stop_loss': float,
                'take_profit': float,
                'position_size': float (% of portfolio)
            }
        """
        try:
            prompt = self._build_trading_prompt(market_data, portfolio_state)
            
            logger.info("Querying AI for trading decision...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=Config.AI_TEMPERATURE,
                max_tokens=Config.AI_MAX_TOKENS
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            logger.info(f"AI Response received: {ai_response[:200]}...")
            
            # Parse the structured response
            decision = self._parse_ai_response(ai_response)
            
            return decision
            
        except Exception as e:
            logger.error(f"Error getting AI decision: {e}")
            return self._default_decision()
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI"""
        return """You are an expert quantitative trader and portfolio manager with 20 years of experience.
You analyze market data, technical indicators, news, and sentiment to make informed trading decisions.

Your goals:
1. Preserve capital (risk management is paramount)
2. Generate consistent returns
3. Follow disciplined entry/exit rules
4. Adapt to market regimes

Always respond in this EXACT JSON format (no extra text):
{
    "action": "BUY" or "SELL" or "HOLD",
    "symbol": "SYMBOL",
    "confidence": 0.0-1.0,
    "reasoning": "Your detailed reasoning here",
    "stop_loss_pct": 2.0,
    "take_profit_pct": 6.0,
    "position_size_pct": 10.0
}

Key principles:
- Only trade when you have high confidence (>0.7)
- Always set stop losses (typically 2-3%)
- Target 2:1 or better risk/reward
- Consider market regime
- Don't chase momentum blindly
- Watch for divergences between price and indicators
"""
    
    def _build_trading_prompt(self, market_data: Dict, portfolio_state: Dict) -> str:
        """Build detailed prompt with market context"""
        
        # Extract data
        symbols = market_data.get('symbols', [])
        sentiment = market_data.get('sentiment', {})
        news = market_data.get('news', [])
        
        prompt = f"""
📊 CURRENT MARKET ANALYSIS REQUEST

Portfolio State:
- Cash Available: ${portfolio_state.get('cash', 0):.2f}
- Positions: {len(portfolio_state.get('positions', []))}
- Total Value: ${portfolio_state.get('total_value', 0):.2f}
- Today's P&L: {portfolio_state.get('daily_pnl', 0):.2f}%

Market Regime: {sentiment.get('Market_Regime', 'Unknown')}
VIX Level: {sentiment.get('VIX', 'N/A')}
SPY vs 200 SMA: {sentiment.get('SPY_vs_SMA200', 'N/A')}

"""
        
        # Add symbol analysis
        for symbol_data in symbols:
            symbol = symbol_data.get('symbol')
            indicators = symbol_data.get('indicators', {})
            
            prompt += f"""
Symbol: {symbol}
Current Price: ${indicators.get('Current_Price', 0):.2f}
Price Change (1D): {indicators.get('Price_Change_1D', 0):.2f}%
Price Change (5D): {indicators.get('Price_Change_5D', 0):.2f}%

Technical Indicators:
- RSI: {indicators.get('RSI', 0):.1f}
- MACD: {indicators.get('MACD', 0):.3f}
- MACD Signal: {indicators.get('MACD_Signal', 0):.3f}
- SMA 20: ${indicators.get('SMA_20', 0):.2f}
- SMA 50: ${indicators.get('SMA_50', 0):.2f}
- Bollinger Bands: ${indicators.get('BB_Low', 0):.2f} - ${indicators.get('BB_High', 0):.2f}

"""
        
        # Add news if available
        if news:
            prompt += "\nRecent News Headlines:\n"
            for article in news[:3]:
                prompt += f"- {article.get('title', '')}\n"
        
        prompt += """
Based on this analysis, what is your trading decision?
Respond ONLY with the JSON format specified in your system instructions.
"""
        
        return prompt
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response into structured decision"""
        try:
            # Try to extract JSON from response
            # Sometimes AI adds text before/after JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = response[start:end]
                decision = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['action', 'symbol', 'confidence', 'reasoning']
                if all(field in decision for field in required_fields):
                    return decision
            
            logger.error(f"Could not parse AI response as JSON: {response}")
            return self._default_decision()
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return self._default_decision()
    
    def _default_decision(self) -> Dict:
        """Return default HOLD decision on error"""
        return {
            'action': 'HOLD',
            'symbol': None,
            'confidence': 0.0,
            'reasoning': 'Error in AI processing, defaulting to HOLD',
            'stop_loss_pct': 0,
            'take_profit_pct': 0,
            'position_size_pct': 0
        }
    
    def validate_decision(self, decision: Dict, risk_limits: Dict) -> tuple[bool, str]:
        """
        Validate AI decision against risk limits
        
        Returns:
            (is_valid, reason)
        """
        action = decision.get('action')
        confidence = decision.get('confidence', 0)
        position_size = decision.get('position_size_pct', 0)
        
        # Check confidence threshold
        if action in ['BUY', 'SELL'] and confidence < 0.7:
            return False, f"Confidence too low: {confidence:.2f} < 0.70"
        
        # Check position size limits
        max_position = risk_limits.get('max_position_size_pct', 20)
        if position_size > max_position:
            return False, f"Position size {position_size}% exceeds limit {max_position}%"
        
        # Check stop loss is set
        if action == 'BUY' and decision.get('stop_loss_pct', 0) <= 0:
            return False, "Stop loss not set for BUY order"
        
        return True, "Decision validated"
