# News Recommendation System

A FastAPI service that finds similar news articles using Sentence Transformer embeddings and a FAISS index.

## Project structure

```text
app/
  __init__.py
  main.py
  recommender.py
  benchmark.py
data/
  news_rec_embeddings.faiss
  news_articles.parquet
.env.example
requirements.txt
README.md
```

## Environment variables

Copy `.env.example` to `.env` and adjust as needed:

| Variable | Default | Description |
|---|---|---|
| `MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | Sentence Transformer model |
| `FAISS_INDEX_PATH` | `data/news_rec_embeddings.faiss` | Path to FAISS index |
| `ARTICLES_PATH` | `data/news_articles.parquet` | Path to article metadata |
| `TOP_K` | `5` | Default number of recommendations |

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
```

## Run

```powershell
uvicorn app.main:app --reload
```

API docs available at `http://127.0.0.1:8000/docs`.

## Endpoints

- `GET /health` - Service health and asset status
- `POST /recommend` - Get similar articles

```json
{
  "query": "BlackBerry smartphone business",
  "k": 5
}
```
