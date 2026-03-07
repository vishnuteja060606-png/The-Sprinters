# The-Sprinters – AI Fashion Stylist

This Generative AI platform provides **personalized fashion recommendations** based on user preferences and visual inputs. It delivers:

- **Personalized styling advice**
- **Outfit recommendations**
- **Image-based analysis**
- **Trend-aware suggestions**
- **Interactive UI**

The stack is **Python-only** end-to-end:

- **Backend**: FastAPI
- **Frontend**: Streamlit (with custom HTML/CSS styling)
- **AI integrations (currently mocked)**: Gemini, Hugging Face, Groq, IBM AI

---

## Quick start

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Run the FastAPI backend**

```bash
python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000
```

3. **Run the Streamlit frontend**

```bash
python -m streamlit run frontend.py
```

4. Open the URL printed by Streamlit (usually `http://localhost:8501`) and:

- Set your **style profile** in the left sidebar
- Click **“Generate outfits”** for recommendations
- Paste an **image URL** for mocked image-based analysis

---

## Where to plug in real AI

All external models are currently mocked in `backend.py` so the app runs without credentials. To connect real services:

- **Gemini**: Replace `_mock_gemini_style_explanation` with a call to the Gemini text model for natural language styling rationale.
- **Hugging Face**: Replace `_mock_hf_trend_tags` with a pipeline/model call that predicts style / trend tags from text or images.
- **IBM AI**: Replace `_mock_ibm_style_rules` with IBM Watson / watsonx rules or an LLM that enforces constraints (budget, dislikes, dress codes).
- **Groq**: Replace `_mock_groq_rerank` with reranking / fast inference over candidate outfits using Groq-hosted models.

All of these should be implemented as **pure Python** functions inside `backend.py`, keeping the stack consistent.

---

## Groq setup (to get varied outputs)

`backend.py` supports Groq via the OpenAI-compatible endpoint. **Do not paste your API key into the code or commit it to git.** Instead, set it in an environment variable.

PowerShell:

```bash
$env:GROQ_API_KEY="your_real_key_here"
uvicorn backend:app --reload --port 8000
```

Optional: choose a model:

```bash
$env:GROQ_MODEL="llama-3.1-8b-instant"
```
