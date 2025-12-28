# 🌍 Campus Carbon Pulse

**AI-Powered Digital Twin for Campus Carbon Footprint Monitoring**

A real-time 3D visualization dashboard that uses LSTM neural networks to predict and monitor carbon emissions across campus buildings over a 24-hour period.

![Campus Carbon Pulse](https://img.shields.io/badge/Status-Active-success)
![React](https://img.shields.io/badge/React-18.3-blue)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)

---

## 🎯 Features

- **🤖 LSTM-Based Forecasting**: 24-hour carbon emission predictions using trained neural networks
- **🗺️ Interactive 3D Map**: Real-time campus visualization with color-coded heat levels
- **📊 Live Dashboard**: Dynamic metrics showing total campus emissions
- **⏱️ Time Slider**: Explore emissions across different hours of the day
- **🎨 Modern UI**: Glassmorphic design with smooth animations

---

## 🏗️ Tech Stack

### **Frontend**
- **React 18** + **TypeScript**
- **Vite** (build tool)
- **MapLibre GL** (3D mapping)
- **Tailwind CSS** (styling)
- **shadcn/ui** (components)

### **Backend**
- **FastAPI** (Python web framework)
- **TensorFlow/Keras** (LSTM models)
- **Pandas** (data processing)
- **Uvicorn** (ASGI server)

---

## 📦 Installation

### **Prerequisites**
- Node.js 18+ and npm
- Python 3.8+
- Git

### **1. Clone the Repository**
```bash
git clone <your-repo-url>
cd campus-carbon-pulse-main
```

### **2. Frontend Setup**
```bash
# Install dependencies
npm install

# Start development server (runs on http://localhost:8080)
npm run dev
```

### **3. Backend Setup**
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server (runs on http://localhost:8000)
python -m uvicorn main:app --reload --port 8000
```

---

## 🚀 Usage

1. **Start the backend server** (port 8000)
2. **Start the frontend dev server** (port 8080)
3. **Open browser** to `http://localhost:8080`
4. **Interact with the map**:
   - Move the time slider to see emissions at different hours
   - Click buildings to view detailed metrics
   - Watch colors change based on predicted emissions

---

## 📁 Project Structure

```
campus-carbon-pulse-main/
├── backend/
│   ├── models/              # Trained LSTM models (*.keras)
│   ├── main.py              # FastAPI server
│   ├── forecast.py          # LSTM prediction logic
│   ├── emissions.json       # 24-hour forecast data
│   ├── campus.json          # GeoJSON building data
│   └── requirements.txt     # Python dependencies
├── src/
│   ├── components/          # React components
│   ├── pages/               # Page components
│   ├── lib/                 # Utility functions
│   └── types/               # TypeScript types
├── public/
│   └── campus.json          # Static GeoJSON data
├── package.json             # Node dependencies
└── vite.config.ts           # Vite configuration
```

---

## 🧠 How It Works

1. **Data Collection**: Historical campus energy consumption data (CSV)
2. **Model Training**: LSTM models trained per building to learn usage patterns
3. **Forecasting**: `forecast.py` generates 24-hour predictions → `emissions.json`
4. **API**: FastAPI serves predictions via `/get-emissions/{hour}` endpoint
5. **Visualization**: React frontend fetches data and updates 3D map colors in real-time

---

## 🎨 Color Scale

Buildings are color-coded based on emission levels:
- 🟢 **Green** (0-33%): Low emissions
- 🟡 **Yellow** (34-66%): Moderate emissions
- 🔴 **Red** (67-100%): High emissions

---

## 📊 API Endpoints

### `GET /get-emissions/{hour}`
Returns emission predictions for a specific hour (0-23).

**Response:**
```json
{
  "hour": 10,
  "results": [
    {
      "building_id": "Academic_Block_Large",
      "total_emission": 110.77,
      "scaled_emission": 70.5
    }
  ]
}
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👨‍💻 Author

Built with ❤️ for sustainable campus management

---

## 🙏 Acknowledgments

- Campus energy data provided by [Your Institution]
- 3D mapping powered by MapLibre GL
- ML models built with TensorFlow/Keras
