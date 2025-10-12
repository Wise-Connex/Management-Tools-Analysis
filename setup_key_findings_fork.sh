#!/bin/bash
# setup_key_findings_fork.sh

set -e

echo "🍴 Key Findings Module - Fork Setup Script"
echo "=========================================="

# Configuration
ORIGINAL_REPO="Wise-Connex/Management-Tools-Analysis"
YOUR_USERNAME=${1:-"YOUR_USERNAME"}
REPO_NAME="Management-Tools-Analysis"

# Step 1: Fork the repository (manual step)
echo "📋 Step 1: Fork the repository"
echo "Please visit: https://github.com/${ORIGINAL_REPO}"
echo "Click 'Fork' button and select your account"
echo "Press Enter to continue..."
read

# Step 2: Clone your fork
echo "📥 Step 2: Cloning your fork..."
if [ -d "$REPO_NAME" ]; then
    echo "Repository already exists. Updating..."
    cd "$REPO_NAME"
    git pull origin main
else
    git clone "https://github.com/${YOUR_USERNAME}/${REPO_NAME}.git"
    cd "$REPO_NAME"
fi

# Step 3: Add upstream remote
echo "🔗 Step 3: Adding upstream remote..."
git remote add upstream "https://github.com/${ORIGINAL_REPO}.git" || echo "Upstream remote already exists"

# Step 4: Create feature branch
echo "🌿 Step 4: Creating feature branch..."
git checkout -b feature/key-findings-module || git checkout feature/key-findings-module

# Step 5: Create module structure
echo "📁 Step 5: Creating Key Findings module structure..."
mkdir -p dashboard_app/key_findings
mkdir -p dashboard_app/tests

# Create __init__.py files
touch dashboard_app/key_findings/__init__.py

# Step 6: Update requirements
echo "📦 Step 6: Updating requirements..."
echo "aiohttp>=3.8.0" >> dashboard_app/requirements.txt
echo "asyncio-throttle>=1.0.2" >> dashboard_app/requirements.txt

# Step 7: Create .env.example updates
echo "⚙️ Step 7: Updating environment configuration..."
cat >> dashboard_app/.env.example << EOF

# Key Findings Configuration
OPENROUTER_API_KEY=your_api_key_here
KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
KEY_FINDINGS_BACKUP_PATH=/app/data/backups/
KEY_FINDINGS_BACKUP_INTERVAL=3600
KEY_FINDINGS_DATA_DIR=/app/data
KEY_FINDINGS_VOLUME_MOUNT=/var/lib/key_findings_data
KEY_FINDINGS_CACHE_TTL=86400
KEY_FINDINGS_MAX_HISTORY=100
KEY_FINDINGS_AUTO_GENERATE=true
KEY_FINDINGS_MAX_DATA_POINTS=10000
KEY_FINDINGS_PCA_WEIGHT=0.3
KEY_FINDINGS_CONFIDENCE_THRESHOLD=0.7
KEY_FINDINGS_ANONYMIZE_DATA=true
KEY_FINDINGS_MAX_TOKENS=4000
PRIMARY_MODEL=openai/gpt-4o-mini
FALLBACK_MODELS=nvidia/llama-3.1-nemotron-70b-instruct,meta-llama/llama-3.1-8b-instruct:free
EOF

# Step 8: Initial commit
echo "💾 Step 8: Making initial commit..."
git add .
git commit -m "feat: create Key Findings module structure and dependencies"

# Step 9: Push to fork
echo "📤 Step 9: Pushing to your fork..."
git push -u origin feature/key-findings-module

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Copy implementation code from KEY_FINDINGS_IMPLEMENTATION_PLAN.md"
echo "2. Follow the implementation phases in KEY_FINDINGS_GIT_WORKFLOW.md"
echo "3. Test your implementation locally"
echo "4. Create a pull request when ready"
echo ""
echo "📁 Project structure created at: $(pwd)"
echo "🌿 Current branch: $(git branch --show-current)"
echo "🔗 Your fork: https://github.com/${YOUR_USERNAME}/${REPO_NAME}"