from backend import _hf_analyze_image, ImageAnalysisRequest
import traceback

def test():
    req = ImageAnalysisRequest(
        image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_xOT1VofYV237g77Dng2H5Jv5t-A3x30k1A&usqp=CAU", # Example google image
        notes="Testing google image"
    )
    
    result = _hf_analyze_image(req)
        
    if result is None:
        print("Analysis returned None!")
    else:
        print("Success!")
        print(result)

if __name__ == "__main__":
    test()
