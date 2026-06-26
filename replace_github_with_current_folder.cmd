@echo off
setlocal

cd /d "%~dp0"

set "REPO_URL=https://github.com/chunyi-mitust/Ministry-of-Education-s-Interpretation-on-Gender-Equality.md.git"
set "BRANCH=main"

echo.
echo === Replace GitHub repo with current folder ===
echo Current folder: %CD%
echo Target repo: %REPO_URL%
echo.
echo WARNING: This script treats the current folder as the source of truth.
echo Files that exist on GitHub but not in this folder will be removed from GitHub.
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
echo Staging current folder...
git add --all

git diff --cached --quiet
if errorlevel 1 (
  git commit -m "Replace GitHub with current database"
) else (
  echo No new changes to commit.
)

echo.
echo Force uploading current folder to GitHub...
git push --force -u origin %BRANCH%
if errorlevel 1 (
  echo.
  echo Upload failed. Common causes:
  echo 1. You are not signed in to GitHub.
  echo 2. Your GitHub account does not have write access to this repository.
  echo 3. GitHub asks you to sign in with a browser or a Personal Access Token.
  echo 4. Branch protection on GitHub blocks force pushes.
  echo.
  echo After fixing the login, access, or branch protection issue, run this file again.
  pause
  exit /b 1
)

echo.
echo Done. GitHub now matches the current folder:
echo %REPO_URL%
pause
