from dotenv import load_dotenv
load_dotenv()

import os
import requests
import json

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_BASE = "https://api.groq.com/openai/v1"

def test_vision():
    prompt = "Analyze this fashion look. Return ONLY valid JSON with exactly these keys: 'detected_style' (list of strings), 'color_palette' (list of strings), 'fit_feedback' (string detailing styling and fit suggestions)."
    image_url = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=500"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
    }
    
    resp = requests.post(f"{GROQ_API_BASE}/chat/completions", headers=headers, json=payload)
    print("Status:", resp.status_code)
    try:
        print("Response JSON:", json.dumps(resp.json(), indent=2))
    except Exception as e:
        print("Response Text:", resp.text)

if __name__ == "__main__":
    test_vision()
