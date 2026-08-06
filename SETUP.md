# Campus Carbon Pulse - Setup Guide

## Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

## Initial Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd campus-carbon-pulse-main
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Get your Google Gemini API key:
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the generated API key

3. Open the `.env` file and add your API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

   **⚠️ IMPORTANT**: Never commit the `.env` file to Git! It's already in `.gitignore`.

#### Run the Backend Server
```bash
# From the backend directory
python -m uvicorn main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

#### Install Node Dependencies
```bash
# From the project root
npm install
```

#### Run the Development Server
```bash
npm run dev
```

The frontend will be available at `http://localhost:8080`

## Troubleshooting

### "GEMINI_API_KEY not found" Error
- Make sure you created the `.env` file in the project root
- Verify the API key is correctly pasted without extra spaces
- Check that the `.env` file contains: `GEMINI_API_KEY=your_key_here`

### API Key Quota Exceeded
- Each Google account has a free tier quota for Gemini API
- If you exceed the quota, you may need to:
  - Wait for the quota to reset (usually daily)
  - Upgrade to a paid plan
  - Create a new API key with a different Google account

### Backend Won't Start
- Ensure all Python dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is already in use
- Verify Python version: `python --version` (should be 3.8+)

### Frontend Won't Start
- Ensure all Node dependencies are installed: `npm install`
- Check if port 8080 is already in use
- Verify Node version: `node --version` (should be 16+)

## Team Collaboration Notes

### For New Team Members
1. **Never share your API key** - Each team member should get their own free API key
2. **Never commit `.env` file** - This file is in `.gitignore` for security
3. **Always use `.env.example`** as a template for your local `.env` file

### For Repository Maintainers
- Keep `.env.example` updated with any new environment variables
- Document any new API keys or secrets needed in this SETUP.md file
- Regularly check that `.env` is in `.gitignore`

## Additional Resources
- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Documentation](https://vitejs.dev/)
