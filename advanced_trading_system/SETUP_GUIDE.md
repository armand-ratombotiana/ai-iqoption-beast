# Trading System Setup Guide

## Setting Up Claude API Key

### Method 1: Using .env File (Recommended)

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file:**
   ```bash
   nano .env
   # or use your preferred editor
   ```

3. **Add your Claude API key:**
   ```bash
   # Get your key from: https://console.anthropic.com/
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   
   # Add your IQOption credentials
   IQOPTION_EMAIL=your_email@example.com
   IQOPTION_PASSWORD=your_password
   ```

4. **Run the system:**
   ```bash
   python run_trading_system.py --mode basic --demo
   ```
   
   The system will automatically load the .env file!

### Method 2: Environment Variables (One-time)

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-your-actual-key-here"
export IQOPTION_EMAIL="your_email@example.com"
export IQOPTION_PASSWORD="your_password"

python run_trading_system.py --mode basic --demo
```

### Method 3: Inline (One-time)

```bash
ANTHROPIC_API_KEY="sk-ant-api03-your-key" \
IQOPTION_EMAIL="your_email@example.com" \
IQOPTION_PASSWORD="your_password" \
python run_trading_system.py --mode basic --demo
```

### Method 4: Persistent (Add to Shell Profile)

Add to `~/.bashrc` or `~/.zshrc`:
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-your-actual-key-here"
export IQOPTION_EMAIL="your_email@example.com"
export IQOPTION_PASSWORD="your_password"
```

Then reload:
```bash
source ~/.bashrc
```

## Getting API Keys

### Claude (Anthropic)
1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-api03-`)

### OpenAI (Optional)
1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `sk-`)

### DeepSeek (Optional)
1. Go to: https://platform.deepseek.com/
2. Sign up or log in
3. Create a new API key
4. Copy the key

## Complete Setup Example

### Using .env file:

1. **Create .env file:**
   ```bash
   cd /app/app/KAEL/KAEL/advanced_trading_system
   cp .env.example .env
   nano .env
   ```

2. **Add your credentials:**
   ```env
   # IQOption Account
   IQOPTION_EMAIL=tombokael4@gmail.com
   IQOPTION_PASSWORD=your_password
   ACCOUNT_TYPE=demo
   
   # Claude API
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key
   
   # Optional: Other AI models
   OPENAI_API_KEY=sk-your-openai-key
   DEEPSEEK_API_KEY=sk-your-deepseek-key
   
   # Which models to use
   USE_OPENAI=false
   USE_CLAUDE=true
   USE_DEEPSEEK=false
   ```

3. **Run the system:**
   ```bash
   # Basic mode with single pair
   python run_trading_system.py --mode basic --demo
   
   # Enhanced mode with multiple AI models
   python run_trading_system.py --mode enhanced --demo
   
   # Parallel mode trading multiple pairs
   python run_trading_system.py --mode parallel --demo --duration 30
   ```

## Verification

Check if your API key is loaded:

```bash
python -c "
import sys
sys.path.insert(0, '.')
from config.settings import TradingConfig
from ai_models.claude_model import ClaudeModel

print('Claude API Key:', 'SET ✅' if ClaudeModel().api_key else 'NOT SET ❌')
"
```

## Quick Test

Test Claude integration:

```bash
python << 'EOF'
import sys
sys.path.insert(0, '.')
from ai_models.claude_model import ClaudeModel

# Initialize model
model = ClaudeModel()

# Test market data
test_data = {
    'current_price': 1.17,
    'rsi_14': 65,
    'trend': 'uptrend',
    'volatility': 'low'
}

# Get prediction
result = model.predict(test_data)
print(f"Signal: {result['signal']}")
print(f"Confidence: {result['confidence']}%")
print(f"Reasoning: {result['reasoning']}")
