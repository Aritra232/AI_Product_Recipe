from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from Service.config import CSV_DIR, INDEX_PATH
from Service.search_index import SearchIndex


app = FastAPI(title="Tomatoes With Lemon AI Search", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_index = SearchIndex(INDEX_PATH)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "index_exists": INDEX_PATH.exists(),
        "terms": len(search_index.terms),
        "embedded_terms": search_index.embedded_terms_count(),
    }


@app.post("/admin/import-csv")
async def import_csv(
    files: Optional[list[UploadFile]] = File(default=None),
):
    if files:
        if len(files) > 8:
            raise HTTPException(
                status_code=400,
                detail="You can upload a maximum of 8 CSV files",
            )

        CSV_DIR.mkdir(parents=True, exist_ok=True)
        for file in files:
            if not file.filename or not file.filename.lower().endswith(".csv"):
                raise HTTPException(status_code=400, detail="Only CSV files are allowed")

            destination = CSV_DIR / Path(file.filename).name
            content = await file.read()
            destination.write_bytes(content)

    if not list(CSV_DIR.glob("*.csv")):
        raise HTTPException(status_code=400, detail="No CSV files found to import")

    summary = search_index.rebuild_from_csv_dir(CSV_DIR)
    return {
        "status": "indexed",
        "csv_files": len(list(CSV_DIR.glob("*.csv"))),
        **summary,
    }


@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    return search_index.search(q)
