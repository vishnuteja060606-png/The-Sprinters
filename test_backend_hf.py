from backend import _hf_analyze_image, ImageAnalysisRequest
import traceback

def test():
    req = ImageAnalysisRequest(
        image_url="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
        notes="Testing"
    )
    # Mocking the print temporarily to capture the output instead of relying on the backend debug
    import backend
    original_client = backend.InferenceClient
    
    class MockClient:
        def __init__(self, *args, **kwargs):
            self.client = original_client(*args, **kwargs)
        
        @property
        def chat(self):
            return self.client.chat
            
    # We will just run it and let the backend print it. But we'll redirect stdout to a file!
    import sys
    with open("llm_output.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        result = _hf_analyze_image(req)
        sys.stdout = sys.__stdout__
        
    if result is None:
        print("Analysis returned None!")
    else:
        print("Success!")
        print(result)

if __name__ == "__main__":
    test()
