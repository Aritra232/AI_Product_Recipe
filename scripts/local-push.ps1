param(
    [string]$Message = "Update AI search service",
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

Set-Location (Resolve-Path "$PSScriptRoot\..")

Write-Host "Checking repository safety..."

if (git ls-files --error-unmatch .env 2>$null) {
    Write-Error ".env is tracked by Git. Remove it first with: git rm --cached .env"
}

if (git ls-files --error-unmatch Service/data/search_index.json 2>$null) {
    Write-Host "Removing generated search index from Git tracking..."
    git rm --cached Service/data/search_index.json
}

if (Get-Command git-lfs -ErrorAction SilentlyContinue) {
    git lfs untrack "Service/data/search_index.json" | Out-Null
}

git add .gitignore .gitattributes README.md Dockerfile docker-compose.yml .env.example main.py requirements.txt Service scripts

$status = git status --porcelain
if (-not $status) {
    Write-Host "No changes to commit."
} else {
    git commit -m $Message
}

git push origin $Branch

Write-Host "Push complete."

