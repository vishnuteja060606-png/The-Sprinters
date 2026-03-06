import json
from typing import List

import requests
import streamlit as st

API_BASE = "http://localhost:8000"


def _post_json(path: str, payload: dict):
    url = f"{API_BASE}{path}"
    resp = requests.post(url, json=payload, timeout=20)
    resp.raise_for_status()
    return resp.json()


def _set_page_config() -> None:
    st.set_page_config(
        page_title="AI Fashion Stylist",
        page_icon="✨",
        layout="wide",
    )


def _inject_css() -> None:
    st.markdown(
        """
        <style>
        .main {
            background: radial-gradient(circle at top left, #151827 0, #050711 55%, #020308 100%);
            color: #f8fafc;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
        }
        section[data-testid="stSidebar"] {
            background: rgba(10, 13, 26, 0.95);
            border-right: 1px solid rgba(148, 163, 184, 0.3);
        }
        .stButton > button {
            border-radius: 999px;
            padding: 0.6rem 1.4rem;
            border: 1px solid rgba(94, 234, 212, 0.6);
            background: linear-gradient(90deg, #22c55e, #22d3ee);
            color: #020617;
            font-weight: 600;
            letter-spacing: 0.02em;
        }
        .stButton > button:hover {
            box-shadow: 0 0 24px rgba(56, 189, 248, 0.5);
            transform: translateY(-1px);
        }
        .pill {
            display: inline-flex;
            align-items: center;
            padding: 0.12rem 0.55rem;
            border-radius: 999px;
            font-size: 0.74rem;
            border: 1px solid rgba(148, 163, 184, 0.6);
            margin-right: 0.25rem;
            margin-bottom: 0.2rem;
            background: radial-gradient(circle at top left, rgba(56, 189, 248, 0.24), transparent 60%);
        }
        .card {
            border-radius: 1rem;
            padding: 1rem 1.1rem;
            background: radial-gradient(circle at top left, rgba(79, 70, 229, 0.36), rgba(15,23,42,0.95));
            border: 1px solid rgba(148, 163, 184, 0.4);
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.85);
        }
        .card h3 {
            margin-bottom: 0.4rem;
        }
        .muted {
            color: #9ca3af;
            font-size: 0.86rem;
        }
        .monosmall {
            font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            font-size: 0.78rem;
            color: #a5b4fc;
        }
        hr {
            border-color: rgba(51, 65, 85, 0.9);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _sidebar() -> dict:
    with st.sidebar:
        st.markdown("### Your Fashion Profile")
        age = st.slider("Age", 16, 65, 24)
        gender = st.selectbox("Gender expression", ["Prefer not to say", "Feminine", "Masculine", "Androgynous"])

        st.markdown("**Style goals**")
        style_options = ["Minimal", "Streetwear", "Formal", "Athleisure", "Y2K", "Edgy", "Soft / Romantic"]
        style_goals: List[str] = st.multiselect("Select 2–3", style_options, default=["Minimal"])

        st.markdown("**Occasions**")
        occ_options = ["Work", "University", "Dates / Evenings", "Weekend", "Events / Weddings"]
        occasions: List[str] = st.multiselect("Where will you wear these?", occ_options, default=["Weekend"])

        budget = st.selectbox("Budget level", ["Low", "Medium", "High"], index=1)

        st.markdown("**Color preferences**")
        color_options = ["Black", "White", "Beige", "Navy", "Grey", "Denim Blue", "Pastels", "Bold colors"]
        preferred_colors: List[str] = st.multiselect("Colors you love", color_options, default=["Black", "White", "Denim Blue"])

        disliked_items_text = st.text_input("Items you dislike (comma-separated)", value="Skinny jeans")
        disliked_items = [i.strip() for i in disliked_items_text.split(",") if i.strip()]

        st.markdown("---")
        st.markdown(
            '<span class="monosmall">Models: Gemini · Hugging Face · Groq · IBM AI (mocked)</span>',
            unsafe_allow_html=True,
        )

    payload = {
        "age": age,
        "gender": None if gender == "Prefer not to say" else gender,
        "style_goals": style_goals,
        "occasions": occasions,
        "budget_level": budget.lower(),
        "preferred_colors": preferred_colors,
        "disliked_items": disliked_items,
    }
    return payload


def _hero_section() -> None:
    left, right = st.columns([1.6, 1.1])
    with left:
        st.markdown(
            """
            <div style="margin-top: 1.8rem;">
              <div class="pill">✨ Generative AI Fashion Studio</div>
              <h1 style="font-size: 2.35rem; line-height: 1.1; margin-top: 0.6rem;">
                Personalized outfits,<br/>generated in seconds.
              </h1>
              <p class="muted" style="margin-top: 0.6rem; max-width: 34rem;">
                Feed your style goals and images into an AI stylist that understands silhouettes, color balance, and current trends — 
                then returns outfits you can actually wear tomorrow.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="card" style="margin-top: 1.6rem;">
              <p class="monosmall">Capabilities</p>
              <ul style="padding-left: 1rem; margin-top: 0.4rem;">
                <li>Personalized styling advice</li>
                <li>Outfit recommendations</li>
                <li>Image-based look analysis</li>
                <li>Trend-aware suggestions</li>
                <li>Interactive, explorable UI</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_recommendations(data: dict) -> None:
    st.markdown("### Recommended outfits")
    recs = data.get("recommendations", [])
    cols = st.columns(3)
    for idx, rec in enumerate(recs):
        col = cols[idx % 3]
        with col:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"#### {rec['title']}")
            st.markdown(f"<p class='muted'>{rec['description']}</p>", unsafe_allow_html=True)

            st.markdown("**Pieces**")
            for p in rec.get("pieces", []):
                st.markdown(f"- {p}")

            st.markdown("<div style='margin-top: 0.3rem;'>", unsafe_allow_html=True)
            for tag in rec.get("style_tags", []):
                st.markdown(f"<span class='pill'>{tag}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                f"<p class='monosmall' style='margin-top:0.45rem;'>Model confidence · {rec['confidence']*100:.0f}%</p>",
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### How the AI thinks about your style")
    st.write(data.get("trend_notes", ""))

    st.markdown("**Styling guidance**")
    for tip in data.get("styling_tips", []):
        st.markdown(f"- {tip}")


def _image_analysis_ui() -> None:
    st.markdown("### Image-based analysis")
    st.markdown(
        "Paste an image URL of your current outfit, a moodboard, or an inspiration look. "
        "In a real deployment this would be a Gemini / Hugging Face vision model."
    )
    img_url = st.text_input("Image URL")
    note = st.text_input("Optional notes", value="This is my daily fit, make it sharper.")

    analyze = st.button("Analyze image", key="analyze_image")
    if analyze and img_url:
        with st.spinner("Analyzing style and fit (mocked)…"):
            data = _post_json(
                "/api/analyze-image",
                {"image_url": img_url, "notes": note or None},
            )
        left, right = st.columns([1.3, 1])
        with left:
            st.image(img_url, caption="Reference image", use_column_width=True)
        with right:
            st.markdown("**Detected style signals**")
            st.markdown(
                " ".join(f"<span class='pill'>{t}</span>" for t in data["detected_style"]),
                unsafe_allow_html=True,
            )
            st.markdown("**Color palette**")
            st.markdown(
                " ".join(f"<span class='pill'>{c}</span>" for c in data["color_palette"]),
                unsafe_allow_html=True,
            )
            st.markdown("**Fit notes**")
            st.write(data["fit_feedback"])


def main() -> None:
    _set_page_config()
    _inject_css()
    profile_payload = _sidebar()

    _hero_section()

    st.markdown("### Generate personalized outfits")
    st.markdown(
        "The backend combines multiple AI signals (text reasoning, trend tags, rule-based constraints, and ranking) "
        "to build outfits aligned with your profile."
    )

    if st.button("Generate outfits", key="gen_outfits"):
        with st.spinner("Asking your AI stylist… (mocked models)"):
            data = _post_json("/api/recommend", profile_payload)
        _render_recommendations(data)
    else:
        st.info("Set your profile in the left panel, then click **Generate outfits**.")

    st.markdown("---")
    _image_analysis_ui()

    with st.expander("Debug · raw API payloads"):
        st.code(json.dumps(profile_payload, indent=2), language="json")


if __name__ == "__main__":
    main()

