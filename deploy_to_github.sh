#!/bin/bash

echo "🚀 Deploying Interactive Intake Chatbot to GitHub..."
echo "================================================"

echo ""
echo "📁 Initializing Git repository..."
git init

echo ""
echo "📋 Adding all files to Git..."
git add .

echo ""
echo "💾 Creating initial commit..."
git commit -m "🤖 Add Interactive Intake Chatbot System with GPT-4o mini

✨ Features:
- AI-powered conversational intake forms
- Dual communication modes (formal/casual)
- Multi-organization support with authentication
- Admin portal with form management
- Real-time validation and help system
- Export capabilities (CSV/JSON)
- Streamlit Cloud ready deployment

🏢 Sample Organizations:
- Broomfield Department of Health
- First Things First
- Gateway YMCA  
- SBNJ Mobile Midwife Clinic

🔧 Tech Stack:
- Streamlit + Python
- OpenAI GPT-4o mini
- Pandas for data processing
- Role-based authentication"

echo ""
echo "🌐 Setting up remote repository..."
git branch -M main
git remote add origin https://github.com/monjil99/Unite-Us-Demo-Chatbot.git

echo ""
echo "⬆️ Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Deployment to GitHub complete!"
echo ""
echo "🎯 Next Steps:"
echo "1. Go to https://share.streamlit.io"
echo "2. Create new app with your repository"
echo "3. Add OpenAI API key to secrets"
echo "4. Deploy to Streamlit Cloud!"
echo ""
echo "📖 Repository: https://github.com/monjil99/Unite-Us-Demo-Chatbot"
echo ""
read -p "Press any key to continue..."
