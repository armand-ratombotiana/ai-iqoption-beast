# How to Set Claude API Key

## ✅ Your Setup is Already Configured!

The Claude API key has been successfully added to your `.env` file and the system is loading it correctly.

### Current Status:
- ✅ `.env` file exists
- ✅ Claude API key is loaded
- ✅ System configured to use Claude
- ⚠️ **Claude API credits are low/exhausted**

## The Error You're Seeing

```
400 Bad Request: Your credit balance is too low to access the Anthropic API
```

This means:
- Your API key is **valid** ✅
- It's **properly configured** ✅
- But needs **credits added** to work

## How to Add Credits

1. Go to: https://console.anthropic.com/settings/billing
2. Add credits or upgrade your plan
3. Once credits are added, the system will work automatically!

## Your Current Configuration

File: `.env`
```env
IQOPTION_EMAIL=tombokael4@gmail.com
IQOPTION_PASSWORD=tombokael04
ACCOUNT_TYPE=demo

# Claude API (configured, needs credits)
ANTHROPIC_API_KEY=sk-ant-api03-hsqwDif...
USE_CLAUDE=true
CLAUDE_MODEL=claude-3-5-haiku-20241022
CLAUDE_WEIGHT=1.0
```

## Testing Without Claude (Until Credits Added)

You can still test the system without Claude AI:

### Option 1: Use Lower Confidence Threshold
```bash
# Run with lower confidence requirement (no AI needed)
MIN_CONFIDENCE=45 python run_trading_system.py --mode basic --demo
```

### Option 2: Disable Claude Temporarily
Edit `.env`:
```env
USE_CLAUDE=false
```

Then run normally:
```bash
python run_trading_system.py --mode basic --demo
```

## Alternative: Use OpenAI Instead

If you have OpenAI credits, you can use that instead:

1. Get API key from: https://platform.openai.com/api-keys
2. Add to `.env`:
   ```env
   OPENAI_API_KEY=sk-...
   USE_OPENAI=true
   USE_CLAUDE=false
   ```

## Verify Your Setup

Check if Claude key is loaded:
```bash
python -c "
import sys
sys.path.insert(0, '.')
from ai_models.claude_model import ClaudeModel
model = ClaudeModel()
print('Claude API Key:', 'Loaded ✅' if model.api_key else 'Not loaded ❌')
print('Key starts with:', model.api_key[:20] if model.api_key else 'N/A')
"
```

## Summary

**Everything is set up correctly!** 

The only thing needed is:
1. Add credits to your Claude account at https://console.anthropic.com/settings/billing
2. Or use a different AI provider (OpenAI, DeepSeek)
3. Or run with lower confidence threshold to test without AI

Your configuration files are all correct and the system will work as soon as credits are available.

## Quick Commands Reference

**Run without AI (testing):**
```bash
MIN_CONFIDENCE=45 python run_trading_system.py --mode basic --demo
```

**Run with OpenAI (if you have credits):**
```bash
# Add to .env first: OPENAI_API_KEY=sk-...
USE_OPENAI=true USE_CLAUDE=false python run_trading_system.py --mode basic --demo
```

**Check configuration:**
```bash
python -c "from config.settings import TradingConfig; print('Email:', TradingConfig.EMAIL)"
```
