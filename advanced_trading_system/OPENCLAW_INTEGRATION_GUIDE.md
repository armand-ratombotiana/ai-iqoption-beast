# OpenClaw Integration Guide - Open-Source AI Models

**Date**: February 2026  
**Status**: ✅ Complete  
**Integration**: KAEL Trading System

---

## 🎯 What is OpenClaw?

**OpenClaw** is our integration layer for **open-source Large Language Models (LLMs)** that provides:
- ✅ **Multiple Backend Support** - Ollama, HuggingFace, LM Studio, LocalAI, OpenRouter
- ✅ **Local & Cloud Options** - Run models locally or use cloud APIs
- ✅ **Free & Paid Models** - From completely free to premium options
- ✅ **Automatic Fallbacks** - Robust error handling and parsing
- ✅ **Easy Integration** - Drop-in replacement for Claude/GPT

---

## 🚀 Supported Backends

### 1. **Ollama** (Recommended for Local)
**Best for**: Privacy, no API costs, full control

- **Setup**: Install Ollama locally
- **Cost**: FREE
- **Privacy**: 100% local, no data sent externally
- **Speed**: Fast (depends on hardware)
- **Models**: 50+ open-source models

### 2. **HuggingFace Inference API**
**Best for**: Quick start, no local setup

- **Setup**: Get free API key
- **Cost**: FREE tier available
- **Privacy**: Data sent to HuggingFace
- **Speed**: Medium (API latency)
- **Models**: 1000+ models available

### 3. **LM Studio**
**Best for**: User-friendly local setup

- **Setup**: Install LM Studio app
- **Cost**: FREE
- **Privacy**: 100% local
- **Speed**: Fast (depends on hardware)
- **Models**: Easy model management

### 4. **LocalAI**
**Best for**: Self-hosted production

- **Setup**: Docker container
- **Cost**: FREE
- **Privacy**: 100% local
- **Speed**: Fast (optimized)
- **Models**: OpenAI-compatible API

### 5. **OpenRouter**
**Best for**: Access to many models via one API

- **Setup**: Get API key
- **Cost**: Pay-per-use (some free models)
- **Privacy**: Data sent to OpenRouter
- **Speed**: Fast (optimized routing)
- **Models**: 100+ models from various providers

---

## 📦 Installation & Setup

### Option 1: Ollama (Recommended)

#### Step 1: Install Ollama
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

#### Step 2: Pull a Model
```bash
# Recommended: Llama 3.2 (3B parameters, fast)
ollama pull llama3.2

# Or other models:
ollama pull mistral        # Mistral 7B
ollama pull phi3           # Microsoft Phi-3
ollama pull gemma2         # Google Gemma 2
ollama pull qwen2.5        # Qwen 2.5
```

#### Step 3: Start Ollama Server
```bash
# Ollama runs automatically after installation
# Check if running:
ollama list

# Or start manually:
ollama serve
```

#### Step 4: Configure KAEL
```python
# In your .env file
USE_OPENCLAW=true
OPENCLAW_BACKEND=ollama
OPENCLAW_MODEL=llama3.2
```

### Option 2: HuggingFace

#### Step 1: Get API Key
1. Go to https://huggingface.co/
2. Sign up (free)
3. Go to Settings → Access Tokens
4. Create new token

#### Step 2: Configure KAEL
```bash
# In your .env file
USE_OPENCLAW=true
OPENCLAW_BACKEND=huggingface
OPENCLAW_MODEL=meta-llama/Llama-3.2-3B-Instruct
HUGGINGFACE_API_KEY=hf_your_api_key_here
```

### Option 3: LM Studio

#### Step 1: Install LM Studio
1. Download from https://lmstudio.ai/
2. Install and launch
3. Download a model (e.g., Llama 3.2)

#### Step 2: Start Local Server
1. In LM Studio, go to "Local Server" tab
2. Click "Start Server"
3. Note the port (default: 1234)

#### Step 3: Configure KAEL
```bash
# In your .env file
USE_OPENCLAW=true
OPENCLAW_BACKEND=lmstudio
OPENCLAW_MODEL=llama-3.2-3b-instruct
LMSTUDIO_URL=http://localhost:1234/v1/chat/completions
```

### Option 4: OpenRouter

#### Step 1: Get API Key
1. Go to https://openrouter.ai/
2. Sign up
3. Get API key from dashboard

#### Step 2: Configure KAEL
```bash
# In your .env file
USE_OPENCLAW=true
OPENCLAW_BACKEND=openrouter
OPENCLAW_MODEL=meta-llama/llama-3.2-3b-instruct:free
OPENROUTER_API_KEY=sk-or-your_api_key_here
```

---

## 💻 Usage Examples

### Basic Usage

```python
from ai.models.openclaw_model import OpenClawModel

# Create model
model = OpenClawModel(
    backend="ollama",
    model_name="llama3.2"
)

# Get trading signal
market_data = {
    'pair': 'EURUSD',
    'current_price': 1.0850,
    'rsi_14': 35,
    'trend': 'downtrend',
    'macd': {'histogram': -0.002}
}

prediction = model.predict(market_data)
print(f"Signal: {prediction['signal']}")
print(f"Confidence: {prediction['confidence']}%")
print(f"Reasoning: {prediction['reasoning']}")
```

### With Consensus Engine

```python
from ai.models.openclaw_model import OpenClawModel
from ai.models.consensus_engine import AIConsensusEngine

# Create consensus engine
consensus = AIConsensusEngine(consensus_threshold=0.66)

# Add multiple OpenClaw models
model1 = OpenClawModel(backend="ollama", model_name="llama3.2")
model2 = OpenClawModel(backend="ollama", model_name="mistral")
model3 = OpenClawModel(backend="ollama", model_name="phi3")

consensus.add_model(model1, weight=1.0)
consensus.add_model(model2, weight=1.0)
consensus.add_model(model3, weight=1.0)

# Get consensus signal
result = consensus.get_consensus_signal(market_data)
print(f"Consensus: {result['signal']} ({result['confidence']}%)")
print(f"Agreement: {result['agreement']}%")
```

### List Available Models

```python
from ai.models.openclaw_model import OpenClawModel

# List all available models
models = OpenClawModel.list_available_models()

for backend, model_list in models.items():
    print(f"\n{backend.upper()}:")
    for model in model_list:
        print(f"  - {model}")

# Get recommended model for backend
recommended = OpenClawModel.get_recommended_model("ollama")
print(f"\nRecommended for Ollama: {recommended}")
```

---

## 🎨 Recommended Models

### For Speed (Fast inference)
```python
# Ollama
OpenClawModel(backend="ollama", model_name="phi3")           # 3.8B params
OpenClawModel(backend="ollama", model_name="llama3.2")       # 3B params
OpenClawModel(backend="ollama", model_name="gemma2:2b")      # 2B params

# OpenRouter (Free)
OpenClawModel(
    backend="openrouter",
    model_name="meta-llama/llama-3.2-3b-instruct:free"
)
```

### For Accuracy (Better predictions)
```python
# Ollama
OpenClawModel(backend="ollama", model_name="llama3.1:8b")    # 8B params
OpenClawModel(backend="ollama", model_name="mistral")        # 7B params
OpenClawModel(backend="ollama", model_name="mixtral")        # 8x7B params

# OpenRouter (Paid but cheap)
OpenClawModel(
    backend="openrouter",
    model_name="meta-llama/llama-3.1-8b-instruct"
)
```

### For Balance (Speed + Accuracy)
```python
# Ollama (Recommended)
OpenClawModel(backend="ollama", model_name="llama3.2")       # Best overall
OpenClawModel(backend="ollama", model_name="qwen2.5:7b")     # Great alternative

# HuggingFace (Free API)
OpenClawModel(
    backend="huggingface",
    model_name="meta-llama/Llama-3.2-3B-Instruct"
)
```

---

## ⚙️ Configuration Options

### Environment Variables

```bash
# Backend selection
USE_OPENCLAW=true
OPENCLAW_BACKEND=ollama  # ollama, huggingface, lmstudio, localai, openrouter

# Model selection
OPENCLAW_MODEL=llama3.2

# API Keys (if needed)
HUGGINGFACE_API_KEY=hf_...
OPENROUTER_API_KEY=sk-or-...
OPENCLAW_API_KEY=...  # Generic fallback

# Custom URLs (for local servers)
OLLAMA_URL=http://localhost:11434
LMSTUDIO_URL=http://localhost:1234/v1/chat/completions
LOCALAI_URL=http://localhost:8080/v1/chat/completions
```

### Python Configuration

```python
# config/settings.py

class TradingConfig:
    # OpenClaw settings
    USE_OPENCLAW = os.getenv('USE_OPENCLAW', 'true').lower() == 'true'
    OPENCLAW_BACKEND = os.getenv('OPENCLAW_BACKEND', 'ollama')
    OPENCLAW_MODEL = os.getenv('OPENCLAW_MODEL', 'llama3.2')
    OPENCLAW_WEIGHT = float(os.getenv('OPENCLAW_WEIGHT', '1.5'))
```

---

## 🔧 Troubleshooting

### Ollama Issues

**Problem**: "Connection refused"
```bash
# Solution: Start Ollama
ollama serve

# Or check if running
ps aux | grep ollama
```

**Problem**: "Model not found"
```bash
# Solution: Pull the model
ollama pull llama3.2

# List installed models
ollama list
```

**Problem**: "Out of memory"
```bash
# Solution: Use smaller model
ollama pull phi3  # Only 3.8B parameters

# Or increase memory limit
export OLLAMA_MAX_LOADED_MODELS=1
```

### HuggingFace Issues

**Problem**: "Invalid API key"
```bash
# Solution: Check your API key
# Go to https://huggingface.co/settings/tokens
# Create new token if needed
```

**Problem**: "Model is loading"
```bash
# Solution: Wait 20-30 seconds
# HuggingFace cold-starts models
# First request may be slow
```

### General Issues

**Problem**: "JSON parsing error"
```python
# Solution: OpenClaw has automatic fallback
# It will extract signal from text if JSON fails
# Check logs for details
```

**Problem**: "Timeout"
```python
# Solution: Increase timeout
model = OpenClawModel(backend="ollama", model_name="llama3.2")
# Timeout is set to 60 seconds by default
```

---

## 📊 Performance Comparison

| Backend | Speed | Cost | Privacy | Setup | Accuracy |
|---------|-------|------|---------|-------|----------|
| **Ollama** | ⚡⚡⚡ | FREE | 🔒🔒🔒 | Easy | ⭐⭐⭐⭐ |
| **HuggingFace** | ⚡⚡ | FREE* | 🔒 | Easiest | ⭐⭐⭐ |
| **LM Studio** | ⚡⚡⚡ | FREE | 🔒🔒🔒 | Easy | ⭐⭐⭐⭐ |
| **LocalAI** | ⚡⚡⚡ | FREE | 🔒🔒🔒 | Medium | ⭐⭐⭐⭐ |
| **OpenRouter** | ⚡⚡⚡⚡ | Paid* | 🔒 | Easiest | ⭐⭐⭐⭐⭐ |

*FREE tier available

---

## 🎯 Best Practices

### 1. Start with Ollama
```python
# Easiest to set up, completely free, private
model = OpenClawModel(backend="ollama", model_name="llama3.2")
```

### 2. Use Multiple Models for Consensus
```python
# Better accuracy through voting
consensus = AIConsensusEngine()
consensus.add_model(OpenClawModel(backend="ollama", model_name="llama3.2"))
consensus.add_model(OpenClawModel(backend="ollama", model_name="mistral"))
consensus.add_model(OpenClawModel(backend="ollama", model_name="phi3"))
```

### 3. Cache Model Instances
```python
# Don't create new model for each prediction
# Create once, reuse many times
model = OpenClawModel(backend="ollama", model_name="llama3.2")

for market_data in data_stream:
    prediction = model.predict(market_data)
```

### 4. Monitor Performance
```python
# Track model accuracy
info = model.get_model_info()
print(f"Accuracy: {info['accuracy']}%")
print(f"Total predictions: {info['total_predictions']}")
```

---

## 🚀 Next Steps

1. **Choose Backend**: Start with Ollama for local, or HuggingFace for cloud
2. **Install & Configure**: Follow setup guide above
3. **Test Integration**: Run example code
4. **Add to Trading System**: Integrate with consensus engine
5. **Monitor Performance**: Track accuracy and adjust

---

## 📚 Additional Resources

- **Ollama**: https://ollama.com/
- **HuggingFace**: https://huggingface.co/
- **LM Studio**: https://lmstudio.ai/
- **LocalAI**: https://localai.io/
- **OpenRouter**: https://openrouter.ai/

---

## 🎉 Benefits of OpenClaw

✅ **Cost Savings**: No API costs with local models  
✅ **Privacy**: Keep trading data private  
✅ **Flexibility**: Choose from 100+ models  
✅ **Performance**: Fast local inference  
✅ **Reliability**: No API rate limits  
✅ **Control**: Full control over model behavior  

---

**Status**: ✅ Ready to Use  
**Integration**: Complete  
**Recommended**: Ollama + Llama 3.2

---

*OpenClaw Integration Guide - KAEL Trading System*  
*Last Updated: February 2026*