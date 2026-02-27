"""
main.py — BizForge / BrandPilot AI
FastAPI backend: route handlers only. All AI logic is in ai_services.py.
Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

import ai_services as ai

# ─── App Setup ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="BizForge / BrandPilot AI",
    description="GenAI-Powered End-to-End Branding Platform",
    version="2.0.0",
)

# Allow requests from frontend served on file:// or any local origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated logos and uploads
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ─── Entry-point redirects (must be registered BEFORE the static mount) ─────
# Both / and /app redirect to the landing page so it is always shown first.

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/app/landing.html")

@app.get("/app", include_in_schema=False)
async def app_root():
    return RedirectResponse(url="/app/landing.html")


# Serve the frontend folder (registered AFTER the explicit routes above)
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


# ═══════════════════════════════════════════════════════════════════
# Request / Response Models
# ═══════════════════════════════════════════════════════════════════

class BrandNamesRequest(BaseModel):
    industry: str
    keywords: str
    tone: str
    language: str = "English"

class MarketingContentRequest(BaseModel):
    brand_description: str
    tone: str
    content_type: str
    language: str = "English"

class TaglineRequest(BaseModel):
    brand_name: str
    industry: str
    tone: str
    language: str = "English"

class BrandStoryRequest(BaseModel):
    brand_name: str
    industry: str
    mission: str
    tone: str
    language: str = "English"

class SocialPostsRequest(BaseModel):
    brand_name: str
    product_description: str
    platform: str
    tone: str
    language: str = "English"

class ProductDescriptionRequest(BaseModel):
    product_name: str
    features: str
    target_audience: str
    tone: str
    language: str = "English"

class ColorPaletteRequest(BaseModel):
    tone: str
    industry: str

class SentimentRequest(BaseModel):
    text: str
    brand_tone: str

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    system_context: str = ""

class LogoRequest(BaseModel):
    brand_name: str
    industry: str
    style_keywords: str
    description: str = ""
    mood: str = ""
    colors: str = ""

class CompetitorRequest(BaseModel):
    brand_name: str
    industry: str
    target_market: str
    language: str = "English"

class EmailCampaignRequest(BaseModel):
    brand_name: str
    campaign_goal: str
    product_service: str
    tone: str
    language: str = "English"

class BrandGuidelinesRequest(BaseModel):
    brand_name: str
    industry: str
    mission: str
    tone: str
    color_palette: str
    language: str = "English"


# ─── Utility wrapper ────────────────────────────────────────────────────────
def success(data) -> dict:
    return {"success": True, "data": data}


# ═══════════════════════════════════════════════════════════════════
# Health Check
# ═══════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {"message": "BizForge / BrandPilot AI API is running 🚀", "version": "2.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "BizForge API"}


# ═══════════════════════════════════════════════════════════════════
# TEXT GENERATION ROUTES  (Groq LLaMA-3.3-70B)
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/generate-brand-names")
async def generate_brand_names(req: BrandNamesRequest):
    """Generate 10 creative brand name suggestions."""
    try:
        result = await ai.generate_brand_names(
            req.industry, req.keywords, req.tone, req.language
        )
        return success(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-marketing-content")
async def generate_marketing_content(req: MarketingContentRequest):
    """Generate marketing copy for a given brand and content type."""
    try:
        result = await ai.generate_marketing_content(
            req.brand_description, req.tone, req.content_type, req.language
        )
        return success(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-taglines")
async def generate_taglines(req: TaglineRequest):
    """Generate 10 tagline variations."""
    try:
        result = await ai.generate_taglines(
            req.brand_name, req.industry, req.tone, req.language
        )
        return success(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-brand-story")
async def generate_brand_story(req: BrandStoryRequest):
    """Generate a compelling brand story / About Us narrative."""
    try:
        result = await ai.generate_brand_story(
            req.brand_name, req.industry, req.mission, req.tone, req.language
        )
        return success(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-social-posts")
async def generate_social_posts(req: SocialPostsRequest):
    """Generate platform-specific social media posts."""
    try:
        result = await ai.generate_social_posts(
            req.brand_name, req.product_description, req.platform, req.tone, req.language
        )
        return success(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-product-description")
async def generate_product_description(req: ProductDescriptionRequest):
    """Generate a compelling product description."""
    try:
        result = await ai.generate_product_description(
            req.product_name, req.features, req.target_audience, req.tone, req.language
        )
        return success(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-email-campaign")
async def generate_email_campaign(req: EmailCampaignRequest):
    """Generate a 3-email marketing campaign sequence."""
    try:
        result = await ai.generate_email_campaign(
            req.brand_name, req.campaign_goal, req.product_service, req.tone, req.language
        )
        return success(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-brand-guidelines")
async def generate_brand_guidelines(req: BrandGuidelinesRequest):
    """Generate comprehensive brand guidelines document."""
    try:
        result = await ai.generate_brand_guidelines(
            req.brand_name, req.industry, req.mission, req.tone,
            req.color_palette, req.language
        )
        return success(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
# DESIGN SYSTEM ROUTES  (Groq)
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/get-color-palette")
async def get_color_palette(req: ColorPaletteRequest):
    """Generate a brand color palette with HEX codes and usage guidance."""
    try:
        result = await ai.get_color_palette(req.tone, req.industry)
        return success(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-logo-prompt")
async def generate_logo_prompt(req: LogoRequest):
    """Generate a structured Gemini logo creation prompt (preview before generation)."""
    try:
        result = await ai.generate_logo_prompt(
            req.brand_name, req.industry, req.style_keywords,
            req.description, req.mood, req.colors
        )
        return success(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
# IMAGE GENERATION ROUTE  (Google Gemini)
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/generate-logo")
async def generate_logo(req: LogoRequest):
    """Generate a brand logo image using Pollinations.ai (FLUX)."""
    try:
        safe_name = req.brand_name.replace(" ", "_").lower()
        filename = f"{safe_name}_{uuid.uuid4().hex[:8]}.png"
        logo_url = await ai.generate_logo_image(
            req.brand_name, req.industry, req.style_keywords,
            filename, req.description, req.mood, req.colors
        )
        return success({"image_url": logo_url, "filename": filename})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
# ANALYSIS ROUTES  (Groq)
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/analyze-sentiment")
async def analyze_sentiment(req: SentimentRequest):
    """Analyze sentiment and brand alignment of marketing text."""
    try:
        result = await ai.analyze_sentiment(req.text, req.brand_tone)
        return success(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-competitors")
async def analyze_competitors(req: CompetitorRequest):
    """Provide competitive landscape analysis and positioning strategies."""
    try:
        result = await ai.analyze_competitors(
            req.brand_name, req.industry, req.target_market, req.language
        )
        return success(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════
# AI CHATBOT ROUTE  (IBM Granite via HF)
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Multi-turn branding AI chatbot powered by IBM Granite."""
    try:
        reply = await ai.chat_with_ai(
            req.message, req.session_id, req.system_context
        )
        return success({"reply": reply, "session_id": req.session_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/chat/{session_id}")
async def clear_chat(session_id: str):
    """Clear conversation history for a session."""
    ai.clear_chat_history(session_id)
    return success({"message": f"Session '{session_id}' cleared"})


# ═══════════════════════════════════════════════════════════════════
# VOICE TRANSCRIPTION ROUTE  (Groq Whisper)
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/transcribe-voice")
async def transcribe_voice(audio: UploadFile = File(...)):
    """Transcribe voice input using Groq Whisper."""
    try:
        audio_bytes = await audio.read()
        text = await ai.transcribe_voice(audio_bytes, audio.filename or "audio.webm")
        return success({"transcription": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
