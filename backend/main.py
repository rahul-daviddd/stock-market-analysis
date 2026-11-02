from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from services.crypto_data import fetch_historical_crypto
from services.forecasting import train_and_predict
from services.sentiment import get_crypto_news_sentiment
from services.adv_technicals import calculate_fibonacci, calculate_zigzag
from ta.momentum import RSIIndicator
from ta.trend import MACD
import pandas as pd
load_dotenv(override=True)

app = FastAPI(title="Crypto Market Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Crypto Market Analysis API is running (Conda DL Env)"}

@app.get("/api/history/{symbol}")
def get_history(symbol: str):
    try:
        data = fetch_historical_crypto(symbol.upper())
        
        # Technical Analysis via 'ta' library
        close_series = data['close']
        rsi = RSIIndicator(close=close_series, window=14).rsi().iloc[-1]
        
        # Explicitly setting MACD to standard 12, 26, 9 defaults
        macd_indicator = MACD(close=close_series, window_fast=12, window_slow=26, window_sign=9)
        macd_line = macd_indicator.macd().iloc[-1]
        macd_signal = macd_indicator.macd_signal().iloc[-1]
        macd_hist = macd_indicator.macd_diff().iloc[-1] # Histogram: MACD - Signal
        
        # LSTM Forecasting Prediction
        forecasts = train_and_predict(data, forecast_days=5)
        
        # Determine Basic Signal based on indicators & LSTM
        signal = "Hold"
        if pd.notna(rsi) and pd.notna(macd_hist):
            # Oversold and momentum turning positive = Strong Buy
            if rsi < 35 and macd_hist > 0:
                signal = "Strong Buy"
            elif rsi < 45 or (rsi < 55 and macd_hist > 0):
                signal = "Buy"
            # Overbought and momentum turning negative = Strong Sell
            elif rsi > 70 and macd_hist < 0:
                signal = "Strong Sell"
            elif rsi > 60 or (rsi > 50 and macd_hist < 0):
                signal = "Sell"
                
        if len(forecasts) > 0 and signal == "Hold":
             # Extremely basic consensus logic using LSTM
             if forecasts[-1] > data['close'].iloc[-1] * 1.05:
                 signal = "Buy (AI Forecasted)"
             elif forecasts[-1] < data['close'].iloc[-1] * 0.95:
                 signal = "Sell (AI Forecasted)"

        fibs = calculate_fibonacci(data)
        zigzag = calculate_zigzag(data, deviation_perc=5.0)

        technicals_payload = {
            "rsi": float(rsi) if pd.notna(rsi) else 0,
            "macd": float(macd_line) if pd.notna(macd_line) else 0,
            "signal": signal,
            "lstm_forecast": forecasts,
            "fibonacci": fibs,
            "zigzag": zigzag
        }

        data.index = data.index.astype(str)
        data = data.reset_index()
        data.rename(columns={'Date': 'time', 'index': 'time'}, inplace=True)
        history_payload = data.to_dict(orient='records')

        return {
            "history": history_payload,
            "technicals": technicals_payload
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/sentiment/{symbol}")
def get_sentiment(symbol: str):
    try:
        # Pulls live news and runs it through ProsusAI/finbert
        sentiment_data = get_crypto_news_sentiment(symbol.upper())
        return sentiment_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
