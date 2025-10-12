#!/bin/bash
# auto_fork_and_setup.sh - Complete automated fork and setup workflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ORIGINAL_REPO="Wise-Connex/Management-Tools-Analysis"
REPO_NAME="Management-Tools-Analysis"
DEFAULT_BRANCH="main"
FEATURE_BRANCH="feature/key-findings-module"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed. Please install curl first."
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        print_error "jq is not installed. Please install jq first."
        exit 1
    fi
    
    print_success "All dependencies are available"
}

# Function to get GitHub token
get_github_token() {
    if [[ -n "$GITHUB_TOKEN" ]]; then
        echo "$GITHUB_TOKEN"
    elif [[ -f "$HOME/.github_token" ]]; then
        cat "$HOME/.github_token"
    else
        echo -n "Enter your GitHub token: "
        read -s token
        echo
        echo "$token"
    fi
}

# Function to create fork via GitHub API
create_fork() {
    local username="$1"
    local token="$2"
    
    print_status "Creating fork via GitHub API..."
    
    # Check if fork already exists
    local fork_check=$(curl -s -H "Authorization: token $token" \
        "https://api.github.com/repos/$username/$REPO_NAME" \
        -w "%{http_code}" -o /dev/null)
    
    if [[ "$fork_check" == "200" ]]; then
        print_warning "Fork already exists at https://github.com/$username/$REPO_NAME"
        return 0
    fi
    
    # Create fork
    local response=$(curl -s -X POST \
        -H "Authorization: token $token" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$ORIGINAL_REPO/forks")
    
    local fork_url=$(echo "$response" | jq -r '.html_url')
    
    if [[ "$fork_url" == "null" ]]; then
        print_error "Failed to create fork. Check your token and permissions."
        echo "Response: $response"
        exit 1
    fi
    
    print_success "Fork created at $fork_url"
    
    # Wait for fork to be ready
    print_status "Waiting for fork to be ready..."
    sleep 5
    
    # Verify fork is ready
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        local status=$(curl -s -H "Authorization: token $token" \
            "https://api.github.com/repos/$username/$REPO_NAME" \
            | jq -r '.status')
        
        if [[ "$status" == "\"\"" ]] || [[ "$status" == "null" ]]; then
            print_success "Fork is ready"
            break
        fi
        
        print_status "Attempt $attempt/$max_attempts: Fork not ready yet, waiting..."
        sleep 2
        ((attempt++))
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        print_warning "Fork might still be processing, but continuing anyway..."
    fi
}

# Function to setup repository
setup_repository() {
    local username="$1"
    local token="$2"
    
    print_status "Setting up repository..."
    
    # Clone or update repository
    if [[ -d "$REPO_NAME" ]]; then
        print_status "Repository exists, updating..."
        cd "$REPO_NAME"
        git fetch origin
        git checkout "$DEFAULT_BRANCH"
        git pull origin "$DEFAULT_BRANCH"
    else
        print_status "Cloning forked repository..."
        git clone "https://$username:$token@github.com/$username/$REPO_NAME.git"
        cd "$REPO_NAME"
    fi
    
    # Add upstream remote
    if ! git remote | grep -q "upstream"; then
        git remote add upstream "https://github.com/$ORIGINAL_REPO.git"
        print_success "Added upstream remote"
    else
        print_status "Upstream remote already exists"
    fi
    
    # Fetch from upstream
    git fetch upstream
    
    # Create and switch to feature branch
    if git show-ref --verify --quiet "refs/heads/$FEATURE_BRANCH"; then
        print_status "Feature branch already exists, switching to it..."
        git checkout "$FEATURE_BRANCH"
        git merge upstream/"$DEFAULT_BRANCH" || true
    else
        print_status "Creating feature branch..."
        git checkout -b "$FEATURE_BRANCH" upstream/"$DEFAULT_BRANCH"
    fi
    
    print_success "Repository setup complete"
}

# Function to create module structure
create_module_structure() {
    print_status "Creating Key Findings module structure..."
    
    # Create directories
    mkdir -p dashboard_app/key_findings
    mkdir -p dashboard_app/tests
    mkdir -p dashboard_app/data
    
    # Create __init__.py files
    touch dashboard_app/key_findings/__init__.py
    
    # Create placeholder files for the module
    cat > dashboard_app/key_findings/database_manager.py << 'EOF'
"""
Database Manager for Key Findings Module
Handles persistent storage and caching of analysis results
"""

class KeyFindingsDBManager:
    """Database manager for Key Findings with persistent storage"""
    
    def __init__(self, db_path):
        self.db_path = db_path
    
    def verify_persistence(self):
        """Verify that persistent storage is working"""
        return True
EOF

    cat > dashboard_app/key_findings/ai_service.py << 'EOF'
"""
AI Service for Key Findings Module
Handles OpenRouter.ai integration and AI analysis
"""

class AIService:
    """AI service for generating Key Findings analysis"""
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def generate_analysis(self, data):
        """Generate AI-powered analysis"""
        return "AI analysis placeholder"
EOF

    cat > dashboard_app/key_findings/data_aggregator.py << 'EOF'
"""
Data Aggregator for Key Findings Module
Processes and aggregates data for analysis
"""

class DataAggregator:
    """Data aggregator for Key Findings analysis"""
    
    def process_data(self, data):
        """Process data for analysis"""
        return data
EOF

    cat > dashboard_app/key_findings/prompt_engineer.py << 'EOF'
"""
Prompt Engineer for Key Findings Module
Handles AI prompt generation and optimization
"""

class PromptEngineer:
    """Prompt engineer for AI analysis"""
    
    def generate_prompt(self, context):
        """Generate optimized prompt for AI"""
        return "Analysis prompt placeholder"
EOF

    cat > dashboard_app/key_findings/modal_component.py << 'EOF'
"""
Modal Component for Key Findings Module
UI component for displaying Key Findings
"""

class ModalComponent:
    """Modal UI component for Key Findings"""
    
    def render(self, data):
        """Render modal with Key Findings"""
        return "Modal HTML placeholder"
EOF

    cat > dashboard_app/key_findings/dashboard_integration.py << 'EOF'
"""
Dashboard Integration for Key Findings Module
Integrates Key Findings with main dashboard
"""

class DashboardIntegration:
    """Dashboard integration for Key Findings"""
    
    def integrate(self, app):
        """Integrate Key Findings with dashboard"""
        pass
EOF

    cat > dashboard_app/key_findings/config.py << 'EOF'
"""
Configuration for Key Findings Module
Handles module configuration and settings
"""

class Config:
    """Configuration class for Key Findings"""
    
    OPENROUTER_API_KEY = ""
    DB_PATH = "/app/data/key_findings.db"
    CACHE_TTL = 86400
EOF

    # Create test files
    cat > dashboard_app/tests/test_key_findings.py << 'EOF'
"""
Test suite for Key Findings Module
"""

import unittest

class TestKeyFindings(unittest.TestCase):
    """Test cases for Key Findings module"""
    
    def test_database_manager(self):
        """Test database manager"""
        from key_findings.database_manager import KeyFindingsDBManager
        db = KeyFindingsDBManager("/tmp/test.db")
        self.assertTrue(db.verify_persistence())
    
    def test_ai_service(self):
        """Test AI service"""
        from key_findings.ai_service import AIService
        ai = AIService("test_key")
        result = ai.generate_analysis({})
        self.assertIsInstance(result, str)

if __name__ == "__main__":
    unittest.main()
EOF

    cat > dashboard_app/tests/test_integration.py << 'EOF'
"""
Integration tests for Key Findings Module
"""

import unittest

class TestIntegration(unittest.TestCase):
    """Integration tests for Key Findings"""
    
    def test_full_workflow(self):
        """Test complete workflow"""
        self.assertTrue(True)  # Placeholder

if __name__ == "__main__":
    unittest.main()
EOF

    print_success "Module structure created"
}

# Function to update dependencies
update_dependencies() {
    print_status "Updating dependencies..."
    
    # Add new dependencies to requirements.txt
    if [[ -f "dashboard_app/requirements.txt" ]]; then
        grep -q "aiohttp" dashboard_app/requirements.txt || echo "aiohttp>=3.8.0" >> dashboard_app/requirements.txt
        grep -q "asyncio-throttle" dashboard_app/requirements.txt || echo "asyncio-throttle>=1.0.2" >> dashboard_app/requirements.txt
    else
        echo "aiohttp>=3.8.0" > dashboard_app/requirements.txt
        echo "asyncio-throttle>=1.0.2" >> dashboard_app/requirements.txt
    fi
    
    print_success "Dependencies updated"
}

# Function to update environment configuration
update_environment_config() {
    print_status "Updating environment configuration..."
    
    # Add Key Findings configuration to .env.example
    cat >> dashboard_app/.env.example << 'EOF'

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

    print_success "Environment configuration updated"
}

# Function to commit and push changes
commit_and_push() {
    local username="$1"
    local token="$2"
    
    print_status "Committing and pushing changes..."
    
    # Configure git if not configured
    if ! git config user.name &> /dev/null; then
        echo -n "Enter your Git name: "
        read git_name
        git config user.name "$git_name"
    fi
    
    if ! git config user.email &> /dev/null; then
        echo -n "Enter your Git email: "
        read git_email
        git config user.email "$git_email"
    fi
    
    # Add all changes
    git add .
    
    # Commit changes
    git commit -m "feat: create Key Findings module structure and dependencies

- Add complete module structure with placeholder implementations
- Update dependencies with aiohttp and asyncio-throttle
- Configure environment variables for Key Findings
- Add test suite structure
- Prepare for AI-powered analysis implementation"

    # Push to fork
    git push "https://$username:$token@github.com/$username/$REPO_NAME.git" "$FEATURE_BRANCH"
    
    print_success "Changes committed and pushed to fork"
}

# Function to display final instructions
display_instructions() {
    local username="$1"
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📁 Repository location: $(pwd)"
    echo "🌿 Current branch: $(git branch --show-current)"
    echo "🔗 Your fork: https://github.com/$username/$REPO_NAME"
    echo ""
    echo "📋 Next steps:"
    echo "1. Implement the module components in dashboard_app/key_findings/"
    echo "2. Follow KEY_FINDINGS_IMPLEMENTATION_PLAN.md for detailed implementation"
    echo "3. Test your implementation locally"
    echo "4. Create a pull request when ready"
    echo ""
    echo "🔄 To sync with upstream in the future:"
    echo "   git fetch upstream"
    echo "   git checkout main"
    echo "   git merge upstream/main"
    echo "   git checkout $FEATURE_BRANCH"
    echo "   git merge main"
    echo ""
    echo "🚀 Happy coding!"
}

# Main execution
main() {
    echo "🍴 Auto Fork and Setup for Key Findings Module"
    echo "=============================================="
    echo ""
    
    # Check dependencies
    check_dependencies
    
    # Get GitHub username
    if [[ -n "$1" ]]; then
        username="$1"
    else
        echo -n "Enter your GitHub username: "
        read username
    fi
    
    # Get GitHub token
    token=$(get_github_token)
    
    if [[ -z "$token" ]]; then
        print_error "GitHub token is required"
        exit 1
    fi
    
    # Execute workflow
    create_fork "$username" "$token"
    setup_repository "$username" "$token"
    create_module_structure
    update_dependencies
    update_environment_config
    commit_and_push "$username" "$token"
    display_instructions "$username"
}

# Run main function with all arguments
main "$@"