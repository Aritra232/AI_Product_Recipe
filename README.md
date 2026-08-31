# Tomatoes With Lemon AI Search Service

FastAPI service for correcting website search terms from CMS CSV exports.

Example:

```text
psti -> Pasta
pickled Daikn -> Pickled Daikon and Carrots
glutn-free -> Gluten Free
```

The service reads CSV files from `Service/CSV`, builds `Service/data/search_index.json`, and uses OpenAI embeddings when rebuilding the index.

## Requirements

- Python 3.11+
- OpenAI API key

## Environment

Create `.env` from `.env.example`:

```powershell
copy .env.example .env
```

Then set:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

## Run Locally

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 7011 --reload
```

Open:

```text
http://127.0.0.1:7011/docs
```

## Endpoints

Health:

```http
GET /health
```

Search:

```http
GET /search?q=psti
```

Response:

```json
{
  "query": "psti",
  "match": "Pasta"
}
```

Import or rebuild CSV index:

```http
POST /admin/import-csv
```

Upload rules:

- 0 files: rebuilds using existing CSV files in `Service/CSV`
- 1 to 8 files: saves uploaded CSV files, then rebuilds the index
- More than 8 files: returns a validation error

Use `multipart/form-data` with key `files` when uploading CSV files.

## Run With Docker

Build and start:

```powershell
docker compose up --build
```

Open:

```text
http://127.0.0.1:7011/docs
```

Rebuild index after changing CSV files:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:7011/admin/import-csv
```

## GitHub And VPS Workflow

Do not push these files:

```text
.env
Service/data/search_index.json
venv/
__pycache__/
```

The large `Service/data/search_index.json` file is generated from CSV files on the server.

Safe local push:

```powershell
.\scripts\local-push.ps1 -Message "Update AI search service"
```

VPS deploy after pushing:

```bash
cd /var/www/AI_Product_Recipe
chmod +x scripts/vps-deploy.sh
./scripts/vps-deploy.sh
```

Optional one-time VPS auto-deploy hook:

```bash
cd /var/www/AI_Product_Recipe
chmod +x scripts/install-vps-auto-deploy.sh
./scripts/install-vps-auto-deploy.sh
```

After this, future VPS updates only need:

```bash
git pull
```

The Git hook will automatically run Docker rebuild/restart and regenerate the search index.

The deploy script will:

- pull latest code from GitHub
- create a valid empty index if needed
- rebuild and restart Docker
- call `/admin/import-csv`
- regenerate `Service/data/search_index.json` on the VPS
