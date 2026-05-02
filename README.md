# Sports Match Predictor

A machine learning web app that predicts cricket and football match outcomes using real match data.

- **Cricket** — predicts the winner of an ODI match based on 1st innings performance (72% accuracy)
- **Football** — predicts Premier League match result: Home Win / Draw / Away Win (45% accuracy)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS v4 |
| Backend | Python, Flask, Flask-CORS |
| ML | scikit-learn (RandomForest), pandas, joblib |
| Cricket data | Cricsheet.org — free public zip download, no API key needed |
| Football data | football-data.org — requires free API key |
| Live scores (planned) | Cricbuzz via RapidAPI — key stored, not yet integrated |
| Scheduler | APScheduler (monthly auto-retrain) |
| Deployment | AWS (planned) |

---

## Project Structure

```
sports-predictor/
├── backend/
│   ├── app.py                  # Flask app entry point
│   ├── config.py               # Environment config
│   ├── scheduler.py            # Monthly retrain scheduler
│   ├── routes/
│   │   ├── cricket.py          # POST /api/predict/cricket
│   │   ├── football.py         # POST /api/predict/football
│   │   └── admin.py            # POST /api/admin/retrain, GET /api/admin/status
│   ├── src/
│   │   ├── data_collector.py   # Fetch & parse raw data
│   │   ├── feature_engineer.py # Build model features
│   │   ├── train_cricket.py    # Train cricket model
│   │   ├── train_football.py   # Train football model
│   │   ├── predictor.py        # Load models & run predictions
│   │   └── retrain.py          # Full monthly retrain pipeline
│   ├── models/                 # Saved .pkl model files (gitignored)
│   └── data/                   # Raw & processed data (gitignored)
└── frontend/
    ├── src/
    │   ├── App.jsx             # Tab navigation (Cricket / Football)
    │   ├── api.js              # Axios API calls
    │   └── components/
    │       ├── CricketForm.jsx
    │       ├── FootballForm.jsx
    │       ├── PredictionResult.jsx
    │       └── ErrorMessage.jsx
    └── .env                    # VITE_API_URL
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### 1. Clone the repo

```bash
git clone https://github.com/your-username/sports-predictor.git
cd sports-predictor
```

### 2. Backend setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```env
FOOTBALL_API_KEY=your_football_data_org_key   # required for football data fetch
DEBUG=True
PORT=5000
```

> **Cricket data requires no API key.** It is downloaded automatically from [cricsheet.org](https://cricsheet.org) as a free public zip file.

### 3. Build the data pipeline (first time only)

**Cricket data** — download the ODI CSV zip manually from [cricsheet.org/downloads](https://cricsheet.org/downloads/) and extract the CSV files into `backend/data/raw/`. No API key needed, it is a free public download.

**Football data** — fetched automatically from football-data.org using your API key.

```bash
# Parses cricket CSVs from data/raw/ + fetches football matches from API
python src/data_collector.py

# Build model features from raw data
python src/feature_engineer.py

# Train both models — saves .pkl files to models/
python src/train_cricket.py
python src/train_football.py
```

> After the first setup, monthly retraining (`POST /api/admin/retrain`) handles everything automatically — including re-downloading the latest cricket zip from cricsheet.org.

### 4. Start the backend

```bash
python app.py
```

Flask runs at `http://localhost:5000`

### 5. Frontend setup

```bash
cd ../frontend
npm install
npm run dev
```

React runs at `http://localhost:5173`

---

## API Reference

### Predict cricket match

```
POST /api/predict/cricket
```

```json
{
  "team1": "India",
  "team2": "Australia",
  "inn1_runs": 287,
  "inn1_wickets": 6,
  "inn1_balls": 300
}
```

**Response:**
```json
{
  "winner": "India",
  "win_probability": 74.4,
  "team1": "India",
  "team2": "Australia"
}
```

---

### Predict football match

```
POST /api/predict/football
```

```json
{
  "home_team": "Arsenal FC",
  "away_team": "Chelsea FC",
  "matchday": 10
}
```

**Response:**
```json
{
  "result": "Home Win",
  "home_win_prob": 45.0,
  "draw_prob": 21.6,
  "away_win_prob": 33.4,
  "home_team": "Arsenal FC",
  "away_team": "Chelsea FC"
}
```

---

### Manual retrain

```
POST /api/admin/retrain
```

Triggers the full pipeline in the background:
1. Downloads latest ODI zip from cricsheet.org (free, no key)
2. Fetches current PL season from football-data.org (needs `FOOTBALL_API_KEY`)
3. Re-engineers features from all data
4. Retrains both models
5. Hot-reloads models into Flask (no restart needed)

```
GET /api/admin/status
```

Returns last retrain time, accuracy for both models, and full retrain history.

---

## Automated Monthly Retraining

The app automatically retrains both models on the **1st of every month at 02:00 UTC** using APScheduler.

Each retrain logs:
- Date and time
- Number of matches used
- Model accuracy (cricket & football)
- Any errors

Logs are stored in `backend/data/retrain_log.json` (last 24 runs).

---

## Supported Teams

**Cricket (28 teams):** Australia, India, England, Pakistan, South Africa, New Zealand, Sri Lanka, West Indies, Bangladesh, Afghanistan, Zimbabwe, Ireland, and more.

**Football (20 Premier League teams):** Arsenal FC, Chelsea FC, Liverpool FC, Manchester City FC, Manchester United FC, Tottenham Hotspur FC, and all other 2023/24 PL clubs.

---

## Model Details

| Model | Algorithm | Features | Accuracy |
|---|---|---|---|
| Cricket | RandomForest (100 trees) | Team encodings, inn1 runs, wickets, balls | 72% |
| Football | RandomForest (100 trees) | Team codes, matchday, rolling 5-match avg goals | 45% |

Football accuracy is typical — even professional models rarely exceed 55% for 3-class prediction (H/D/A).

---

## License

MIT
