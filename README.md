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
python -m uvicorn main:app --host 127.0.0.1 --port 8005 --reload
```

Open:

```text
http://127.0.0.1:8005/docs
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
http://127.0.0.1:8005/docs
```

Rebuild index after changing CSV files:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8005/admin/import-csv
```

