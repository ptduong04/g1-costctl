@echo off
REM Script to push costctl to your GitHub (Windows)

REM INSTRUCTIONS:
REM 1. Create a new repo on GitHub: https://github.com/new
REM    - Name: g<N>-costctl (replace <N> with your group number)
REM    - Public
REM    - DO NOT initialize with README
REM 2. Edit this file and replace <USERNAME> and <N> below
REM 3. Run this script: push-to-github.bat

SET USERNAME=<YOUR_GITHUB_USERNAME>
SET GROUP_NUMBER=<YOUR_GROUP_NUMBER>
SET REPO_NAME=g%GROUP_NUMBER%-costctl

echo Pushing to: https://github.com/%USERNAME%/%REPO_NAME%
echo.

REM Remove old remote
git remote remove origin

REM Add new remote
git remote add origin https://github.com/%USERNAME%/%REPO_NAME%.git

REM Stage all changes
git add .

REM Commit
git commit -m "implement costctl - 25/25 tests passing"

REM Push to GitHub
git push -u origin main

REM Create and push tag
git tag w6-sidechallenge-v1
git push --tags

echo.
echo Done! Your repo is now at:
echo https://github.com/%USERNAME%/%REPO_NAME%
echo.
echo Next: Post in Slack #w6-sidechallenge:
echo G%GROUP_NUMBER% — https://github.com/%USERNAME%/%REPO_NAME% — 25/25 tests passing — implemented: list, terminate, clean, cost, tag

pause
