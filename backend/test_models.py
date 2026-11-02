import sys
import os
sys.path.append('c:\\Users\\rahul\\dev\\pt-2\\stock-market-analysis\\backend')
from dotenv import load_dotenv
load_dotenv('c:\\Users\\rahul\\dev\\pt-2\\stock-market-analysis\\backend\\.env')
from google import genai

gemini_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_key)
for m in client.models.list():
    print(m.name)
