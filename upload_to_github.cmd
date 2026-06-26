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
echo Syncing latest changes from GitHub...
git fetch origin %BRANCH%
if errorlevel 1 (
  echo.
  echo Could not fetch the latest GitHub branch.
  echo Please check your network connection, GitHub login, and repository access.
  pause
  exit /b 1
)

git rebase origin/%BRANCH%
if errorlevel 1 (
  echo.
  echo GitHub has changes that could not be merged automatically.
  echo Please ask Codex to help resolve the Git rebase conflict, then run this file again.
  pause
  exit /b 1
)

echo.
echo Uploading to GitHub...
git push -u origin %BRANCH%
if errorlevel 1 (
  echo.
  echo Upload failed. Common causes:
  echo 1. You are not signed in to GitHub.
  echo 2. Your GitHub account does not have write access to this repository.
  echo 3. GitHub asks you to sign in with a browser or a Personal Access Token.
  echo 4. The remote branch changed again while this script was running.
  echo.
  echo After fixing the login or access issue, run this file again.
  pause
  exit /b 1
)

echo.
echo Done. Uploaded to:
echo %REPO_URL%
pause
