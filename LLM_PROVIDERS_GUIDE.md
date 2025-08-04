# LLM Providers Guide - Dynamic Quiz Application

This guide provides detailed information about all supported LLM providers, their API keys, models, and performance characteristics for the dynamic quiz application.

## 🚀 Supported LLM Providers

### 1. **OpenAI** - Industry Leader
**Best for**: High-quality quiz generation and educational content
- **API Key Format**: `sk-...`
- **Get API Key**: https://platform.openai.com/api-keys
- **Models Available**:
  - `gpt-4o` (Recommended) - Fastest GPT-4 model
  - `gpt-4o-mini` - Cost-effective option
  - `gpt-3.5-turbo` - Budget-friendly
- **Performance**: 1-3 seconds
- **Cost**: $0.01-0.03 per 1K tokens
- **Strengths**: Excellent reasoning, consistent JSON output
- **Use Case**: Primary quiz generation and complex explanations

### 2. **Anthropic (Claude)** - Educational Excellence
**Best for**: Educational content and tutoring
- **API Key Format**: `sk-ant-...`
- **Get API Key**: https://console.anthropic.com/
- **Models Available**:
  - `claude-3-sonnet-20240229` (Recommended) - Balanced performance
  - `claude-3-haiku-20240307` - Ultra-fast, cost-effective
  - `claude-3-opus-20240229` - Highest quality
- **Performance**: 1-4 seconds
- **Cost**: $0.003-0.015 per 1K tokens
- **Strengths**: Excellent for educational content, strong reasoning
- **Use Case**: Primary chatbot and educational explanations

### 3. **Google (Gemini)** - Fast and Reliable
**Best for**: Quick responses and cost-effective generation
- **API Key Format**: `AIza...`
- **Get API Key**: https://makersuite.google.com/app/apikey
- **Models Available**:
  - `gemini-1.5-flash` (Recommended) - Fast and efficient
  - `gemini-1.5-pro` - Higher quality
  - `gemini-pro` - Standard model
- **Performance**: 0.5-2 seconds
- **Cost**: $0.00025-0.0025 per 1K tokens
- **Strengths**: Very fast, good JSON output, cost-effective
- **Use Case**: Fast quiz generation and quick responses

### 4. **Groq** - Ultra-Fast Inference
**Best for**: Speed-critical applications
- **API Key Format**: `gsk_...`
- **Get API Key**: https://console.groq.com/
- **Models Available**:
  - `mixtral-8x7b-32768` (Recommended) - Fast and capable
  - `llama3-8b-8192` - Good balance
  - `llama3-70b-8192` - Higher quality
- **Performance**: 0.1-1 second ⚡
- **Cost**: $0.0001-0.0008 per 1K tokens
- **Strengths**: Extremely fast, cost-effective
- **Use Case**: Ultra-fast quiz generation

### 5. **Cohere** - Command Models
**Best for**: Structured content generation
- **API Key Format**: `...`
- **Get API Key**: https://dashboard.cohere.com/
- **Models Available**:
  - `command-r-plus` (Recommended) - Latest model
  - `command-r` - Standard model
  - `command-light` - Fast model
- **Performance**: 1-3 seconds
- **Cost**: $0.0005-0.003 per 1K tokens
- **Strengths**: Good for structured output, reliable
- **Use Case**: Reliable quiz generation

### 6. **Mistral AI** - European Excellence
**Best for**: High-quality European models
- **API Key Format**: `...`
- **Get API Key**: https://console.mistral.ai/
- **Models Available**:
  - `mistral-large-latest` (Recommended) - High quality
  - `mistral-medium-latest` - Balanced
  - `mistral-small-latest` - Fast
- **Performance**: 1-3 seconds
- **Cost**: $0.0005-0.002 per 1K tokens
- **Strengths**: High quality, good reasoning
- **Use Case**: Quality-focused quiz generation

### 7. **Ollama** - Local Models (Optional)
**Best for**: Privacy and offline usage
- **Setup**: Local installation required
- **Installation**: https://ollama.ai/
- **Models Available**:
  - `llama3.1:8b` (Recommended) - Good balance
  - `llama3.1:70b` - Higher quality
  - `mistral:7b` - Fast and efficient
- **Performance**: 2-10 seconds (depends on hardware)
- **Cost**: Free (local compute)
- **Strengths**: Privacy, no API costs, offline
- **Use Case**: Privacy-focused deployments

## 🔧 Configuration Setup

### Environment Variables

Copy the `env.example` file to `.env` and configure your API keys:

```bash
# Copy example file
cp env.example .env

# Edit with your API keys
nano .env
```

### Required API Keys (Minimum Setup)

For optimal performance, configure at least 3 providers:

```env
# Essential providers
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=your-google-key

# Optional but recommended
GROQ_API_KEY=gsk-your-groq-key
COHERE_API_KEY=your-cohere-key
MISTRAL_API_KEY=your-mistral-key
```

### Provider Priority Configuration

Configure the order of preference for different tasks:

```env
# Quiz generation priority (fastest first)
QUIZ_GENERATION_MODELS=groq,google,openai,anthropic,cohere,mistral

# Chatbot priority (quality first)
CHATBOT_MODELS=anthropic,openai,mistral,cohere,google
```

## 📊 Performance Comparison

| Provider | Speed | Quality | Cost | Best For |
|----------|-------|---------|------|----------|
| **Groq** | ⚡⚡⚡ | ⭐⭐ | 💰 | Ultra-fast generation |
| **Google** | ⚡⚡ | ⭐⭐⭐ | 💰💰 | Fast, cost-effective |
| **OpenAI** | ⚡ | ⭐⭐⭐⭐⭐ | 💰💰💰 | High quality |
| **Anthropic** | ⚡ | ⭐⭐⭐⭐⭐ | 💰💰💰 | Educational content |
| **Cohere** | ⚡ | ⭐⭐⭐⭐ | 💰💰 | Reliable generation |
| **Mistral** | ⚡ | ⭐⭐⭐⭐ | 💰💰 | Quality-focused |
| **Ollama** | ⚡⚡ | ⭐⭐⭐ | Free | Privacy-focused |

## 🎯 Recommended Configurations

### 1. **Speed-Optimized Setup**
```env
QUIZ_GENERATION_MODELS=groq,google,openai
CHATBOT_MODELS=anthropic,openai,google
```

### 2. **Quality-Optimized Setup**
```env
QUIZ_GENERATION_MODELS=openai,anthropic,mistral
CHATBOT_MODELS=anthropic,openai,mistral
```

### 3. **Cost-Optimized Setup**
```env
QUIZ_GENERATION_MODELS=google,groq,cohere
CHATBOT_MODELS=cohere,google,anthropic
```

### 4. **Balanced Setup (Recommended)**
```env
QUIZ_GENERATION_MODELS=groq,google,openai,anthropic
CHATBOT_MODELS=anthropic,openai,google,cohere
```

## 🔄 Fallback Strategy

The application uses intelligent fallback:

1. **Primary Provider**: First in the list
2. **Fallback Providers**: Try in order if primary fails
3. **Error Handling**: Graceful degradation
4. **Performance Monitoring**: Logs response times

### Fallback Configuration
```env
ENABLE_FALLBACK=true
MAX_RETRIES=3
TIMEOUT_SECONDS=30
```

## 💰 Cost Optimization

### Budget-Friendly Setup
```env
# Use cost-effective providers
QUIZ_GENERATION_MODELS=google,groq,cohere
CHATBOT_MODELS=cohere,google

# Estimated cost: $0.001-0.005 per quiz
```

### High-Quality Setup
```env
# Use premium providers
QUIZ_GENERATION_MODELS=openai,anthropic,mistral
CHATBOT_MODELS=anthropic,openai

# Estimated cost: $0.01-0.03 per quiz
```

## 🚀 Getting Started

### 1. **Get API Keys**
- [OpenAI](https://platform.openai.com/api-keys)
- [Anthropic](https://console.anthropic.com/)
- [Google](https://makersuite.google.com/app/apikey)
- [Groq](https://console.groq.com/)
- [Cohere](https://dashboard.cohere.com/)
- [Mistral](https://console.mistral.ai/)

### 2. **Configure Environment**
```bash
cd backend
cp env.example .env
# Edit .env with your API keys
```

### 3. **Test Configuration**
```bash
# Start the backend
uvicorn main:app --reload

# Check provider status at
curl http://localhost:8000/health
```

### 4. **Monitor Performance**
The application logs:
- Which provider generated each quiz
- Response times for each provider
- Fallback usage statistics

## 🔍 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify API key format
   - Check API key permissions
   - Ensure sufficient credits

2. **Rate Limiting**
   - Providers have different rate limits
   - Application includes throttling
   - Consider upgrading API plans

3. **Timeout Issues**
   - Increase `TIMEOUT_SECONDS`
   - Check network connectivity
   - Use faster providers (Groq, Google)

### Provider-Specific Issues

- **OpenAI**: Check API usage limits
- **Anthropic**: Verify model availability
- **Google**: Ensure API is enabled
- **Groq**: Check model availability
- **Cohere**: Verify API key permissions
- **Mistral**: Check regional availability

## 📈 Performance Monitoring

The application provides real-time monitoring:

```python
# Example log output
Quiz generated by groq in 0.45s
Chat response from anthropic in 1.23s
Fallback to openai after groq timeout
```

## 🎯 Best Practices

1. **Start with 3-4 providers** for redundancy
2. **Use Groq/Google for speed-critical tasks**
3. **Use Anthropic/OpenAI for quality-critical tasks**
4. **Monitor costs and adjust provider mix**
5. **Test fallback scenarios regularly**
6. **Keep API keys secure and rotate regularly**

This multi-provider setup ensures maximum reliability, speed, and cost-effectiveness for your dynamic quiz application! 