# Crypto & Stock Market Analysis Platform

A full-stack financial market analysis and forecasting platform combining technical indicators, deep learning (LSTM) price prediction, and AI-driven news sentiment analysis.

---

## Features

- **Interactive Candlestick Charts**: High-performance charting powered by TradingView's Lightweight Charts.
- **Technical Indicators**: Real-time calculation of RSI, MACD, Fibonacci retracements, and ZigZag patterns.
- **Deep Learning Price Forecasting**: On-the-fly PyTorch LSTM model predicting multi-day price directions.
- **AI-Powered Sentiment Analysis**: Financial news retrieval coupled with Google Gemini GenAI narrative evaluation.
- **Modern Responsive UI**: Fast and reactive dashboard built with React 19 and Vite.

---

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, PyTorch, Pandas, NumPy, scikit-learn, `ta`, `yfinance`, Google GenAI SDK.
- **Frontend**: React 19, Vite, Lightweight Charts, Lucide React.

---

## Project Structure

```text
├── backend/
│   ├── services/
│   │   ├── adv_technicals.py   # Fibonacci & ZigZag indicators
│   │   ├── crypto_data.py      # Historical market data fetcher
│   │   ├── forecasting.py      # PyTorch LSTM forecasting model
│   │   └── sentiment.py        # Gemini-based news sentiment analysis
│   ├── .env.example            # Environment variables template
│   ├── main.py                 # FastAPI application & endpoints
│   └── requirements.txt        # Python backend dependencies
├── frontend/
│   ├── src/                    # React components and styling
│   ├── package.json            # Frontend dependencies & scripts
│   └── vite.config.js          # Vite configuration
├── generate_report_graphs.py   # Script for generating analytical visual charts
├── .gitignore                  # Git ignore rules for Python & Node.js
└── README.md                   # Project documentation
```

---

## Getting Started

### 1. Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm
- (Optional) API keys for Google Gemini & Finnhub

---

### 2. Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # On macOS/Linux:
   python3 -m venv .venv
   source .venv/bin/activate

   # On Windows (PowerShell):
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in your API credentials:
   ```env
   FINNHUB_API_KEY=your_finnhub_key
   GEMINI_API_KEY=your_gemini_key
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   The API will be available at `http://127.0.0.1:8000` (docs at `http://127.0.0.1:8000/docs`).

---

### 3. Frontend Setup

1. In a new terminal, navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   Open your browser to the URL shown in terminal (typically `http://localhost:5173`).

---

## License

This project is licensed under the MIT License.

