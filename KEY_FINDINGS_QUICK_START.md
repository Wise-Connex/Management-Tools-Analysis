# Key Findings Module - Quick Start Guide

## Overview

The Key Findings module provides AI-powered doctoral-level analysis of dashboard data using OpenRouter.ai. This guide will help you get the module up and running quickly.

## Prerequisites

1. **OpenRouter.ai API Key**: Sign up at [OpenRouter.ai](https://openrouter.ai/) and get your API key
2. **Python 3.8+**: Ensure you have the required Python version
3. **Existing Dashboard**: The module integrates with the existing Management Tools Analysis Dashboard

## Installation Steps

### 1. Environment Setup

```bash
# Navigate to dashboard_app directory
cd dashboard_app

# Add new dependencies to requirements.txt
echo "aiohttp>=3.8.0" >> requirements.txt
echo "asyncio-throttle>=1.0.2" >> requirements.txt

# Install dependencies using UV
uv pip install -r requirements.txt
```

### 2. Environment Configuration

Create or update your `.env` file:

```env
# OpenRouter.ai Configuration
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_TIMEOUT=30
OPENROUTER_MAX_RETRIES=3

# ⚠️ CRITICAL: Persistent Database Configuration (Required for Docker/Dokploy)
KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
KEY_FINDINGS_BACKUP_PATH=/app/data/backups/
KEY_FINDINGS_BACKUP_INTERVAL=3600  # Backup every hour
KEY_FINDINGS_DATA_DIR=/app/data
KEY_FINDINGS_VOLUME_MOUNT=/var/lib/key_findings_data

# Key Findings Configuration
KEY_FINDINGS_CACHE_TTL=86400
KEY_FINDINGS_MAX_HISTORY=100
KEY_FINDINGS_AUTO_GENERATE=true
KEY_FINDINGS_MAX_DATA_POINTS=10000
KEY_FINDINGS_PCA_WEIGHT=0.3
KEY_FINDINGS_CONFIDENCE_THRESHOLD=0.7
KEY_FINDINGS_ANONYMIZE_DATA=true
KEY_FINDINGS_MAX_TOKENS=4000

# Model Configuration
PRIMARY_MODEL=openai/gpt-4o-mini
FALLBACK_MODELS=nvidia/llama-3.1-nemotron-70b-instruct,meta-llama/llama-3.1-8b-instruct:free
```

### 3. Module Installation

Create the Key Findings module structure:

```bash
# Create module directory
mkdir key_findings

# Create the core files (copy from implementation plan)
touch key_findings/__init__.py
touch key_findings/database_manager.py
touch key_findings/ai_service.py
touch key_findings/data_aggregator.py
touch key_findings/prompt_engineer.py
touch key_findings/modal_component.py
touch key_findings/dashboard_integration.py
touch key_findings/config.py
```

### 4. Dashboard Integration

Modify `dashboard_app/app.py` to integrate the Key Findings module:

```python
# Add these imports at the top
from key_findings.dashboard_integration import KeyFindingsIntegration
from key_findings.config import KeyFindingsConfig

# After app creation, initialize Key Findings
key_findings_config = KeyFindingsConfig.from_env()
key_findings_integration = KeyFindingsIntegration(app, db_manager, key_findings_config.to_dict())

# Add Key Findings modal to layout
app.layout.children.append(key_findings_integration.modal_component.create_modal_layout())
```

### 5. Database Initialization

The Key Findings database will be automatically created on first run. To verify:

```python
# Test database creation
from key_findings.database_manager import KeyFindingsDBManager
db = KeyFindingsDBManager("test_key_findings.db")
print("Database created successfully!")
```

## Usage Guide

### 1. Accessing Key Findings

1. Select a management tool from the dropdown
2. Choose one or more data sources
3. Click the "🧠 Generar Key Findings" button
4. The modal will open and display AI-generated insights

### 2. Understanding the Output

The Key Findings modal provides:

- **🎯 Hallazgos Principales**: 3-5 bullet points with doctoral-level reasoning
- **📈 Insights de PCA**: Principal Component Analysis interpretations
- **📋 Resumen Ejecutivo**: 2-3 paragraph executive summary

### 3. Available Actions

- **🔄 Regenerar**: Force new analysis (bypasses cache)
- **💾 Guardar**: Save findings for future reference
- **⭐ Calificar**: Rate the quality of AI analysis
- **Cerrar**: Close the modal

## Configuration Options

### Model Selection

Configure which AI models to use:

```python
# In config or environment
PRIMARY_MODEL=openai/gpt-4o-mini
FALLBACK_MODELS=nvidia/llama-3.1-nemotron-70b-instruct,meta-llama/llama-3.1-8b-instruct:free
```

### Cache Settings

Adjust caching behavior:

```env
KEY_FINDINGS_CACHE_TTL=86400  # 24 hours
KEY_FINDINGS_MAX_HISTORY=100  # Maximum cached reports
```

### Analysis Parameters

Fine-tune analysis depth:

```env
KEY_FINDINGS_PCA_WEIGHT=0.3  # Emphasis on PCA insights
KEY_FINDINGS_CONFIDENCE_THRESHOLD=0.7  # Minimum confidence score
```

## Docker/Dokploy Deployment

### ⚠️ Critical: Persistent Storage Setup

For Docker/Dokploy deployments, you MUST configure persistent storage to prevent cache loss during updates.

#### 1. Server Setup

Create persistent directory on your Dokploy server:

```bash
# SSH into your Dokploy server
ssh your-server

# Create persistent directory
sudo mkdir -p /var/lib/key_findings_data
sudo chmod 755 /var/lib/key_findings_data
sudo chown 1000:1000 /var/lib/key_findings_data  # Match container user

# Verify directory exists and has correct permissions
ls -la /var/lib/key_findings_data
```

#### 2. Docker Compose Configuration

Update your `docker-compose.yml`:

```yaml
version: "3.8"

services:
  dashboard-app:
    build: .
    ports:
      - "8050:8050"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
    volumes:
      - key_findings_data:/app/data
      - ./dashboard_app:/app
    restart: unless-stopped

volumes:
  key_findings_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /var/lib/key_findings_data
```

#### 3. Dockerfile Updates

Ensure your Dockerfile creates the data directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Create data directory for persistent storage
RUN mkdir -p /app/data && \
    chmod 755 /app/data

# ... rest of your Dockerfile ...

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser
```

#### 4. Verify Persistence

After deployment, verify persistent storage is working:

```bash
# Check if database file exists in persistent directory
ls -la /var/lib/key_findings_data/

# Should see key_findings.db and backups/ directory
```

## Troubleshooting

### Common Issues

1. **API Key Not Working**

   - Verify your OpenRouter.ai API key
   - Check if the key has sufficient credits
   - Ensure the key is properly set in environment variables

2. **No Analysis Generated**

   - Check if data sources have sufficient data
   - Verify the selected tool has data in the database
   - Check browser console for error messages

3. **Slow Response Times**

   - Check network connectivity to OpenRouter.ai
   - Consider using faster models for testing
   - Monitor API usage and limits

4. **Cache Loss After Docker Update** ⚠️

   - Verify persistent volume is mounted correctly
   - Check `/var/lib/key_findings_data` directory exists on server
   - Ensure container has write permissions to volume
   - Verify `KEY_FINDINGS_DB_PATH` points to `/app/data/key_findings.db`

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Monitoring

Monitor cache efficiency:

```python
from key_findings.database_manager import KeyFindingsDBManager
db = KeyFindingsDBManager()
# Check cache statistics in cache_statistics table
```

### Verify Persistent Storage

Test that persistence is working correctly:

```python
from key_findings.database_manager import KeyFindingsDBManager
db = KeyFindingsDBManager("/app/data/key_findings.db")
persistence_ok = db.verify_persistence()
print(f"Persistence working: {persistence_ok}")

# Get database information
db_info = db.get_database_info()
print(f"Database size: {db_info['database_size_mb']} MB")
print(f"Total reports: {db_info['total_reports']}")
print(f"Backup count: {db_info['backup_count']}")
```

## Testing

### Unit Tests

Run the test suite:

```bash
cd dashboard_app
python -m pytest tests/test_key_findings.py -v
```

### Integration Tests

Test the full workflow:

```bash
python -m pytest tests/test_integration.py -v
```

### Manual Testing

1. Start the dashboard: `python app.py`
2. Select a tool and data sources
3. Click "🧠 Generar Key Findings"
4. Verify the modal opens and displays analysis
5. Test all buttons and interactions

## Security Considerations

### Data Privacy

- All data is anonymized before sending to AI
- No sensitive identifiers are included in prompts
- Local caching reduces API calls

### API Security

- API keys are stored in environment variables
- Rate limiting prevents abuse
- Request timeouts prevent hanging

### Audit Trail

All AI interactions are logged in:

- `model_performance` table
- `key_findings_history` table
- Application logs

## Performance Optimization

### Cache Management

- Scenario-based caching prevents redundant API calls
- Hash-based identification ensures cache accuracy
- TTL-based expiration keeps data fresh

### API Efficiency

- Fallback models ensure reliability
- Retry logic with exponential backoff
- Token limits control costs

### Database Optimization

- Indexed queries for fast lookups
- Connection pooling for efficiency
- Regular cleanup of old records

## Support

### Documentation

- Full architecture: `KEY_FINDINGS_ARCHITECTURE.md`
- Implementation details: `KEY_FINDINGS_IMPLEMENTATION_PLAN.md`
- API documentation: Inline code comments

### Getting Help

1. Check the troubleshooting section
2. Review application logs
3. Test with different data combinations
4. Monitor API usage and costs

## Future Enhancements

### Planned Features

- Comparative analysis across tools
- Export functionality (PDF, Word)
- Advanced visualization integration
- Real-time collaboration features

### Model Improvements

- Fine-tuned domain-specific models
- Multi-modal analysis capabilities
- Custom prompt templates
- User preference learning

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit pull request

### Code Standards

- Follow PEP 8 guidelines
- Add comprehensive tests
- Update documentation
- Ensure backward compatibility

---

**Note**: This module requires an active OpenRouter.ai API key and internet connection for AI analysis. The caching system minimizes API usage and costs.
