@echo off
setlocal

cd /d "%~dp0"

set "REPO_URL=https://github.com/chunyi-mitust/Ministry-of-Education-s-Interpretation-on-Gender-Equality.md.git"
set "BRANCH=main"

echo.
echo === Upload database to GitHub ===
echo Current folder: %CD%
echo Target repo: %REPO_URL%
echo.

git --version >nul 2>&1
if errorlevel 1 (
  echo Git was not found. Please install Git for Windows first:
  echo https://git-scm.com/download/win
  pause
  exit /b 1
)

if not exist ".git" (
  echo This folder is not a Git repository yet. Initializing...
  git init
)

git branch -M %BRANCH%

git remote get-url origin >nul 2>&1
if errorlevel 1 (
  git remote add origin "%REPO_URL%"
) else (
  git remote set-url origin "%REPO_URL%"
)

echo.
echo Staging files...
git add --all

git diff --cached --quiet
if errorlevel 1 (
  git commit -m "Sync latest database files"
) else (
  echo No new changes to commit.
)

echo.
echo Uploading to GitHub...
git push -u origin %BRANCH%
if errorlevel 1 (
  echo.
  echo Upload failed. Common causes:
  echo 1. The GitHub repository has not been created yet.
  echo 2. You are not signed in to GitHub.
  echo 3. Your GitHub account does not have write access to this repository.
  echo 4. GitHub asks you to sign in with a browser or a Personal Access Token.
  echo.
  echo After fixing the GitHub setting or login, run this file again.
  pause
  exit /b 1
)

echo.
echo Done. Uploaded to:
echo %REPO_URL%
pause
