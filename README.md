# 🎬📚 Hybrid Recommendation System

An end-to-end ML project that recommends movies and books based on free-text user interests using a **hybrid recommendation engine** (content-based + collaborative filtering).

## Architecture

```
User Input (text)
       │
       ▼
┌─────────────────────────────────────────┐
│           FastAPI Backend               │
│                                         │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │ Content-Based│  │  Collaborative  │  │
│  │  TF-IDF +    │  │  SVD Matrix     │  │
│  │  Cosine Sim  │  │  Factorization  │  │
│  └──────┬───────┘  └────────┬────────┘  │
│         │    Hybrid Scorer  │           │
│         └────────┬──────────┘           │
│              Weighted Blend             │
│           (α·content + β·collab)        │
└─────────────────┬───────────────────────┘
                  │
                  ▼
         React Frontend UI
```

## ML Pipeline

| Stage | Technology |
|-------|-----------|
| Text vectorization | TF-IDF (sklearn) |
| Content similarity | Cosine similarity |
| Collaborative filtering | SVD (scipy / surprise) |
| Hybrid blending | Weighted score fusion |
| Model serialization | joblib |
| Experiment tracking | MLflow |
| API | FastAPI |
| Frontend | React + Vite |

## Project Structure

```
recommender/
├── backend/
│   ├── data/
│   │   ├── movies.csv          # MovieLens / TMDB enriched dataset
│   │   └── books.csv           # Goodreads dataset
│   ├── scripts/
│   │   ├── prepare_data.py     # Data cleaning & preprocessing
│   │   └── train.py            # Train & serialize models
│   ├── models/                 # Saved .pkl / .joblib files
│   ├── api/
│   │   ├── main.py             # FastAPI app
│   │   ├── recommender.py      # Hybrid recommendation logic
│   │   └── schemas.py          # Pydantic models
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/              # Page views
│   │   └── hooks/              # Custom React hooks
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── mlflow/                     # MLflow tracking uri
└── README.md
```

## Quickstart

### 1. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Prepare data
```bash
python scripts/prepare_data.py
```

### 3. Train models
```bash
python scripts/train.py
```

### 4. Start API
```bash
uvicorn api.main:app --reload --port 8000
```

### 5. Start frontend
```bash
cd frontend
npm install && npm run dev
```

### Or use Docker Compose
```bash
docker-compose up --build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/recommend` | Get hybrid recommendations |
| GET | `/health` | Health check |
| GET | `/model/info` | Model metadata & metrics |

## Datasets

- **Movies:** [MovieLens 25M](https://grouplens.org/datasets/movielens/) — 25M ratings, 62K movies
- **Books:** [Goodreads Dataset](https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks) — 10K books with ratings

## MLflow Tracking

Run the MLflow UI to view experiments:
```bash
mlflow ui --port 5000
```
