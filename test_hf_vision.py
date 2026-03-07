from dotenv import load_dotenv
load_dotenv()

import os
from huggingface_hub import InferenceClient
import json

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"

def test_hf_vision():
    client = InferenceClient(api_key=HF_TOKEN, model=MODEL_ID)
    image_url = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=500"
    prompt = "Analyze this fashion look. Return ONLY valid JSON with exactly these keys: 'detected_style' (list of strings), 'color_palette' (list of strings), 'fit_feedback' (string detailing styling and fit suggestions)."
    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        }
    ]

    try:
        response = client.chat.completions.create(
            messages=messages,
            max_tokens=500,
        )
        print("Response:", response.choices[0].message.content)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_hf_vision()
