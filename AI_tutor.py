"""
AI_tutor.py — Engine Smoke Test
Verifies the raw Google GenAI endpoint is reachable before launching the full app.
Run this standalone first if you suspect API key or network issues.
"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_KEY:
    print("\n❌ CRITICAL: GOOGLE_API_KEY not found in your .env file!")
    print("   Create a .env file in this folder with:  GOOGLE_API_KEY=your_key_here")
    exit(1)

print("\n🔑 API key loaded. Sending test dispatch to Gemini...")

client = genai.Client(api_key=GOOGLE_KEY)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write a one-line software architecture haiku."
)

print("\n━━ ⚡ ENGINE ONLINE ━━")
print(response.text.strip())
print("━━━━━━━━━━━━━━━━━━━━━━\n")
print("✅ GenAI endpoint verified. Safe to run:  streamlit run app.py")

