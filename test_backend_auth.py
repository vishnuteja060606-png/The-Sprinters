import requests

BASE_URL = "http://localhost:8000"

def test_auth():
    print("Testing Signup...")
    signup_data = {"email": "test@example.com", "password": "securepassword"}
    resp = requests.post(f"{BASE_URL}/api/signup", json=signup_data)
    
    if resp.status_code == 200:
        print("Signup Success:", resp.json())
    else:
        print("Signup Status:", resp.status_code)
        print("Signup Error:", resp.text)
        
    print("\nTesting Login...")
    resp = requests.post(f"{BASE_URL}/api/login", json=signup_data)
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        print("Login Success, Token generated:", len(token) > 0)
        
        print("\nTesting Auth-Protected Endpoint (/api/analyze-image)...")
        headers = {"Authorization": f"Bearer {token}"}
        # Intentionally invalid image data to ensure we hit the 400 validation error (which means we got past the 401 Auth error)
        req = requests.post(
            f"{BASE_URL}/api/analyze-image", 
            json={"image_url": "invalid_url"},
            headers=headers
        )
        if req.status_code == 400:
            print("Protected API Access Success (Got expected 400 Bad Request instead of 401 Unauthorized)")
        elif req.status_code == 401:
            print("Protected API Access FAILED (Auth rejected)")
        else:
            print(f"Protected API returned: {req.status_code}: {req.text}")
            
    else:
        print("Login Status:", resp.status_code)
        print("Login Error:", resp.text)

if __name__ == "__main__":
    test_auth()
