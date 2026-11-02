import yfinance as yf
from google import genai
from google.genai import types
import os
import json
import time

def get_crypto_news_sentiment(symbol: str):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("CRITICAL: GEMINI_API_KEY not found in environment.")
        return {"articles": [], "narrative": "Missing API Key", "stats": {}}
        
    try:
        # Initialize Google GenAI Client
        client = genai.Client(api_key=gemini_key)
        
        ticker = f"{symbol}-USD"
        news_items = yf.Ticker(ticker).news
        
        news_mapping = []
        news_text_block = ""
        
        # Scrape and aggregate top 5 articles securely
        for i, item in enumerate(news_items[:5]):
            content = item.get('content', {})
            title = content.get('title', '')
            summary = content.get('summary', '')
            url = content.get('canonicalUrl', {}).get('url', '')
            
            news_mapping.append({"title": title, "url": url})
            news_text_block += f"[Article {i}]\nTitle: {title}\nSummary: {summary}\n\n"
            
        # Few-Shot Prompt Engineering
        system_instruction = """
You are an elite institutional quantitative crypto analyst.
Evaluate the following cryptocurrency news articles.
Determine whether each article presents a 'positive', 'negative', or 'neutral' outlook for the asset's price action.
Assign a confidence score from 0.0 to 1.0 representing how strongly the wording implies the sentiment.

FEW-SHOT EXAMPLES:
Text: "SEC sues major exchange for unregistered securities." -> Sentiment: negative, Confidence: 0.95
Text: "Blackrock submits application for spot ETF." -> Sentiment: positive, Confidence: 0.90
Text: "Mining difficulty remains unchanged this quarter." -> Sentiment: neutral, Confidence: 0.50

Return ONLY a valid JSON Array of objects matching exactly the input index order.
Each object must have the keys: "sentiment" (string) and "confidence" (float).
"""
        
        # Fire Few-Shot inference utilizing Gemini 2.5 Flash with Retry for 503 errors
        max_retries = 3
        retry_delay = 2 # initial backoff in seconds
        response = None
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=news_text_block,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.1,
                        response_mime_type="application/json", # Native structured output validation
                    )
                )
                break
            except Exception as e:
                print(f"Gemini API attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2 # Exponential backoff
                else:
                    raise e # Reraise to be caught by the outer except block
        
        # Safely parse the guaranteed JSON array output
        analysis = json.loads(response.text)
        
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        analyzed_news = []
        
        # Cross-reference LLM output with our stored UI mappings
        for i, result_obj in enumerate(analysis):
            # Guard against potential LLM truncation vs input array constraints
            if i >= len(news_mapping):
                break
                
            label = str(result_obj.get("sentiment", "neutral")).lower()
            confidence = float(result_obj.get("confidence", 0.5))
            
            if 'positive' in label: bullish_count += 1
            elif 'negative' in label: bearish_count += 1
            else: neutral_count += 1
                
            # Safely rebuild the exact JSON dictionary expected by the React frontend payload
            analyzed_news.append({
                "title": news_mapping[i]["title"],
                "sentiment": "positive" if 'positive' in label else "negative" if 'negative' in label else "neutral",
                "confidence": confidence,
                "url": news_mapping[i]["url"]
            })
            
        # Determine macro narrative consensus
        narrative = "Neutral"
        if bullish_count > bearish_count:
            narrative = "Bullish"
        elif bearish_count > bullish_count:
            narrative = "Bearish"

        return {
            "articles": analyzed_news,
            "narrative": narrative,
            "stats": {"bullish": bullish_count, "bearish": bearish_count, "neutral": neutral_count}
        }
    except Exception as e:
        print(f"Gemini Inference Error: {e}")
        return {"articles": [], "narrative": "API Offline", "stats": {}}
