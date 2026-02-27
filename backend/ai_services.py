"""
ai_services.py — BizForge / BrandPilot AI
Intelligence Engine: All AI model integrations live here.
Modules: Groq LLaMA-3.3-70B, IBM Granite (HF), Stable Diffusion XL (HF)
"""

import os
import base64
import asyncio
import json
import re
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from huggingface_hub import AsyncInferenceClient
from PIL import Image
import requests

load_dotenv()

# ─── Clients ────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HF_API_KEY   = os.getenv("HF_API_KEY", "")

groq_client = Groq(api_key=GROQ_API_KEY)
hf_client   = AsyncInferenceClient(token=HF_API_KEY)

# IBM Granite model ID on Hugging Face
GRANITE_MODEL = "ibm-granite/granite-3.3-8b-instruct"

# Static logo output directory (served via FastAPI)
LOGO_DIR = Path(__file__).parent / "static" / "logos"
LOGO_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════
# HELPER: call Groq LLaMA-3.3-70B with a system + user prompt
# ═══════════════════════════════════════════════════════════════════
def _groq_chat(system_prompt: str, user_prompt: str, temperature: float = 0.8) -> str:
    """
    Internal helper that sends a chat request to Groq LLaMA-3.3-70B
    and returns the assistant message as a plain string.
    """
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


# ═══════════════════════════════════════════════════════════════════
# 1. BRAND NAME GENERATION  (Groq)
# ═══════════════════════════════════════════════════════════════════
async def generate_brand_names(
    industry: str,
    keywords: str,
    tone: str,
    language: str = "English",
) -> str:
    """
    Generate 10 creative brand name suggestions based on industry,
    keywords, and tone. Returns a JSON string [ { "name": "...", "rationale": "..." }, ... ]
    """
    system = (
        "You are a world-class brand strategist and naming expert. "
        "Generate creative, memorable, domain-friendly brand names. "
        f"Respond in {language}. Return ONLY a JSON array of objects with 'name' and 'rationale' keys."
    )
    user = (
        f"Generate 10 creative brand name ideas for a {industry} business.\n"
        f"Keywords to incorporate: {keywords}\n"
        f"Brand tone/personality: {tone}\n\n"
        "Return the response as a valid JSON array of objects. "
        "Each object should have:\n"
        "1. 'name': The brand name suggestion\n"
        "2. 'rationale': A 1-2 sentence explanation of why it works and its meaning.\n\n"
        "Do not include any other text before or after the JSON."
    )
    return await asyncio.to_thread(_groq_chat, system, user)


# ═══════════════════════════════════════════════════════════════════
# 2. MARKETING CONTENT GENERATION  (Groq)
# ═══════════════════════════════════════════════════════════════════
async def generate_marketing_content(
    brand_description: str,
    tone: str,
    content_type: str,
    language: str = "English",
) -> str:
    """
    Generate marketing copy (taglines, social posts, product descriptions,
    email campaigns, ad copy, etc.) for a given brand and content type.
    """
    system = (
        "You are an expert marketing copywriter and brand storyteller. "
        "Write compelling, conversion-focused marketing content. "
        f"Respond in {language}."
    )
    user = (
        f"Brand description: {brand_description}\n"
        f"Tone of voice: {tone}\n"
        f"Content type requested: {content_type}\n\n"
        "Create high-quality marketing content that perfectly captures "
        "the brand essence. Include multiple variations where applicable."
    )
    return await asyncio.to_thread(_groq_chat, system, user, 0.85)


# ═══════════════════════════════════════════════════════════════════
# 3. LOGO PROMPT GENERATION  (Groq → feeds into SDXL)
# ═══════════════════════════════════════════════════════════════════
async def generate_logo_prompt(
    brand_name: str,
    industry: str,
    keywords: str,
    description: str = "",
) -> str:
    """
    Generate a rich Stable Diffusion XL prompt for logo creation
    based on brand name, industry, keywords, and optional description.
    """
    system = (
        "You are an expert at translating brand missions into SINGLE, RECOGNIZABLE objects. "
        "Your goal is to pick ONE literal, iconic metaphor that communicates 'Education', 'Free', or 'Knowledge'."
        "Avoid any abstract or complex descriptions. Output MUST be short and direct."
    )
    user = (
        f"Brand Name: {brand_name}\n"
        f"Mission: {description}\n"
        f"Industry/Keywords: {industry}, {keywords}\n\n"
        "Strategic Metaphor Options for 'Free Education' and 'Students':\n"
        "- 'An open book where the pages turn into a flight bird'\n"
        "- 'A graduation mortarboard cap with an unlocked padlock'\n"
        "- 'A lightbulb with a pencil tip as the filament'\n"
        "- 'A single, vibrant open book with a rising sun inside'\n\n"
        "Pick ONE of these or something equally LITERAL. Do NOT use abstract circles or blobs.\n"
        "Describe ONLY the object and its primary color (e.g., 'A vibrant blue open book with a golden sun rising from its center')."
    )
    return await asyncio.to_thread(_groq_chat, system, user, 0.7)


# ═══════════════════════════════════════════════════════════════════
# 4. COLOR PALETTE GENERATION  (Groq)
# ═══════════════════════════════════════════════════════════════════
async def get_color_palette(tone: str, industry: str) -> dict:
    """
    Generate a complete brand color palette with HEX codes and usage guidance
    based on brand tone and industry.
    Returns a dict with palette info.
    """
    system = (
        "You are a professional brand designer and color psychology expert. "
        "Generate precise, visually harmonious color palettes for brands. "
        "Always respond with valid JSON only."
    )
    user = (
        f"Create a complete brand color palette for a {industry} brand with a {tone} tone.\n\n"
        "Respond with ONLY this JSON structure (no extra text):\n"
        "{\n"
        '  "primary": {"hex": "#XXXXXX", "name": "Color Name", "usage": "Main brand color, CTAs"},\n'
        '  "secondary": {"hex": "#XXXXXX", "name": "Color Name", "usage": "Supporting elements"},\n'
        '  "accent": {"hex": "#XXXXXX", "name": "Color Name", "usage": "Highlights, hovers"},\n'
        '  "background": {"hex": "#XXXXXX", "name": "Color Name", "usage": "Page backgrounds"},\n'
        '  "text": {"hex": "#XXXXXX", "name": "Color Name", "usage": "Body text"},\n'
        '  "rationale": "1-2 sentence explanation of the palette psychology"\n'
        "}"
    )
    raw = await asyncio.to_thread(_groq_chat, system, user, 0.6)
    # Extract JSON block from the response
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"raw": raw}


# ═══════════════════════════════════════════════════════════════════
# 5. SENTIMENT ANALYSIS  (Groq)
# ═══════════════════════════════════════════════════════════════════
async def analyze_sentiment(text: str, brand_tone: str) -> dict:
    """
    Analyze the sentiment, emotional tone, and brand alignment of a tagline
    or marketing text. Returns structured analysis.
    """
    system = (
        "You are a brand analyst and NLP specialist with expertise in consumer "
        "psychology and brand perception. Always respond with valid JSON only."
    )
    user = (
        f"Analyze this marketing text for sentiment and brand fit:\n"
        f'Text: "{text}"\n'
        f"Target brand tone: {brand_tone}\n\n"
        "Respond with ONLY this JSON (no extra text):\n"
        "{\n"
        '  "overall_sentiment": "Positive/Negative/Neutral",\n'
        '  "sentiment_score": 0.85,\n'
        '  "emotions": ["confidence", "innovation", "trust"],\n'
        '  "brand_alignment_score": 0.9,\n'
        '  "strengths": ["Clear value proposition", "Memorable"],\n'
        '  "improvements": ["Could be more action-oriented"],\n'
        '  "recommendation": "One sentence recommendation"\n'
        "}"
    )
    raw = await asyncio.to_thread(_groq_chat, system, user, 0.5)
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"raw": raw}


# ═══════════════════════════════════════════════════════════════════
# 6. TAGLINE GENERATION  (Groq)
# ═══════════════════════════════════════════════════════════════════
async def generate_taglines(
    brand_name: str,
    industry: str,
    tone: str,
    language: str = "English",
) -> str:
    """Generate 10 creative taglines for a brand."""
    system = (
        "You are a world-class brand copywriter specializing in memorable taglines. "
        f"Respond in {language}."
    )
    user = (
        f"Generate 10 powerful tagline options for:\n"
        f"Brand: {brand_name}\n"
        f"Industry: {industry}\n"
        f"Tone: {tone}\n\n"
        "Each tagline should be:\n"
        "- Under 7 words\n"
        "- Memorable and emotionally resonant\n"
        "- Different style per option (inspirational, bold, witty, minimal, etc.)\n\n"
        "Format: numbered list with a brief style label for each."
    )
    return await asyncio.to_thread(_groq_chat, system, user)


# ═══════════════════════════════════════════════════════════════════
# 7. BRAND STORY GENERATION  (Groq)
# ═══════════════════════════════════════════════════════════════════
async def generate_brand_story(
    brand_name: str,
    industry: str,
    mission: str,
    tone: str,
    language: str = "English",
) -> str:
    """Generate a compelling brand story / About Us narrative."""
    system = (
        "You are a master brand storyteller with expertise in brand narrative and identity. "
        f"Respond in {language}."
    )
    user = (
        f"Write a compelling brand story for:\n"
        f"Brand: {brand_name}\n"
        f"Industry: {industry}\n"
        f"Mission/Values: {mission}\n"
        f"Tone: {tone}\n\n"
        "Structure:\n"
        "1. The Problem (why we exist)\n"
        "2. Our Vision (what we believe)\n"
        "3. Our Approach (how we're different)\n"
        "4. The Promise (what customers can expect)\n\n"
        "Aim for 250-350 words. Make it emotionally engaging."
    )
    return await asyncio.to_thread(_groq_chat, system, user, 0.9)


# ═══════════════════════════════════════════════════════════════════
# 8. SOCIAL MEDIA POST GENERATION  (Groq)
# ═══════════════════════════════════════════════════════════════════
async def generate_social_posts(
    brand_name: str,
    product_description: str,
    platform: str,
    tone: str,
    language: str = "English",
) -> str:
    """Generate platform-specific social media posts."""
    system = (
        f"You are a social media expert and content strategist specializing in {platform}. "
        f"Respond in {language}."
    )
    user = (
        f"Create 5 engaging {platform} posts for:\n"
        f"Brand: {brand_name}\n"
        f"Product/Service: {product_description}\n"
        f"Tone: {tone}\n\n"
        f"Each post must:\n"
        f"- Be optimized for {platform} format and character limits\n"
        f"- Include relevant hashtags\n"
        f"- Include an emoji where appropriate\n"
        f"- Have a clear call-to-action\n\n"
        f"Number each post 1-5."
    )
    return await asyncio.to_thread(_groq_chat, system, user, 0.88)


# ═══════════════════════════════════════════════════════════════════
# 9. PRODUCT DESCRIPTION GENERATION  (Groq)
# ═══════════════════════════════════════════════════════════════════
async def generate_product_description(
    product_name: str,
    features: str,
    target_audience: str,
    tone: str,
    language: str = "English",
) -> str:
    """Generate a compelling product description."""
    system = (
        "You are an expert e-commerce copywriter who creates high-converting product descriptions. "
        f"Respond in {language}."
    )
    user = (
        f"Write a compelling product description for:\n"
        f"Product: {product_name}\n"
        f"Key Features: {features}\n"
        f"Target Audience: {target_audience}\n"
        f"Tone: {tone}\n\n"
        "Include:\n"
        "- A punchy headline\n"
        "- 2-3 sentence overview paragraph\n"
        "- 5 key feature bullet points\n"
        "- A persuasive closing CTA paragraph\n"
        "- SEO-friendly structure"
    )
    return await asyncio.to_thread(_groq_chat, system, user, 0.8)


# ═══════════════════════════════════════════════════════════════════
# 10. IBM GRANITE CHATBOT  (HuggingFace Inference API)
# ═══════════════════════════════════════════════════════════════════
# Conversation history stored per session (in-memory for demo)
_chat_histories: dict[str, list[dict]] = {}


async def chat_with_ai(
    user_message: str,
    session_id: str = "default",
    system_context: str = "",
) -> str:
    """
    Multi-turn branding AI chatbot powered by IBM Granite 3.3-8B-Instruct.
    Maintains per-session conversation history for context continuity.
    """
    if session_id not in _chat_histories:
        _chat_histories[session_id] = []

    history = _chat_histories[session_id]

    default_system = (
        "You are BrandBot, an expert AI branding consultant powered by IBM Granite. "
        "You specialize in brand strategy, naming, marketing, logo design, color psychology, "
        "and brand identity creation. You are helpful, concise, and always provide actionable advice. "
        "You assist startups and small businesses build powerful brand identities."
    )
    system_prompt = system_context if system_context else default_system

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-10:])  # keep last 5 turns for context window
    messages.append({"role": "user", "content": user_message})

    def _call_chat():
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=512,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()

    reply = await asyncio.to_thread(_call_chat)

    # Update conversation history
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    _chat_histories[session_id] = history[-20:]  # cap at 10 turns

    return reply


def clear_chat_history(session_id: str = "default") -> None:
    """Clear the conversation history for a given session."""
    _chat_histories.pop(session_id, None)


# ═══════════════════════════════════════════════════════════════════
# 11. LOGO GENERATION — Stable Diffusion XL  (HuggingFace)
# ═══════════════════════════════════════════════════════════════════
async def generate_logo_image(
    brand_name: str,
    industry: str,
    style_keywords: str,
    filename: str = "logo.png",
    description: str = "",
) -> str:
    """
    Generate a brand logo using Stable Diffusion XL via HuggingFace Inference API.
    First generates an optimized SDXL prompt via Groq, then creates the image.
    Returns the relative URL path to the saved logo file.
    """
    # Step 1: Generate optimised image prompt via Groq
    sd_prompt = await generate_logo_prompt(brand_name, industry, style_keywords, description)

    # Forcefully construct a singular icon prompt
    enhanced_prompt = (
        "A minimalist flat vector logo icon of "
        f"{sd_prompt}, "
        "centered on a solid white background, isolated, "
        "professional branding, high contrast, clean lines, "
        "masterpiece, high quality, no text, no words, no letters, "
        "no grid, no multiple icons, one single icon only, 8k"
    )
    negative_prompt = (
        "grid, multiple versions, variants, collection, sheet, collage, blurry, text, "
        "lettering, font, signature, messy background, low resolution, multiple icons, "
        "borders, frames, dark background, shadow, photo, 3d render"
    )

    image: Image.Image = await hf_client.text_to_image(
        model="stabilityai/stable-diffusion-xl-base-1.0",
        prompt=enhanced_prompt,
        negative_prompt=negative_prompt,
        width=512,
        height=512,
    )

    # Save to static/logos/
    safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", filename)
    if not safe_name.endswith(".png"):
        safe_name += ".png"
    save_path = LOGO_DIR / safe_name
    image.save(save_path, "PNG")

    return f"/static/logos/{safe_name}"


# ═══════════════════════════════════════════════════════════════════
# 12. VOICE TRANSCRIPTION  (Groq Whisper)
# ═══════════════════════════════════════════════════════════════════
async def transcribe_voice(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Transcribe voice input using Groq's hosted Whisper model.
    Accepts raw audio bytes and returns transcribed text.
    """
    def _transcribe():
        transcription = groq_client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=(filename, audio_bytes, "audio/webm"),
        )
        return transcription.text

    return await asyncio.to_thread(_transcribe)


# ═══════════════════════════════════════════════════════════════════
# 13. COMPETITOR ANALYSIS  (Groq)
# ═══════════════════════════════════════════════════════════════════
async def analyze_competitors(
    brand_name: str,
    industry: str,
    target_market: str,
    language: str = "English",
) -> str:
    """Provide competitive landscape analysis and differentiation strategies."""
    system = (
        "You are a strategic business analyst specializing in competitive brand positioning. "
        f"Respond in {language}."
    )
    user = (
        f"Provide a competitive brand analysis for:\n"
        f"Brand: {brand_name}\n"
        f"Industry: {industry}\n"
        f"Target Market: {target_market}\n\n"
        "Include:\n"
        "1. Key competitors and their brand positioning\n"
        "2. Market gaps and opportunities\n"
        "3. Unique differentiation angles for {brand_name}\n"
        "4. Recommended brand positioning statement\n"
        "5. 3 strategic recommendations"
    )
    return await asyncio.to_thread(_groq_chat, system, user, 0.75)


# ═══════════════════════════════════════════════════════════════════
# 14. EMAIL CAMPAIGN GENERATION  (Groq)
# ═══════════════════════════════════════════════════════════════════
async def generate_email_campaign(
    brand_name: str,
    campaign_goal: str,
    product_service: str,
    tone: str,
    language: str = "English",
) -> str:
    """Generate a complete email marketing campaign sequence."""
    system = (
        "You are an expert email marketing strategist. "
        f"Respond in {language}."
    )
    user = (
        f"Create a 3-email marketing campaign sequence for:\n"
        f"Brand: {brand_name}\n"
        f"Campaign Goal: {campaign_goal}\n"
        f"Product/Service: {product_service}\n"
        f"Tone: {tone}\n\n"
        "For each email provide:\n"
        "- Subject line (with open-rate optimization)\n"
        "- Preview text\n"
        "- Email body (200-300 words)\n"
        "- CTA button text\n\n"
        "Label clearly: Email 1 (Welcome/Intro), Email 2 (Value/Education), Email 3 (Conversion)"
    )
    return await asyncio.to_thread(_groq_chat, system, user, 0.82)


# ═══════════════════════════════════════════════════════════════════
# 15. BRAND GUIDELINES DOCUMENT  (Groq)
# ═══════════════════════════════════════════════════════════════════
async def generate_brand_guidelines(
    brand_name: str,
    industry: str,
    mission: str,
    tone: str,
    color_palette: str,
    language: str = "English",
) -> str:
    """Generate a comprehensive brand guidelines document."""
    system = (
        "You are a brand identity designer creating professional brand guidelines. "
        f"Respond in {language}."
    )
    user = (
        f"Create comprehensive brand guidelines for:\n"
        f"Brand: {brand_name}\n"
        f"Industry: {industry}\n"
        f"Mission: {mission}\n"
        f"Tone of Voice: {tone}\n"
        f"Color Palette: {color_palette}\n\n"
        "Include sections:\n"
        "1. Brand Mission & Vision\n"
        "2. Core Values (5 values with descriptions)\n"
        "3. Logo Usage Rules\n"
        "4. Color System & Usage\n"
        "5. Typography Guidelines\n"
        "6. Tone of Voice & Messaging\n"
        "7. Do's and Don'ts"
    )
    return await asyncio.to_thread(_groq_chat, system, user, 0.72)
