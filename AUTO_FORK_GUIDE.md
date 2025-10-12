# Automated Fork and Setup Guide

## 🚀 Complete Automated Fork Workflow

This guide helps you use the [`auto_fork_and_setup.sh`](auto_fork_and_setup.sh) script to completely automate the Git fork process, including creating the fork via GitHub API and pushing all changes.

## 📋 Prerequisites

### Required Tools

- **Git** - For version control
- **curl** - For GitHub API requests
- **jq** - For JSON parsing (GitHub API responses)

### Install Dependencies

```bash
# macOS
brew install git curl jq

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install git curl jq

# CentOS/RHEL
sudo yum install git curl jq
```

### GitHub Token Setup

You need a GitHub Personal Access Token with `repo` scope:

1. **Generate Token**:

   - Visit https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control of private repositories)
   - Generate and copy the token

2. **Set Token Environment Variable** (recommended):

   ```bash
   export GITHUB_TOKEN="your_token_here"
   ```

3. **Or save to file**:
   ```bash
   echo "your_token_here" > ~/.github_token
   chmod 600 ~/.github_token
   ```

## 🔧 Usage

### Basic Usage

```bash
# Interactive mode (will prompt for username and token)
./auto_fork_and_setup.sh

# With username as argument
./auto_fork_and_setup.sh your_github_username

# With token pre-set
GITHUB_TOKEN="your_token" ./auto_fork_and_setup.sh your_username
```

### Example Execution

```bash
# Set your token
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

# Run the script
./auto_fork_and_setup.sh johndoe
```

## 🔄 What the Script Does

### 1. **Fork Creation via API**

- Automatically creates a fork of `Wise-Connex/Management-Tools-Analysis`
- Waits for the fork to be ready
- Handles existing forks gracefully

### 2. **Repository Setup**

- Clones your forked repository
- Adds upstream remote to original repository
- Creates and switches to `feature/key-findings-module` branch
- Syncs with upstream main branch

### 3. **Module Structure Creation**

- Creates complete `dashboard_app/key_findings/` directory structure
- Adds placeholder implementations for all module components
- Sets up test directory structure
- Creates necessary `__init__.py` files

### 4. **Dependencies and Configuration**

- Updates `requirements.txt` with new dependencies
- Adds comprehensive environment variables to `.env.example`
- Configures all necessary settings for Key Findings module

### 5. **Git Operations**

- Configures Git user if needed
- Commits all changes with descriptive message
- Pushes to your fork's feature branch

## 📁 Expected Results

After execution, you'll have:

```
Management-Tools-Analysis/
├── dashboard_app/
│   ├── key_findings/             # Complete module structure
│   │   ├── __init__.py
│   │   ├── database_manager.py   # Placeholder implementation
│   │   ├── ai_service.py         # Placeholder implementation
│   │   ├── data_aggregator.py    # Placeholder implementation
│   │   ├── prompt_engineer.py    # Placeholder implementation
│   │   ├── modal_component.py    # Placeholder implementation
│   │   ├── dashboard_integration.py  # Placeholder implementation
│   │   └── config.py             # Configuration class
│   ├── tests/                    # Test structure
│   │   ├── test_key_findings.py  # Unit tests
│   │   └── test_integration.py   # Integration tests
│   ├── requirements.txt          # Updated with new deps
│   └── .env.example             # Updated with Key Findings config
├── auto_fork_and_setup.sh        # The automation script
└── AUTO_FORK_GUIDE.md            # This guide
```

## 🔍 Verification

### Verify Fork Creation

```bash
# Check your fork on GitHub
# Visit: https://github.com/YOUR_USERNAME/Management-Tools-Analysis
```

### Verify Local Repository

```bash
cd Management-Tools-Analysis

# Check remotes
git remote -v
# Should show both origin (your fork) and upstream (original)

# Check branch
git branch
# Should show * feature/key-findings-module

# Check module structure
ls -la dashboard_app/key_findings/
```

### Verify Git History

```bash
# Check commit history
git log --oneline -n 3

# Check that files were committed
git show --name-only HEAD
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. "GitHub token is required"

**Solution**: Set the `GITHUB_TOKEN` environment variable or create `~/.github_token`

#### 2. "Failed to create fork. Check your token and permissions"

**Solution**:

- Verify your token has `repo` scope
- Check that you haven't exceeded API rate limits
- Ensure your GitHub account has fork permissions

#### 3. "jq is not installed"

**Solution**: Install jq using your package manager (see prerequisites)

#### 4. "Fork might still be processing"

**Solution**: This is normal - GitHub sometimes takes time to process forks. The script will continue anyway.

#### 5. "Permission denied (publickey)"

**Solution**: The script uses HTTPS with token authentication, so SSH keys aren't needed.

### Debug Mode

To debug issues, you can run the script with verbose output:

```bash
bash -x ./auto_fork_and_setup.sh your_username
```

### Manual Recovery

If the script fails, you can manually complete the setup:

```bash
# Clone your fork manually
git clone https://github.com/YOUR_USERNAME/Management-Tools-Analysis.git
cd Management-Tools-Analysis

# Add upstream
git remote add upstream https://github.com/Wise-Connex/Management-Tools-Analysis.git

# Create feature branch
git checkout -b feature/key-findings-module

# Run the original setup script
../setup_key_findings_fork.sh
```

## 🔄 Daily Workflow

### Syncing with Upstream

```bash
cd Management-Tools-Analysis
git fetch upstream
git checkout main
git merge upstream/main
git checkout feature/key-findings-module
git merge main
git push origin feature/key-findings-module
```

### Making Changes

```bash
# Make your changes
git add .
git commit -m "feat: implement database manager"
git push origin feature/key-findings-module
```

## 📝 Environment Variables

The script configures these environment variables in `.env.example`:

```bash
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
```

## 🎯 Next Steps

After successful automation:

1. **Implement the module components** replacing placeholders with actual code
2. **Configure your API keys** in `.env` file
3. **Test locally** following the testing guide
4. **Create a pull request** when implementation is complete

## 🚀 Advanced Usage

### Custom Branch Name

To use a custom branch name, modify the script:

```bash
# Change this line in the script
FEATURE_BRANCH="feature/your-custom-branch"
```

### Custom Repository

To fork a different repository, modify the script:

```bash
# Change this line in the script
ORIGINAL_REPO="owner/repo-name"
```

### Batch Operations

The script can be used in CI/CD pipelines for automated repository setup:

```yaml
# GitHub Actions example
- name: Setup fork
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    ./auto_fork_and_setup.sh ${{ github.actor }}
```

---

**🎉 Ready to go!** Your complete automated fork workflow is ready. Run the script and start developing the Key Findings module immediately! 🚀
