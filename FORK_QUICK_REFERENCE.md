# Fork Workflow Quick Reference

## 🚀 One-Command Fork Setup

### Automated Complete Fork

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Run complete automated fork
./auto_fork_and_setup.sh your_github_username
```

### Manual Fork Setup

```bash
# Manual fork + automated setup
./setup_key_findings_fork.sh your_github_username
```

## 📋 Prerequisites Checklist

- [ ] **GitHub Token** with `repo` scope
- [ ] **Git** installed
- [ ] **curl** installed
- [ ] **jq** installed

### Install Dependencies

```bash
# macOS
brew install git curl jq

# Ubuntu/Debian
sudo apt-get install git curl jq

# CentOS/RHEL
sudo yum install git curl jq
```

## 🔧 GitHub Token Setup

### Option 1: Environment Variable

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
```

### Option 2: File

```bash
echo "your_token_here" > ~/.github_token
chmod 600 ~/.github_token
```

## 📁 Expected Results

```
Management-Tools-Analysis/
├── dashboard_app/
│   ├── key_findings/             # 🆕 Complete module
│   ├── tests/                    # 🆕 Test suite
│   ├── requirements.txt          # 🔄 Updated
│   └── .env.example             # 🔄 Updated
├── feature/key-findings-module   # 🌿 Active branch
└── remotes configured            # 🔗 origin + upstream
```

## 🔍 Verification Commands

```bash
# Check remotes
git remote -v

# Check branch
git branch

# Check module structure
ls -la dashboard_app/key_findings/

# Check commit history
git log --oneline -n 3
```

## 🔄 Daily Workflow

### Sync with Upstream

```bash
git fetch upstream
git checkout main
git merge upstream/main
git checkout feature/key-findings-module
git merge main
git push origin feature/key-findings-module
```

### Commit Changes

```bash
git add .
git commit -m "feat: your change description"
git push origin feature/key-findings-module
```

## 🛠️ Troubleshooting

### Token Issues

```bash
# Test token
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/user
```

### Fork Already Exists

```bash
# Script handles this automatically
# Will continue with existing fork
```

### Permission Issues

```bash
# Check token permissions
# Ensure token has 'repo' scope
```

## 📝 Environment Variables

Key variables added to `.env.example`:

```bash
OPENROUTER_API_KEY=your_api_key_here
KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
PRIMARY_MODEL=openai/gpt-4o-mini
# ... and more
```

## 🎯 Next Steps

1. **Implement module components** in `dashboard_app/key_findings/`
2. **Configure API keys** in your `.env` file
3. **Test locally** with `python -m pytest tests/`
4. **Create pull request** when ready

## 📚 Full Documentation

- [`AUTO_FORK_GUIDE.md`](AUTO_FORK_GUIDE.md) - Complete automated guide
- [`KEY_FINDINGS_FORK_EXECUTION_GUIDE.md`](KEY_FINDINGS_FORK_EXECUTION_GUIDE.md) - Manual fork guide
- [`KEY_FINDINGS_GIT_WORKFLOW.md`](KEY_FINDINGS_GIT_WORKFLOW.md) - Complete workflow
- [`git_workflow_validation.md`](git_workflow_validation.md) - Validation checklist

---

**🚀 Ready to develop!** Your fork is set up and ready for Key Findings module development.
