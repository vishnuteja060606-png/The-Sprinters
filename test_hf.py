from dotenv import load_dotenv
load_dotenv()

import os
from huggingface_hub import InferenceClient
import traceback

try:
    client = InferenceClient(api_key=os.getenv("HF_TOKEN"), model="Qwen/Qwen2.5-VL-7B-Instruct")
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image."},
                {"type": "image_url", "image_url": {"url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"}}
            ]
        }
    ]
    response = client.chat.completions.create(messages=messages, max_tokens=10)
    print("Success:", response.choices[0].message.content)
except Exception as e:
    with open("hf_error.txt", "w") as f:
        f.write(traceback.format_exc())
    print("Error written to hf_error.txt")
