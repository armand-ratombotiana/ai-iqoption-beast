"""
OpenClaw Test Script
Test open-source AI model integration
"""

import sys
from ai.models.openclaw_model import OpenClawModel, create_openclaw_model
from ai.models.consensus_engine import AIConsensusEngine


def test_single_model():
    """Test single OpenClaw model"""
    print("\n" + "=" * 70)
    print("🧪 Testing Single OpenClaw Model")
    print("=" * 70)
    
    # Create model (defaults to Ollama + Llama 3.2)
    print("\n📦 Creating OpenClaw model...")
    model = create_openclaw_model(backend="ollama")
    
    # Model info
    info = model.get_model_info()
    print(f"\n✅ Model created:")
    print(f"   Name: {info['name']}")
    print(f"   Provider: {info['provider']}")
    print(f"   Backend: {info['backend']}")
    print(f"   Model: {info['model']}")
    
    # Test market data
    market_data = {
        'pair': 'EURUSD-OTC',
        'current_price': 1.0850,
        'rsi_14': 35,
        'rsi_7': 32,
        'trend': 'downtrend',
        'volatility': 'medium',
        'macd': {
            'macd': -0.002,
            'signal': -0.001,
            'histogram': -0.001
        },
        'bb_position': 0.2,
        'support': 1.0820,
        'resistance': 1.0880
    }
    
    print(f"\n📊 Market Data:")
    print(f"   Pair: {market_data['pair']}")
    print(f"   Price: {market_data['current_price']}")
    print(f"   RSI: {market_data['rsi_14']}")
    print(f"   Trend: {market_data['trend']}")
    
    # Get prediction
    print(f"\n🤖 Getting prediction...")
    try:
        prediction = model.predict(market_data)
        
        print(f"\n✅ Prediction:")
        print(f"   Signal: {prediction['signal']}")
        print(f"   Confidence: {prediction['confidence']}%")
        print(f"   Reasoning: {prediction['reasoning']}")
        print(f"   Model: {prediction['model']}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\n💡 Make sure Ollama is running:")
        print(f"   1. Install: curl -fsSL https://ollama.com/install.sh | sh")
        print(f"   2. Pull model: ollama pull llama3.2")
        print(f"   3. Start server: ollama serve")
        return False


def test_consensus():
    """Test consensus with multiple OpenClaw models"""
    print("\n" + "=" * 70)
    print("🧪 Testing OpenClaw Consensus Engine")
    print("=" * 70)
    
    # Create consensus engine
    print("\n📦 Creating consensus engine...")
    consensus = AIConsensusEngine(consensus_threshold=0.66)
    
    # Add multiple models
    print("\n➕ Adding models...")
    try:
        model1 = OpenClawModel(backend="ollama", model_name="llama3.2")
        print("   ✅ Added: llama3.2")
        consensus.add_model(model1, weight=1.0)
        
        # Try to add more models if available
        try:
            model2 = OpenClawModel(backend="ollama", model_name="mistral")
            print("   ✅ Added: mistral")
            consensus.add_model(model2, weight=1.0)
        except:
            print("   ⚠️  Mistral not available (optional)")
        
        try:
            model3 = OpenClawModel(backend="ollama", model_name="phi3")
            print("   ✅ Added: phi3")
            consensus.add_model(model3, weight=1.0)
        except:
            print("   ⚠️  Phi3 not available (optional)")
        
    except Exception as e:
        print(f"\n❌ Error adding models: {e}")
        return False
    
    # Test market data
    market_data = {
        'pair': 'EURUSD-OTC',
        'current_price': 1.0850,
        'rsi_14': 72,
        'rsi_7': 78,
        'trend': 'uptrend',
        'volatility': 'high',
        'macd': {
            'macd': 0.003,
            'signal': 0.002,
            'histogram': 0.001
        },
        'bb_position': 0.9,
        'support': 1.0820,
        'resistance': 1.0880
    }
    
    print(f"\n📊 Market Data:")
    print(f"   Pair: {market_data['pair']}")
    print(f"   Price: {market_data['current_price']}")
    print(f"   RSI: {market_data['rsi_14']} (Overbought)")
    print(f"   Trend: {market_data['trend']}")
    
    # Get consensus
    print(f"\n🤖 Getting consensus...")
    try:
        result = consensus.get_consensus_signal(market_data)
        
        print(f"\n✅ Consensus Result:")
        print(f"   Signal: {result['signal']}")
        print(f"   Confidence: {result['confidence']}%")
        print(f"   Agreement: {result['agreement']}%")
        print(f"   Consensus Reached: {'✅ YES' if result['consensus_reached'] else '❌ NO'}")
        print(f"   Total Models: {result['total_models']}")
        
        print(f"\n📊 Voting Breakdown:")
        print(f"   CALL Weight: {result['call_weight']}")
        print(f"   PUT Weight: {result['put_weight']}")
        
        print(f"\n🗳️  Individual Votes:")
        for model_name, vote in result['models_voted'].items():
            print(f"   • {model_name}:")
            print(f"     Signal: {vote['signal']} | Confidence: {vote['confidence']}%")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def list_available_models():
    """List all available models"""
    print("\n" + "=" * 70)
    print("📋 Available OpenClaw Models")
    print("=" * 70)
    
    models = OpenClawModel.list_available_models()
    
    for backend, model_list in models.items():
        print(f"\n🔧 {backend.upper()}:")
        for model in model_list:
            print(f"   • {model}")
        
        recommended = OpenClawModel.get_recommended_model(backend)
        print(f"   ⭐ Recommended: {recommended}")


def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print("🚀 OpenClaw Integration Test")
    print("=" * 70)
    
    # List available models
    list_available_models()
    
    # Test single model
    success1 = test_single_model()
    
    if success1:
        # Test consensus
        test_consensus()
    
    print("\n" + "=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)
    
    if not success1:
        print("\n💡 Quick Setup Guide:")
        print("   1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
        print("   2. Pull model: ollama pull llama3.2")
        print("   3. Run this test again")
        print("\n📚 Full guide: See OPENCLAW_INTEGRATION_GUIDE.md")


if __name__ == "__main__":
    main()