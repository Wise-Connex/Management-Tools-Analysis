# Key Findings Module - Complete Setup Guide

## 🚀 Quick Start

This guide provides step-by-step instructions for setting up the Key Findings module in your Management Tools Analysis Dashboard.

## 📋 Prerequisites

### System Requirements

- Python 3.8+
- SQLite 3.x
- 2GB+ RAM
- 1GB+ disk space
- Internet connection for AI API

### API Keys

- **OpenRouter.ai API Key**: Required for AI analysis
  - Get your key at: https://openrouter.ai/keys
  - Minimum credits: $5 recommended for testing

### Dependencies

```bash
# Core dependencies
pip install dash dash-bootstrap-components pandas numpy scipy scikit-learn
pip install plotly statsmodels aiohttp

# Key Findings specific
pip install asyncio-mqtt sqlalchemy pytest
```

## 🛠️ Installation Steps

### 1. Module Setup

The Key Findings module is already included in the `dashboard_app/key_findings/` directory. No additional installation needed.

### 2. Environment Configuration

Create or update your `.env` file:

```env
# Key Findings Configuration
KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
KEY_FINDINGS_BACKUP_PATH=/app/data/backups/
KEY_FINDINGS_VOLUME_MOUNT=/var/lib/key_findings_data

# AI Configuration (REQUIRED)
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
PRIMARY_MODEL=openai/gpt-4o-mini
FALLBACK_MODELS=nvidia/llama-3.1-nemotron-70b-instruct,meta-llama/llama-3.1-8b-instruct:free

# Analysis Parameters
KEY_FINDINGS_PCA_WEIGHT=0.3
KEY_FINDINGS_CONFIDENCE_THRESHOLD=0.7
KEY_FINDINGS_MAX_TOKENS=4000
KEY_FINDINGS_CACHE_TTL=86400
KEY_FINDINGS_MAX_HISTORY=100
KEY_FINDINGS_AUTO_GENERATE=true

# Debug (optional)
KEY_FINDINGS_DEBUG=false
```

### 3. Docker Setup (Recommended)

#### Using Docker Compose

1. **Create directories**:

```bash
mkdir -p ./data/key_findings
mkdir -p ./data/key_findings/backups
mkdir -p ./config/key_findings
mkdir -p /var/lib/key_findings_data
```

2. **Update docker-compose.yml**:

```yaml
version: "3.8"

services:
  dashboard-app:
    build: .
    container_name: management-tools-dashboard
    ports:
      - "8050:8050"
    environment:
      # Key Findings Configuration
      - KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
      - KEY_FINDINGS_BACKUP_PATH=/app/data/backups
      - KEY_FINDINGS_VOLUME_MOUNT=/var/lib/key_findings_data
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - PRIMARY_MODEL=openai/gpt-4o-mini
      - FALLBACK_MODELS=nvidia/llama-3.1-nemotron-70b-instruct,meta-llama/llama-3.1-8b-instruct:free
      - KEY_FINDINGS_PCA_WEIGHT=0.3
      - KEY_FINDINGS_CONFIDENCE_THRESHOLD=0.7
      - KEY_FINDINGS_MAX_TOKENS=4000
    volumes:
      - ./data/key_findings:/app/data:rw
      - ./data/key_findings/backups:/app/data/backups:rw
      - /var/lib/key_findings_data:/var/lib/key_findings_data:rw
    restart: unless-stopped

volumes:
  key_findings_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /var/lib/key_findings_data
```

3. **Run the application**:

```bash
# Set your API key
export OPENROUTER_API_KEY=your-api-key-here

# Build and run
docker-compose up --build
```

#### Manual Docker Setup

1. **Build the image**:

```bash
docker build -t management-tools-dashboard .
```

2. **Run with volume mounts**:

```bash
docker run -d \
  --name management-tools-dashboard \
  -p 8050:8050 \
  -v ./data/key_findings:/app/data:rw \
  -v ./data/key_findings/backups:/app/data/backups:rw \
  -v /var/lib/key_findings_data:/var/lib/key_findings_data:rw \
  -e OPENROUTER_API_KEY=your-api-key-here \
  management-tools-dashboard
```

### 4. Local Development Setup

1. **Install dependencies**:

```bash
cd dashboard_app
pip install -r requirements.txt
```

2. **Set environment variables**:

```bash
export OPENROUTER_API_KEY=your-api-key-here
export KEY_FINDINGS_DB_PATH=./data/key_findings.db
```

3. **Run the application**:

```bash
python app.py
```

## 🔧 Configuration Options

### Database Configuration

| Parameter                   | Default                      | Description               |
| --------------------------- | ---------------------------- | ------------------------- |
| `KEY_FINDINGS_DB_PATH`      | `/app/data/key_findings.db`  | Database file path        |
| `KEY_FINDINGS_BACKUP_PATH`  | `/app/data/backups/`         | Backup directory          |
| `KEY_FINDINGS_VOLUME_MOUNT` | `/var/lib/key_findings_data` | Docker volume mount point |

### AI Configuration

| Parameter            | Default                                                                        | Description           |
| -------------------- | ------------------------------------------------------------------------------ | --------------------- |
| `OPENROUTER_API_KEY` | Required                                                                       | OpenRouter.ai API key |
| `PRIMARY_MODEL`      | `openai/gpt-4o-mini`                                                           | Primary AI model      |
| `FALLBACK_MODELS`    | `nvidia/llama-3.1-nemotron-70b-instruct,meta-llama/llama-3.1-8b-instruct:free` | Fallback models       |

### Analysis Parameters

| Parameter                           | Default | Range       | Description                |
| ----------------------------------- | ------- | ----------- | -------------------------- |
| `KEY_FINDINGS_PCA_WEIGHT`           | `0.3`   | 0.0-1.0     | PCA emphasis weight        |
| `KEY_FINDINGS_CONFIDENCE_THRESHOLD` | `0.7`   | 0.0-1.0     | Minimum confidence score   |
| `KEY_FINDINGS_MAX_TOKENS`           | `4000`  | 1000-8000   | Maximum AI response tokens |
| `KEY_FINDINGS_CACHE_TTL`            | `86400` | 3600-604800 | Cache TTL in seconds       |
| `KEY_FINDINGS_MAX_HISTORY`          | `100`   | 10-1000     | Maximum history entries    |

## 🧪 Testing

### Unit Tests

Run the comprehensive test suite:

```bash
cd dashboard_app
python -m pytest tests/test_key_findings.py -v
```

### Integration Tests

Test the complete workflow:

```bash
# Test database operations
python -c "
from key_findings.database_manager import KeyFindingsDBManager
db = KeyFindingsDBManager('./test.db')
print(f'Database initialized: {db.verify_persistence()}')
"

# Test AI service
python -c "
import asyncio
from key_findings.ai_service import OpenRouterService
async def test():
    service = OpenRouterService('your-api-key')
    result = await service.test_model_availability()
    print(f'Model availability: {result}')
asyncio.run(test())
"
```

### Manual Testing

1. **Start the application**
2. **Select a management tool** from the dropdown
3. **Select data sources** (at least one)
4. **Click "🧠 Generar Key Findings"**
5. **Verify the modal opens** with AI-generated content
6. **Test caching** by closing and reopening the same analysis
7. **Test regeneration** by clicking "Regenerar"

## 🔍 Troubleshooting

### Common Issues

#### 1. Module Import Errors

```
ImportError: No module named 'key_findings'
```

**Solution**: Ensure you're running from the `dashboard_app` directory

#### 2. Database Connection Errors

```
sqlite3.OperationalError: unable to open database file
```

**Solution**: Check directory permissions and paths

#### 3. API Key Issues

```
Error: Invalid API key
```

**Solution**: Verify your OpenRouter.ai API key is valid and has credits

#### 4. Docker Volume Issues

```
Permission denied: /app/data/key_findings.db
```

**Solution**: Ensure proper volume mounting and permissions

#### 5. Cache Not Working

```
Cache miss every time
```

**Solution**: Check database path and permissions

### Debug Mode

Enable debug logging:

```env
KEY_FINDINGS_DEBUG=true
```

This will provide detailed logs for:

- Database operations
- AI API calls
- Cache operations
- Performance metrics

## 📊 Performance Monitoring

### Metrics Available

The Key Findings module tracks:

- **Cache Hit Rate**: Percentage of requests served from cache
- **Response Time**: AI API response times
- **Error Rate**: Percentage of failed requests
- **Database Size**: Storage usage
- **Model Performance**: Per-model success rates

### Accessing Metrics

1. **Via Dashboard**: Performance section shows real-time metrics
2. **Via API**: `/health` endpoint includes performance data
3. **Via Database**: Direct query to `model_performance` table

### Performance Optimization

- **Cache Hit Rate Target**: >80%
- **Response Time Target**: <3 seconds
- **Error Rate Target**: <5%

## 🚀 Production Deployment

### Security Considerations

1. **API Key Security**:

   - Use environment variables, not hard-coded keys
   - Rotate API keys regularly
   - Monitor API usage

2. **Database Security**:

   - Regular backups
   - Access logging
   - File permissions

3. **Container Security**:
   - Non-root user
   - Resource limits
   - Health checks

### Scaling Considerations

1. **Horizontal Scaling**:

   - Shared database volume
   - Load balancer configuration
   - Session affinity

2. **Vertical Scaling**:
   - Memory allocation
   - CPU allocation
   - Storage I/O

### Monitoring Setup

1. **Health Checks**:

   ```bash
   curl http://localhost:8050/health
   ```

2. **Log Aggregation**:

   - Application logs
   - Database logs
   - AI service logs

3. **Alerting**:
   - High error rates
   - Low cache hit rates
   - API quota exceeded

## 📚 Advanced Configuration

### Custom Models

Add custom AI models:

```python
from key_findings.ai_service import OpenRouterService

service = OpenRouterService(api_key, {
    'models': [
        'openai/gpt-4o-mini',
        'your-custom-model',
        'another-custom-model'
    ],
    'timeout': 60,
    'max_retries': 5
})
```

### Custom Prompts

Modify analysis prompts:

```python
from key_findings.prompt_engineer import PromptEngineer

engineer = PromptEngineer('es')
engineer.prompt_templates['comprehensive_analysis'] = """
Your custom prompt template here...
"""
```

### Database Optimization

SQLite optimization settings:

```python
from key_findings.database_manager import KeyFindingsDBManager

db = KeyFindingsDBManager(db_path)
db.connection.execute("PRAGMA journal_mode = WAL")
db.connection.execute("PRAGMA synchronous = NORMAL")
db.connection.execute("PRAGMA cache_size = 10000")
```

## 🆘 Support

### Getting Help

1. **Documentation**: Check all `KEY_FINDINGS_*.md` files
2. **Issues**: Create GitHub issues with:
   - Error messages
   - Configuration details
   - Steps to reproduce
3. **Community**: Join discussions for tips and tricks

### Contributing

1. **Fork the repository**
2. **Create feature branch**
3. **Make changes**
4. **Add tests**
5. **Submit pull request**

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Application starts without errors
- [ ] Key Findings button appears in sidebar
- [ ] Modal opens when button clicked
- [ ] AI analysis generates successfully
- [ ] Cache works across page reloads
- [ ] Performance metrics are tracked
- [ ] Database persists across restarts
- [ ] Docker volumes are properly mounted
- [ ] Health check endpoint responds
- [ ] Logs are being generated

## 🎉 Next Steps

Once setup is complete:

1. **Explore Features**: Try different tools and data sources
2. **Monitor Performance**: Check cache hit rates and response times
3. **Customize**: Adjust prompts and models for your needs
4. **Scale**: Deploy to production with proper monitoring
5. **Contribute**: Help improve the module

---

**🚀 Your Key Findings module is ready for doctoral-level analysis!**

For additional support, see the [Complete Implementation Guide](KEY_FINDINGS_COMPLETE_GUIDE.md) or [Architecture Documentation](KEY_FINDINGS_ARCHITECTURE.md).
