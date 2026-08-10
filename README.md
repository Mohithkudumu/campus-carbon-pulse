# 🌿 Campus Carbon Pulse

**AI-Powered Digital Twin for Campus Carbon Footprint Monitoring**

> A real-time 3D visualization system using LSTM neural networks to predict, monitor, and alert on carbon emissions across all campus buildings — with AI-generated sustainability insights powered by Google Gemini.

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![React](https://img.shields.io/badge/React-18.3-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey)

---

## 🎯 What is this project?

Campus Carbon Pulse is a **digital twin** for Shiv Nadar University's physical campus. It continuously:

- **Predicts** next 24-hour carbon emissions for every building using LSTM models trained on a year of historical energy data
- **Visualizes** emissions live on a 3D interactive map — buildings turn green, yellow, or red based on their predicted output
- **Alerts** sustainability managers when a building is projected to cross critical emission thresholds
- **Recommends** corrective actions using AI (Google Gemini) based on real emission patterns

The goal is to give campus administrators an at-a-glance tool to identify emission hotspots, optimize energy usage, and work toward carbon neutrality in measurable steps.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗺️ **3D Interactive Map** | Buildings rendered in 3D via MapLibre GL. Color changes dynamically based on emission level (green → yellow → red) |
| ⏱️ **24-Hour Time Slice** | Drag a slider to see how emissions change hour by hour across the entire campus |
| 📉 **LSTM Forecasting** | Per-building LSTM models (trained on `snuc_carbon_year_2025.csv`) predict the next 24 hours of carbon output |
| 📊 **Carbon Analytics Panel** | Total campus kg/h readout, trend vs. historical average, and historical area chart (7D / 30D / 6M) |
| 🔔 **Anomaly Alerts** | Automated warnings when any building's predicted emission exceeds safety thresholds. CRITICAL / HIGH severity |
| ✅ **Resolve Alerts** | Sustainability managers can mark alerts as resolved directly from the dashboard |
| 🤖 **AI Insights (Gemini)** | One-click AI-generated reports with peak hour analysis, building rankings, trends, and actionable recommendations. Cached daily to save API quota |
| 💾 **SQLite Persistence** | All forecasts, alerts, and AI cache are persisted in a local SQLite database for fast retrieval |

---

## 🏗️ Architecture & Flow

```
┌──────────────────────────────────────────────────────────────┐
│  Browser  →  http://localhost:8080                            │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  React + Vite Frontend                              │    │
│  │  CampusMap.tsx   → 3D MapLibre map                  │    │
│  │  AnalyticsPanel  → Metrics + Charts + AlertsBell    │    │
│  │  TimeSlider      → Controls forecast hour           │    │
│  │  Insights page   → AI sustainability report         │    │
│  └──────────────┬──────────────────────────────────────┘    │
└─────────────────┼────────────────────────────────────────────┘
                  │  HTTP (CORS)
                  ▼
┌──────────────────────────────────────────────────────────────┐
│  FastAPI Backend  →  http://localhost:8000                    │
│                                                              │
│  main.py          → API routes + startup logic               │
│  forecast.py      → LSTM 24h prediction engine               │
│  database.py      → SQLite helpers (init, connect)           │
│  insights.py      → Legacy insights helper                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SQLite  →  database.db                              │   │
│  │  • predicted_emissions   (building, timestamp, kg)   │   │
│  │  • peak_alerts           (severity, resolved flag)   │   │
│  │  • cached_insights       (date_key, Gemini JSON)     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  models/   → 12 × LSTM (.keras) + 12 × Scaler (.joblib)     │
│  snuc_carbon_year_2025.csv  → 1-year training dataset        │
└──────────────────────────────────────────────────────────────┘
```

**Startup flow:**
1. FastAPI starts → `init_db()` creates all SQLite tables if absent
2. `generate_24h_forecast_json()` runs automatically → loads each LSTM model, predicts 24h values, saves to `emissions.json` and `database.db`
3. Any building exceeding carbon thresholds → an alert row is inserted into `peak_alerts`
4. Frontend polls `/get-emissions/{hour}` as user drags the time slider

---

## 🗂️ Project Structure

```
campus-carbon-pulse-main/
│
├── 📁 backend/                      # Python FastAPI application
│   ├── main.py                      # All API routes + startup + GeoJSON injector
│   ├── forecast.py                  # LSTM 24-hour forecasting engine
│   ├── database.py                  # SQLite schema definitions and connection helpers
│   ├── insights.py                  # (Legacy) standalone insights helper
│   ├── emissions.json               # Generated 24h forecast data (auto-written)
│   ├── campus.json                  # Building GeoJSON (auto-updated with live data)
│   ├── snuc_carbon_year_2025.csv    # 1-year historical energy dataset
│   ├── database.db                  # SQLite database (auto-created on startup)
│   ├── requirements.txt             # Python dependencies
│   │
│   ├── 📁 models/                   # Per-building trained artifacts
│   │   ├── lstm_<Building>.keras    # LSTM model weights (12 buildings)
│   │   └── scaler_<Building>.joblib # Min-max scaler per building
│   │
│   ├── 📁 notebooks/                # Jupyter notebooks (model training)
│   │   └── LSTM.ipynb
│   │
│   └── 📁 diagnostics/              # Ad-hoc analysis & testing scripts
│       ├── test_db_endpoints.py     # Full integration test suite
│       ├── check_emissions.py       # Compare forecast vs. training data
│       ├── analyze_patterns.py      # Hostel hourly pattern analysis
│       ├── analyze_5pm.py           # 5PM building emission breakdown
│       ├── simple_check.py          # Quick spot-check script
│       └── analysis_output.txt      # Output from analysis run
│
├── 📁 src/                          # React + TypeScript frontend
│   ├── 📁 components/
│   │   ├── CampusMap.tsx            # MapLibre 3D map renderer
│   │   ├── AnalyticsPanel.tsx       # Right sidebar: metrics + chart + bell
│   │   ├── AlertsBell.tsx           # Alert notification popover
│   │   ├── TimeSlider.tsx           # Bottom time-range slider
│   │   ├── DashboardHeader.tsx      # Top-left campus header
│   │   └── InsightCard.tsx          # AI insight card renderer
│   │
│   ├── 📁 pages/
│   │   ├── Index.tsx                # Main dashboard page
│   │   └── Insights.tsx             # AI insights page
│   │
│   ├── 📁 lib/
│   │   ├── mockData.ts              # Fallback data helpers
│   │   └── utils.ts                 # Utility functions (cn, etc.)
│   │
│   └── 📁 types/
│       └── campus.ts                # Campus GeoJSON TypeScript types
│
├── 📁 public/
│   └── campus.json                  # Static GeoJSON served to the browser
│
├── package.json                     # Node.js dependencies
├── vite.config.ts                   # Vite dev server config (port 8080)
├── tailwind.config.ts               # Tailwind CSS configuration
├── SETUP_GUIDE.md                   # Full setup & troubleshooting guide
└── README.md                        # This file
```

---

## 🌐 API Reference

All endpoints are served at `http://localhost:8000`.  
Interactive docs: **http://localhost:8000/docs**

### `GET /get-emissions/{hour}`
Returns LSTM-forecast emission data for all buildings at a given hour.

| Param | Type | Description |
|---|---|---|
| `hour` | int (0–23) | Target hour of the day |

```json
{
  "hour": 17,
  "results": [
    { "building_id": "Academic_Block_Large", "total_emission": 115.4, "scaled_emission": 74.2 },
    { "building_id": "Large_Hostel_Boys",    "total_emission": 88.2,  "scaled_emission": 52.1 }
  ]
}
```

---

### `GET /get-historical-data/{days}`
Returns daily average campus emissions for the past N days (used by the area chart).

| Param | Type | Description |
|---|---|---|
| `days` | int (1–365) | Number of past days to fetch |

```json
{
  "days": 7,
  "data": [
    { "date": "Aug 04", "carbon": 412.3, "buildings": 12 },
    { "date": "Aug 05", "carbon": 398.7, "buildings": 12 }
  ]
}
```

---

### `GET /get-alerts`
Returns all **unresolved** peak emission warnings sorted by most recent.

```json
[
  {
    "id": 42,
    "building_id": "Large_Hostel_Girls",
    "timestamp": "2026-08-10 21:00:00",
    "emission": 158.3,
    "limit_value": 120.0,
    "alert_msg": "Building Large_Hostel_Girls predicted to hit carbon peak of 158.30 kg CO2e (scaled 96.2%).",
    "severity": "CRITICAL",
    "resolved": 0
  }
]
```

---

### `POST /resolve-alert/{alert_id}`
Marks a specific alert as resolved in the database.

```json
{ "success": true, "message": "Alert 42 marked as resolved" }
```

---

### `GET /get-insights`
Returns AI-generated campus sustainability insights (cached daily via SQLite).

```json
{
  "success": true,
  "cached": false,
  "insights": {
    "summary": "...",
    "categories": [
      { "type": "peak_hours", "title": "Peak Emission Periods", "items": [...] },
      { "type": "buildings",  "title": "Building Analysis",     "items": [...] },
      { "type": "trends",     "title": "Emission Trends",       "items": [...] },
      { "type": "recommendations", "title": "Recommended Actions", "items": [...] }
    ]
  }
}
```

---

## 🗄️ Database Schema

**`predicted_emissions`** — Stores LSTM forecasts generated on each server start
| Column | Type | Description |
|---|---|---|
| `building_id` | TEXT | Building name identifier |
| `timestamp` | TEXT | Forecast datetime (YYYY-MM-DD HH:MM:SS) |
| `emission` | REAL | Predicted kg CO₂e |
| `scaled_emission` | REAL | Normalized 0–100 scale |

**`peak_alerts`** — Tracks anomalous emission events
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-increment primary key |
| `building_id` | TEXT | Building that triggered the alert |
| `emission` | REAL | Predicted emission value |
| `limit_value` | REAL | Threshold that was exceeded (120 kg) |
| `severity` | TEXT | `CRITICAL` or `HIGH` |
| `resolved` | INTEGER | `0` = active, `1` = resolved |

**`cached_insights`** — Daily AI insight cache
| Column | Type | Description |
|---|---|---|
| `date_key` | TEXT | Date string (YYYY-MM-DD), primary key |
| `insights_json` | TEXT | Full Gemini response stored as JSON string |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Map** | MapLibre GL JS | 3D building extrusion and color rendering |
| **Frontend** | React 18 + TypeScript | UI components and state management |
| **Build** | Vite 5 | Fast HMR dev server (port 8080) |
| **Styling** | Tailwind CSS + shadcn/ui | Glassmorphic dark-mode design system |
| **Charts** | Recharts | Historical emission area charts |
| **HTTP** | Axios / Fetch API | API calls to FastAPI backend |
| **Backend** | FastAPI + Uvicorn | Async Python REST API (port 8000) |
| **ML** | TensorFlow / Keras (LSTM) | Per-building time-series forecasting |
| **Data** | Pandas | CSV preprocessing and date filtering |
| **Database** | SQLite | Forecast persistence, alerts, AI cache |
| **AI** | Google Gemini 2.5 Flash | Sustainability insights generation |

---

## 🚀 Quick Start

```bash
# 1. Clone and install frontend
git clone <repo-url> && cd campus-carbon-pulse-main
npm install

# 2. Set up backend
cd backend
python -m venv venv
venv\Scripts\activate         # Windows
# source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt

# 3. Configure API key
echo GEMINI_API_KEY=your_key_here > .env

# 4. Run both servers (separate terminals)
# Terminal 1 - Backend:
python -m uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend:
cd ..
npm run dev
```

Open **http://localhost:8080** in your browser.

> 📖 Full setup instructions and troubleshooting: see [SETUP_GUIDE.md](./SETUP_GUIDE.md)

---

## 📈 Buildings Monitored

| Building | Category |
|---|---|
| Academic_Block_Large | Academic |
| Academic_Block_Small | Academic |
| Library | Academic |
| Large_Hostel_Boys | Residential |
| Large_Hostel_Girls | Residential |
| Small_Hostel_Boys | Residential |
| Small_Hostel_Girls | Residential |
| Boys_Mess | Dining |
| Girls_Mess | Dining |
| Canteen | Dining |
| Clinic | Utility |
| Sports_Complex | Recreational |

---

Built with ❤️ by the GDG team for sustainable campus management at Shiv Nadar University.
