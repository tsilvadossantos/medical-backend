# LLM Provider Configuration

The Medical Backend API is **GenAI-agnostic** with pluggable LLM providers. This document details configuration options for each supported provider.

## Available Providers

| Provider | Cost | Latency | Setup |
|----------|------|---------|-------|
| **Ollama** (default) | Free | Local/Fast | Bundled in Docker |
| **OpenAI** | Paid | Cloud | API key required |
| **Anthropic** | Paid | Cloud | API key required |

## Provider Selection

Set the provider in your `.env` file:

```bash
LLM_PROVIDER=ollama    # Default - free, local
LLM_PROVIDER=openai    # Requires OPENAI_API_KEY
LLM_PROVIDER=anthropic # Requires ANTHROPIC_API_KEY
```

---

## Ollama Configuration

Ollama is the default provider, running locally for free inference without API costs.

### Basic Settings

```bash
OLLAMA_URL=http://ollama:11434    # Bundled container
OLLAMA_MODEL=llama3.2             # Model to use
```

### Performance Tuning Parameters

| Parameter | Default | Description | Performance Impact |
|-----------|---------|-------------|-------------------|
| `OLLAMA_TEMPERATURE` | 0.3 | Controls randomness (0.0-1.0) | Lower = faster, more deterministic |
| `OLLAMA_TOP_P` | 0.9 | Nucleus sampling threshold | Lower = slightly faster |
| `OLLAMA_TOP_K` | 40 | Token selection pool size | Lower = faster inference |
| `OLLAMA_NUM_CTX` | 4096 | Context window size | Smaller = faster, less memory |
| `OLLAMA_NUM_PREDICT` | Auto | Max tokens to generate | Caps generation time |
| `OLLAMA_TIMEOUT` | 60 | Request timeout (seconds) | Increase for larger models |

### Configuration Examples

#### Fast Responses (Lower Quality)
```bash
OLLAMA_TEMPERATURE=0.1
OLLAMA_TOP_K=20
OLLAMA_NUM_CTX=2048
OLLAMA_NUM_PREDICT=200
```

#### Balanced (Default)
```bash
OLLAMA_TEMPERATURE=0.3
OLLAMA_TOP_P=0.9
OLLAMA_TOP_K=40
OLLAMA_NUM_CTX=4096
```

#### High Quality (Slower)
```bash
OLLAMA_TEMPERATURE=0.5
OLLAMA_TOP_P=0.95
OLLAMA_TOP_K=60
OLLAMA_NUM_CTX=8192
OLLAMA_TIMEOUT=120
```

### Model Recommendations

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `llama3.2` | 3B | Fast | Good | Default, general use |
| `llama3.2:1b` | 1B | Fastest | Basic | Quick responses |
| `llama3.1:8b` | 8B | Medium | Better | More detailed summaries |
| `mistral` | 7B | Medium | Good | Alternative option |
| `medllama2` | 7B | Medium | Medical | Healthcare-specific |

### Ollama URL Options

**Bundled (Docker container):**
```bash
OLLAMA_URL=http://ollama:11434
```

**External (Mac/Windows with Docker Desktop):**
```bash
OLLAMA_URL=http://host.docker.internal:11434
```

**External (Linux or remote server):**
```bash
OLLAMA_URL=http://192.168.1.100:11434
```

---

## OpenAI Configuration

Cloud-based provider using OpenAI's API.

### Settings

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
```

### Model Options

| Model | Cost | Speed | Quality |
|-------|------|-------|---------|
| `gpt-3.5-turbo` | $ | Fast | Good |
| `gpt-4o-mini` | $$ | Fast | Better |
| `gpt-4o` | $$$ | Medium | Best |

### Built-in Parameters

The OpenAI provider uses these fixed parameters:
- `temperature`: 0.3
- `top_p`: 0.9
- `max_tokens`: Based on request

---

## Anthropic Configuration

Cloud-based provider using Anthropic's Claude API.

### Settings

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

### Model Options

| Model | Cost | Speed | Quality |
|-------|------|-------|---------|
| `claude-3-haiku-20240307` | $ | Fastest | Good |
| `claude-3-5-sonnet-20241022` | $$ | Medium | Better |
| `claude-3-opus-20240229` | $$$ | Slower | Best |

### Built-in Parameters

The Anthropic provider uses these fixed parameters:
- `temperature`: 0.3
- `top_p`: 0.9
- `max_tokens`: Based on request

---

## Fallback Behavior

If the configured LLM provider is unavailable or fails, the system falls back to **rule-based extraction**:

1. Attempts LLM-based summary generation
2. On failure, extracts key information using regex patterns
3. Returns structured summary from note content

This ensures summaries are always available even without LLM connectivity.

---

## Troubleshooting

### Ollama Issues

**Model not found:**
```bash
# Pull the model first
docker exec -it medical-backend-ollama-1 ollama pull llama3.2
```

**Timeout errors:**
```bash
# Increase timeout for larger models
OLLAMA_TIMEOUT=120
```

**Out of memory:**
```bash
# Use smaller context or model
OLLAMA_NUM_CTX=2048
OLLAMA_MODEL=llama3.2:1b
```

### OpenAI/Anthropic Issues

**Authentication errors:**
- Verify API key is correct
- Check key has sufficient permissions
- Ensure billing is active

**Rate limiting:**
- Implement retry logic (built-in)
- Consider upgrading API tier

---

## Performance Comparison

Typical response times for a 500-character summary:

| Provider | Model | Avg Time | Cost/1K Summaries |
|----------|-------|----------|-------------------|
| Ollama | llama3.2 | ~3s | $0 |
| Ollama | llama3.1:8b | ~8s | $0 |
| OpenAI | gpt-3.5-turbo | ~2s | ~$0.50 |
| OpenAI | gpt-4o-mini | ~3s | ~$1.50 |
| Anthropic | claude-3-haiku | ~2s | ~$0.25 |
| Anthropic | claude-3.5-sonnet | ~4s | ~$3.00 |

*Times vary based on hardware, network, and prompt length.*

---

## Adding Custom Providers

To add a new LLM provider:

1. Create `app/providers/your_provider.py`
2. Extend `LLMProvider` base class
3. Implement `generate_summary()` method
4. Register in `app/providers/factory.py`
5. Add settings to `app/core/settings.py`

See `app/providers/base.py` for the interface definition.
