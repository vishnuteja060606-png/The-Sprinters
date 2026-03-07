from typing import List, Optional

import json
import os
import requests

from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import InferenceClient
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
import backend_auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    email = backend_auth.decode_access_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return email

# Auth Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class UserProfile(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    style_goals: List[str] = []
    occasions: List[str] = []
    budget_level: Optional[str] = None
    preferred_colors: List[str] = []
    disliked_items: List[str] = []


class ImageAnalysisRequest(BaseModel):
    image_url: str
    notes: Optional[str] = None


class OutfitRecommendation(BaseModel):
    title: str
    description: str
    pieces: List[str]
    style_tags: List[str]
    confidence: float


class RecommendationResponse(BaseModel):
    recommendations: List[OutfitRecommendation]
    trend_notes: str
    styling_tips: List[str]


app = FastAPI(title="AI Fashion Stylist API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = "your_groq_api_key_here"
GROQ_API_BASE = "https://api.groq.com/openai/v1"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
HF_TOKEN = "your_hf_token_here"
HF_VISION_MODEL = "Qwen/Qwen2.5-VL-7B-Instruct"


def _groq_key() -> str:
    return GROQ_API_KEY


def _groq_chat_json(system: str, user: str, *, timeout_s: int = 30) -> Optional[dict]:
    api_key = _groq_key()
    url = f"{GROQ_API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "temperature": 0.8,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(content[start : end + 1])
        return None
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return None


def _groq_generate_outfits(profile: UserProfile) -> Optional[RecommendationResponse]:
    system = (
        "You are an expert personal stylist. Return ONLY valid JSON. "
        "You must follow the user's constraints strictly (dislikes, budget, occasions, colors)."
    )
    user = (
        "Generate 3 distinct outfit recommendations.\n"
        "Return a JSON object with this exact schema:\n"
        "{\n"
        '  "recommendations": [\n'
        "    {\n"
        '      "title": string,\n'
        '      "description": string,\n'
        '      "pieces": [string, ...],\n'
        '      "style_tags": [string, ...],\n'
        '      "confidence": number 0..1\n'
        "    }\n"
        "  ],\n"
        '  "trend_notes": "string explaining how the outfits balance the goals and occasions",\n'
        '  "styling_tips": ["string", "string"] (3-5 specific styling rules based on the constraints)\n'
        "}\n\n"
        "User profile:\n"
        f"- Age: {profile.age}\n"
        f"- Gender expression: {profile.gender}\n"
        f"- Style goals: {profile.style_goals}\n"
        f"- Occasions: {profile.occasions}\n"
        f"- Budget level: {profile.budget_level}\n"
        f"- Preferred colors: {profile.preferred_colors}\n"
        f"- Disliked items: {profile.disliked_items}\n"
    )

    obj = _groq_chat_json(system, user)
    if not obj or "recommendations" not in obj:
        return None

    try:
        recs_raw = obj["recommendations"]
        recs: List[OutfitRecommendation] = [
            OutfitRecommendation(
                title=str(r.get("title", "Outfit")),
                description=str(r.get("description", "")),
                pieces=[str(x) for x in r.get("pieces", [])],
                style_tags=[str(x) for x in r.get("style_tags", [])],
                confidence=float(r.get("confidence", 0.75)),
            )
            for r in recs_raw
        ]
        
        return RecommendationResponse(
            recommendations=sorted(recs, key=lambda r: r.confidence, reverse=True)[:3],
            trend_notes=str(obj.get("trend_notes", "These outfits match your goals.")),
            styling_tips=[str(x) for x in obj.get("styling_tips", ["Wear with confidence!"])],
        )
    except Exception as e:
        print(f"Parse error: {e}")
        return None


def _hf_analyze_image(request: ImageAnalysisRequest) -> Optional[dict]:
    import time
    import base64
    
    # Fetch the image to bypass 403s/404s on Google/Pinterest
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "DNT": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Referer": "https://www.google.com/"
        }
        
        # Some URLs need a proper session to handle cookies/redirects
        session = requests.Session()
        img_resp = session.get(request.image_url, headers=headers, timeout=10, allow_redirects=True)
        img_resp.raise_for_status()
        
        # Verify it's actually an image and not a 1x1 tracking pixel or HTML page
        if len(img_resp.content) < 100 or 'text/html' in img_resp.headers.get('Content-Type', ''):
            raise Exception("URL returned HTML or an empty/tracking pixel image.")
        
        content_type = img_resp.headers.get("Content-Type", "image/jpeg")
        base64_img = base64.b64encode(img_resp.content).decode('utf-8')
        data_uri = f"data:{content_type};base64,{base64_img}"
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        error_msg = f"Failed to fetch image: Server returned {status} (which means the image link is broken or protected)."
        print(f"DEBUG: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Failed to download image URL. Ensure it's a direct, publicly accessible image link. Error: {str(e)}"
        print(f"DEBUG: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)

    for attempt in range(3):
        try:
            client = InferenceClient(api_key=HF_TOKEN, model=HF_VISION_MODEL)
            prompt = (
                "Analyze this fashion look. "
                f"Optional notes from user: {request.notes or 'None'}. "
                "Return ONLY JSON with exactly these keys: 'detected_style' (list of strings), 'color_palette' (list of strings), 'fit_feedback' (string detailing styling and fit suggestions)."
            )
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_uri}}
                    ]
                }
            ]
            
            response = client.chat.completions.create(
                messages=messages,
                max_tokens=500,
            )
            content = response.choices[0].message.content
            print(f"DEBUG LLM OUTPUT: {content}")
            
            # Manually extract JSON from the LLM text output
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(content[start : end + 1])
                except json.JSONDecodeError:
                    pass
            print(f"DEBUG: Could not find valid JSON boundaries on attempt {attempt+1}")
        except Exception as e:
            import traceback
            print(f"Error on Hugging Face Vision API (attempt {attempt+1}): {e}")
            traceback.print_exc()
        
        # small delay before retry
        time.sleep(1.5)
        
    return None


@app.post("/api/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(backend_auth.get_db)):
    db_user = db.query(backend_auth.User).filter(backend_auth.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = backend_auth.get_password_hash(user.password)
    new_user = backend_auth.User(email=user.email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    from datetime import timedelta
    access_token_expires = timedelta(minutes=backend_auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = backend_auth.create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(backend_auth.get_db)):
    db_user = db.query(backend_auth.User).filter(backend_auth.User.email == user.email).first()
    if not db_user or not backend_auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    from datetime import timedelta
    access_token_expires = timedelta(minutes=backend_auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = backend_auth.create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/recommend", response_model=RecommendationResponse)
def recommend_outfits(profile: UserProfile, current_user: str = Depends(get_current_user)) -> RecommendationResponse:
    response = _groq_generate_outfits(profile)
    if not response:
        raise HTTPException(status_code=500, detail="Failed to generate recommendations via Groq AI")
    return response


class ImageAnalysisResponse(BaseModel):
    detected_style: List[str]
    color_palette: List[str]
    fit_feedback: str


@app.post("/api/analyze-image", response_model=ImageAnalysisResponse)
def analyze_image(payload: ImageAnalysisRequest, current_user: str = Depends(get_current_user)) -> ImageAnalysisResponse:
    obj = _hf_analyze_image(payload)
    if not obj:
        raise HTTPException(status_code=500, detail="Failed to analyze image via Hugging Face")
        
    try:
        return ImageAnalysisResponse(
            detected_style=[str(x) for x in obj.get("detected_style", ["casual"])],
            color_palette=[str(x) for x in obj.get("color_palette", ["mixed"])],
            fit_feedback=str(obj.get("fit_feedback", "Looking great!")),
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid response format from Groq AI")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
