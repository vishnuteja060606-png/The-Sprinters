from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


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


def _mock_gemini_style_explanation(profile: UserProfile) -> str:
    goals = ", ".join(profile.style_goals) if profile.style_goals else "everyday versatility"
    occasions = ", ".join(profile.occasions) if profile.occasions else "casual wear"
    return (
        "These outfits balance comfort and structure, focusing on "
        f"{goals} suitable for {occasions}. Silhouettes stay clean so you can mix pieces easily."
    )


def _mock_hf_trend_tags(profile: UserProfile) -> List[str]:
    tags: List[str] = ["clean-core", "elevated-basics"]
    if "streetwear" in [g.lower() for g in profile.style_goals]:
        tags.append("modern-street")
    if "formal" in [o.lower() for o in profile.occasions]:
        tags.append("tailored-minimal")
    return tags


def _mock_ibm_style_rules(profile: UserProfile) -> List[str]:
    rules: List[str] = []
    if profile.budget_level == "low":
        rules.append("Prioritize versatile staples that re-style across many outfits.")
    if profile.preferred_colors:
        rules.append(
            f"Anchor looks around {', '.join(profile.preferred_colors)} with 1 neutral base tone."
        )
    if profile.disliked_items:
        rules.append(f"Avoid: {', '.join(profile.disliked_items)}.")
    if not rules:
        rules.append("Keep outfits modular so pieces work across multiple occasions.")
    return rules


def _mock_groq_rerank(recs: List[OutfitRecommendation]) -> List[OutfitRecommendation]:
    return sorted(recs, key=lambda r: r.confidence, reverse=True)


def _build_mock_outfits(profile: UserProfile) -> List[OutfitRecommendation]:
    base_tags = _mock_hf_trend_tags(profile)

    recs: List[OutfitRecommendation] = [
        OutfitRecommendation(
            title="Smart Casual Day Outfit",
            description=(
                "Crisp shirt layered with relaxed trousers and clean sneakers. "
                "Easy to dress up with a blazer or keep casual with a light overshirt."
            ),
            pieces=[
                "White or light blue button-up shirt",
                "Relaxed-fit neutral trousers",
                "Minimal white sneakers",
                "Optional lightweight blazer or overshirt",
            ],
            style_tags=base_tags + ["smart-casual"],
            confidence=0.88,
        ),
        OutfitRecommendation(
            title="Weekend Off-Duty Look",
            description=(
                "Soft knit top with straight-leg denim and comfortable sneakers or loafers. "
                "Layer with a structured jacket for extra polish."
            ),
            pieces=[
                "Fine-knit sweater or premium tee",
                "Straight-leg mid-wash jeans",
                "Retro sneakers or loafers",
                "Short structured jacket or bomber",
            ],
            style_tags=base_tags + ["off-duty"],
            confidence=0.83,
        ),
        OutfitRecommendation(
            title="Evening Minimalist Outfit",
            description=(
                "Monochrome base with a statement texture. "
                "Balanced proportions keep it modern and flattering."
            ),
            pieces=[
                "Monochrome top and bottom (e.g., all black or all navy)",
                "Textured layer (leather, satin, or structured knit)",
                "Sleek boots or heeled sandals",
            ],
            style_tags=base_tags + ["evening"],
            confidence=0.81,
        ),
    ]

    return _mock_groq_rerank(recs)


@app.post("/api/recommend", response_model=RecommendationResponse)
def recommend_outfits(profile: UserProfile) -> RecommendationResponse:
    outfits = _build_mock_outfits(profile)
    explanation = _mock_gemini_style_explanation(profile)
    rules = _mock_ibm_style_rules(profile)

    return RecommendationResponse(
        recommendations=outfits,
        trend_notes=explanation,
        styling_tips=rules,
    )


class ImageAnalysisResponse(BaseModel):
    detected_style: List[str]
    color_palette: List[str]
    fit_feedback: str


@app.post("/api/analyze-image", response_model=ImageAnalysisResponse)
def analyze_image(payload: ImageAnalysisRequest) -> ImageAnalysisResponse:
    return ImageAnalysisResponse(
        detected_style=["minimal", "casual", "trend-aware"],
        color_palette=["black", "white", "denim blue"],
        fit_feedback=(
            "Silhouette is balanced overall. You could size up outerwear slightly "
            "for a more relaxed drape, or add a tapered bottom to sharpen the look."
        ),
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

