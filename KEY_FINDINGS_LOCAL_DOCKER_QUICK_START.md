# 🚀 Key Findings Local Docker Quick Start

## Overview

This guide helps you deploy the Key Findings module locally using Docker without requiring sudo permissions. The setup includes persistent storage, automatic backups, and all the AI-powered analysis features.

## Prerequisites

- Docker installed and running
- Docker Compose installed
- OpenRouter.ai API key (get one at [openrouter.ai](https://openrouter.ai/))

## Quick Start (3 Steps)

### 1. Configure API Key

Edit the `.env` file:

```bash
# If .env doesn't exist, it will be created automatically
nano dashboard_app/.env
```

Add your API key:

````env
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
The deployment script automatically handles API key configuration:

**Option A: If you have a root .env file with your API key**
- The script will automatically detect and copy your API key to `dashboard_app/.env`
- No manual configuration needed

**Option B: Manual configuration**
```bash
# Edit the dashboard_app .env file
nano dashboard_app/.env
````

Add your API key:

```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
```

````

### 2. Run Deployment Script

```bash
# Make the script executable (if not already done)
chmod +x deploy_key_findings_local.sh

# Run the deployment
./deploy_key_findings_local.sh
````

### 3. Access the Application

Open your browser and navigate to:

```
http://localhost:8050
```

## What the Script Does

✅ **Automatic Setup**:

- Creates necessary directories (`./data`, `./logs`)
- Sets proper permissions (no sudo required)
- Creates Docker Compose override for local development
- Builds and starts containers

✅ **Persistent Storage**:

- Database: `./data/key_findings.db`
- Backups: `./data/backups/`
- Logs: `./logs/`

✅ **Health Checks**:

- Verifies application is running
- Tests API endpoints
- Provides troubleshooting tips

## Using Key Findings

1. **Select a Tool**: Choose from the dropdown (e.g., "Cuadro de Mando Integral")
2. **Select Data Sources**: Click the source buttons (Google Trends, Crossref, etc.)
3. **Generate Analysis**: Click the "🧠 Generar Key Findings" button
4. **View Results**: The AI analysis appears in a modal with:
   - Executive summary
   - Principal findings with reasoning
   - PCA insights
   - Performance metrics

## Common Commands

```bash
# View logs
docker-compose logs -f dashboard-app

# Stop the application
docker-compose down

# Restart the application
docker-compose restart

# Rebuild with latest changes
docker-compose build --no-cache && docker-compose up -d
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8050
lsof -i :8050

# Kill the process
kill -9 <PID>
```

### API Key Issues

- Ensure your API key is valid and has credits
- Check the `.env` file for typos
- Verify network connectivity

### Permission Issues

The script handles permissions automatically, but if you encounter issues:

```bash
# Fix directory permissions
chmod -R 755 ./data ./logs
```

### Application Won't Start

```bash
# Check container logs
docker-compose logs dashboard-app

# Rebuild from scratch
docker-compose down
docker system prune -f
./deploy_key_findings_local.sh
```

## Features Available

🤖 **AI-Powered Analysis**:

- Doctoral-level insights using OpenRouter.ai
- Fallback models for reliability
- Intelligent caching to reduce costs

📊 **Advanced Analytics**:

- PCA emphasis and interpretation
- Multi-source data synthesis
- Statistical summaries and trends

🌐 **Bilingual Support**:

- Complete Spanish/English interface
- Localized AI responses
- Cultural adaptation

💾 **Persistent Storage**:

- Zero data loss across restarts
- Automatic hourly backups
- Performance tracking

## Next Steps

1. **Explore the Dashboard**: Try different tools and data source combinations
2. **Test Key Findings**: Generate AI analyses for various scenarios
3. **Check Performance**: Monitor cache hit rates and response times
4. **Review Documentation**: See `KEY_FINDINGS_COMPLETE_GUIDE.md` for advanced features

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the logs: `docker-compose logs dashboard-app`
3. Consult the complete documentation in the project

---

**🎉 Your Key Findings module is now running locally with Docker!**
