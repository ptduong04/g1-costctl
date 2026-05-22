#!/bin/bash
# Script to push costctl to your GitHub

# INSTRUCTIONS:
# 1. Create a new repo on GitHub: https://github.com/new
#    - Name: g<N>-costctl (replace <N> with your group number)
#    - Public
#    - DO NOT initialize with README
# 2. Replace <USERNAME> and <N> below with your values
# 3. Run this script: bash push-to-github.sh

USERNAME="<YOUR_GITHUB_USERNAME>"
GROUP_NUMBER="<YOUR_GROUP_NUMBER>"
REPO_NAME="g${GROUP_NUMBER}-costctl"

echo "Pushing to: https://github.com/${USERNAME}/${REPO_NAME}"
echo ""

# Remove old remote
git remote remove origin

# Add new remote
git remote add origin "https://github.com/${USERNAME}/${REPO_NAME}.git"

# Stage all changes
git add .

# Commit
git commit -m "implement costctl - 25/25 tests passing

- list: EC2/RDS/S3/Volume with tag filtering
- terminate: safe resource deletion
- clean: bulk cleanup with dry-run
- cost: Cost Explorer integration
- tag: multi-resource tagging

All 25 tests passing."

# Push to GitHub
git push -u origin main

# Create and push tag
git tag w6-sidechallenge-v1
git push --tags

echo ""
echo "✅ Done! Your repo is now at:"
echo "https://github.com/${USERNAME}/${REPO_NAME}"
echo ""
echo "Next: Post in Slack #w6-sidechallenge:"
echo "G${GROUP_NUMBER} — https://github.com/${USERNAME}/${REPO_NAME} — 25/25 tests passing — implemented: list, terminate, clean, cost, tag"
