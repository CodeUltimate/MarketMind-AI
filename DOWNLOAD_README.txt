==========================================
🤖 AI TRADING BOT - DOWNLOAD INSTRUCTIONS
==========================================

You have THREE download options:

OPTION 1: Download ZIP Archive (Recommended for Windows)
--------------------------------------------------------
File: ai-trading-bot.zip (76 KB)

After download:
1. Extract the ZIP file
2. Open terminal/command prompt in extracted folder
3. Continue with setup:
   - Copy .env.example to .env
   - Add your API keys to .env
   - Run: pip install -r requirements.txt
   - Run: python test_system.py
   - Run: python main.py


OPTION 2: Download TAR.GZ Archive (Recommended for Mac/Linux)
--------------------------------------------------------------
File: ai-trading-bot.tar.gz (33 KB)

After download:
1. Extract: tar -xzf ai-trading-bot.tar.gz
2. cd ai-trading-bot
3. Continue with setup (same as above)


OPTION 3: Download Folder Directly
-----------------------------------
Folder: ai-trading-bot/

Download the entire folder and follow setup instructions.


QUICK START AFTER EXTRACTION:
------------------------------

1. Get API Keys:
   - Alpaca: https://alpaca.markets (FREE paper trading)
   - DeepSeek: https://platform.deepseek.com (~$5)
   - News API (optional): https://newsapi.org (FREE)

2. Configure:
   cp .env.example .env
   # Edit .env with your API keys

3. Install:
   pip install -r requirements.txt

4. Test:
   python test_system.py

5. Run:
   python main.py


DOCUMENTATION:
--------------
- README.md - Main overview
- docs/SETUP_GUIDE.md - Detailed setup
- docs/ARCHITECTURE.md - How it works
- docs/QUICK_REFERENCE.md - Command reference
- PROJECT_SUMMARY.md - Your roadmap


NEED HELP?
----------
Check the documentation files above or review the logs:
tail -f logs/trading_bot.log


⚠️  IMPORTANT:
- Start with PAPER TRADING only
- Never use real money until 6+ months of testing
- Monitor the bot closely at first
- Review AI decisions and reasoning


Good luck! 🚀
