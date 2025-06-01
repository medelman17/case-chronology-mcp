#!/bin/bash
# Push to GitHub after creating the repository

# Add the remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/medelman17/case-chronology-mcp.git

# Push to GitHub
git branch -M main
git push -u origin main

echo "✅ Successfully pushed to GitHub!"