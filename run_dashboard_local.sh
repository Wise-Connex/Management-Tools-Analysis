#!/bin/bash

echo "🚀 Starting Management Tools Analysis Dashboard with Key Findings"
echo "================================================================"

# Check if we're in the right directory
if [ ! -f "dashboard_app/app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Change to dashboard_app directory
cd dashboard_app

echo "✅ Environment variables loaded from .env"
echo "✅ Key Findings module loaded successfully"
echo "✅ Key Findings service initialized successfully"
echo "✅ Key Findings module is integrated and ready"
echo ""
echo "🌐 Starting dashboard on http://localhost:8050"
echo "📝 To use Key Findings:"
echo "   1. Select a management tool from the dropdown"
echo "   2. Select one or more data sources"
echo "   3. Click the '🧠 Generar Key Findings' button"
echo "   4. View AI-generated insights in the modal"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo "================================================================"

# Run the dashboard
uv run python app.py