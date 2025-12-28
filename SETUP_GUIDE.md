# 🚀 Campus Carbon Pulse - Complete Setup Guide

This guide will walk you through setting up and running the Campus Carbon Pulse project from scratch.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### **Required Software:**
1. **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
2. **Python** (v3.8 or higher) - [Download here](https://www.python.org/downloads/)
3. **Git** (optional, for cloning) - [Download here](https://git-scm.com/)

### **Verify Installation:**
Open a terminal/command prompt and run:
```bash
node --version    # Should show v18.x.x or higher
npm --version     # Should show 9.x.x or higher
python --version  # Should show 3.8.x or higher
```

---

## 📥 Step 1: Get the Project Files

### **Option A: Clone from GitHub**
```bash
git clone <repository-url>
cd campus-carbon-pulse-main
```

### **Option B: Download ZIP**
1. Download the ZIP file
2. Extract it to your desired location
3. Open terminal/command prompt in the extracted folder

---

## 🎨 Step 2: Setup Frontend (React + Vite)

### **2.1 Install Dependencies**
```bash
# Make sure you're in the project root directory
npm install
```

This will install all required packages (React, Vite, MapLibre, etc.). It may take 2-3 minutes.

### **2.2 Verify Installation**
Check that `node_modules/` folder was created in your project root.

---

## 🐍 Step 3: Setup Backend (Python + FastAPI)

### **3.1 Navigate to Backend Directory**
```bash
cd backend
```

### **3.2 Create Virtual Environment**

**On Windows:**
```bash
python -m venv venv
```

**On macOS/Linux:**
```bash
python3 -m venv venv
```

### **3.3 Activate Virtual Environment**

**On Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**On Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

### **3.4 Install Python Dependencies**
```bash
pip install -r requirements.txt
```

This installs FastAPI, TensorFlow, Pandas, etc. May take 3-5 minutes.

### **3.5 Verify Backend Files**
Ensure these files exist in the `backend/` folder:
- ✅ `main.py`
- ✅ `forecast.py`
- ✅ `emissions.json`
- ✅ `campus.json`
- ✅ `models/` folder with `.keras` files

---

## ▶️ Step 4: Run the Application

You need **TWO terminal windows** running simultaneously.

### **Terminal 1: Start Backend Server**

```bash
# Navigate to backend folder (if not already there)
cd backend

# Activate virtual environment (if not already activated)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Start FastAPI server
python -m uvicorn main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Backend is now running on http://localhost:8000**

---

### **Terminal 2: Start Frontend Server**

Open a **NEW terminal window** (keep the backend running):

```bash
# Navigate to project root (NOT backend folder)
cd campus-carbon-pulse-main

# Start Vite dev server
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in 500 ms

  ➜  Local:   http://localhost:8080/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

✅ **Frontend is now running on http://localhost:8080**

---

## 🌐 Step 5: Access the Application

1. Open your web browser
2. Navigate to: **http://localhost:8080**
3. You should see the Campus Carbon Pulse dashboard with:
   - 3D campus map
   - Time slider at the bottom
   - "CAMPUS TWIN" header
   - Real-time emission data

---

## 🎮 Step 6: Test the Application

### **Test 1: Time Slider**
- Move the slider from left (Hour 0) to right (Hour 23)
- Buildings should change colors (green → yellow → red)
- Total emission value should update

### **Test 2: Building Click**
- Click on any building on the 3D map
- A popup should appear showing:
  - Building name
  - Heat Level (%)
  - Carbon emission (kg/h)
  - Height (m)

### **Test 3: API Check**
- Open: http://localhost:8000/get-emissions/10
- You should see JSON data with emission predictions

---

## 🛑 Stopping the Application

### **Stop Frontend:**
In Terminal 2, press: `Ctrl + C`

### **Stop Backend:**
In Terminal 1, press: `Ctrl + C`

### **Deactivate Python Virtual Environment:**
```bash
deactivate
```

---

## 🔄 Running Again Later

### **Quick Start (After Initial Setup):**

**Terminal 1 (Backend):**
```bash
cd backend
venv\Scripts\activate          # Windows
# OR
source venv/bin/activate       # macOS/Linux

python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd campus-carbon-pulse-main
npm run dev
```

---

## 🐛 Troubleshooting

### **Problem: "Port 8000 already in use"**
**Solution:**
```bash
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### **Problem: "Port 8080 already in use"**
**Solution:** Edit `vite.config.ts` and change the port:
```typescript
server: {
  port: 3000,  // Change to any available port
}
```

### **Problem: "Module not found" errors**
**Solution:**
```bash
# Frontend:
rm -rf node_modules package-lock.json
npm install

# Backend:
pip install -r requirements.txt --force-reinstall
```

### **Problem: Python virtual environment won't activate (Windows)**
**Solution:**
```bash
# Run PowerShell as Administrator:
Set-ExecutionPolicy RemoteSigned
```

### **Problem: Map not loading**
**Solution:**
- Check browser console (F12) for errors
- Verify `public/campus.json` exists
- Ensure backend is running on port 8000

### **Problem: Colors not changing**
**Solution:**
- Check that `backend/emissions.json` exists
- Verify API is responding: http://localhost:8000/get-emissions/0
- Clear browser cache (Ctrl + Shift + R)

---

## 📊 Project Architecture

```
┌─────────────────────────────────────────────────┐
│  Browser (http://localhost:8080)                │
│  ┌───────────────────────────────────────────┐  │
│  │  React Frontend                           │  │
│  │  - 3D Map (MapLibre)                      │  │
│  │  - Time Slider                            │  │
│  │  - Dashboard UI                           │  │
│  └───────────────┬───────────────────────────┘  │
└──────────────────┼──────────────────────────────┘
                   │ HTTP Requests
                   │ GET /get-emissions/{hour}
                   ▼
┌─────────────────────────────────────────────────┐
│  Backend (http://localhost:8000)                │
│  ┌───────────────────────────────────────────┐  │
│  │  FastAPI Server                           │  │
│  │  - main.py (API endpoints)                │  │
│  │  - forecast.py (LSTM predictions)         │  │
│  │  - emissions.json (24h forecasts)         │  │
│  │  - models/*.keras (trained models)        │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Next Steps

- ✅ Explore different hours on the time slider
- ✅ Click buildings to see detailed metrics
- ✅ Check the API documentation: http://localhost:8000/docs
- ✅ Customize the campus map data in `public/campus.json`
- ✅ Retrain LSTM models with new data

---

## 💡 Tips

1. **Keep both terminals open** while using the app
2. **Backend auto-reloads** when you edit Python files
3. **Frontend hot-reloads** when you edit React/TypeScript files
4. **Check browser console (F12)** for debugging
5. **API docs available** at http://localhost:8000/docs

---

## 📞 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure both servers are running
4. Check terminal output for error messages

---

**Happy Monitoring! 🌍💚**
