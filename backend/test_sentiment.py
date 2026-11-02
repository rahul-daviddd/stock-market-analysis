import sys
import os
sys.path.append('c:\\Users\\rahul\\dev\\pt-2\\stock-market-analysis\\backend')
from dotenv import load_dotenv
load_dotenv('c:\\Users\\rahul\\dev\\pt-2\\stock-market-analysis\\backend\\.env')

from services.sentiment import get_crypto_news_sentiment

if __name__ == "__main__":
    res = get_crypto_news_sentiment("BTC")
    print(res)
