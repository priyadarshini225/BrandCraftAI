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
from huggingface_hub import AsyncInferenceClient
from PIL import Image
import requests
import asyncio
import time

load_dotenv()

# ─── Clients ────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HF_API_KEY   = os.getenv("HF_API_KEY", "")
WHOISFREAKS_API_KEY = os.getenv("WHOISFREAKS_API_KEY", "")

hf_client   = AsyncInferenceClient(token=HF_API_KEY)

# IBM Granite model ID on Hugging Face
GRANITE_MODEL = "ibm-granite/granite-3.3-8b-instruct"

# Static logo output directory (served via FastAPI)
LOGO_DIR = Path(__file__).parent / "static" / "logos"
LOGO_DIR.mkdir(parents=True, exist_ok=True)
MOOD_DIR = Path(__file__).parent / "static" / "moodboard"
MOOD_DIR.mkdir(parents=True, exist_ok=True)
DECK_DIR = Path(__file__).parent / "static" / "decks"
DECK_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════
# HELPER: call Groq via REST (avoids httpx version issues)
# ═══════════════════════════════════════════════════════════════════
def _groq_chat(system_prompt: str, user_prompt: str, temperature: float = 0.8, max_tokens: int = 1024) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    return (data.get("choices", [{}])[0]
               .get("message", {})
               .get("content", "")
               .strip())

def _groq_chat_messages(messages: list[dict], temperature: float = 0.7, max_tokens: int = 512) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    return (data.get("choices", [{}])[0]
               .get("message", {})
               .get("content", "")
               .strip())


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
        return _groq_chat_messages(messages, temperature=0.7, max_tokens=512)

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
    minimalism: int | None = None,
    complexity: int | None = None,
    vibrancy: int | None = None,
) -> str:
    """
    Generate a brand logo using Stable Diffusion XL via HuggingFace Inference API.
    First generates an optimized SDXL prompt via Groq, then creates the image.
    Returns the relative URL path to the saved logo file.
    """
    # Step 1: Generate optimised image prompt via Groq
    sd_prompt = await generate_logo_prompt(brand_name, industry, style_keywords, description)

    # Forcefully construct a singular icon prompt
    extra_keywords = []
    if isinstance(minimalism, int) and minimalism >= 80:
        extra_keywords += ["vector", "flat design", "simple lines", "white background"]
    if isinstance(vibrancy, int) and vibrancy >= 80:
        extra_keywords += ["neon", "high contrast", "bold colors"]
    if isinstance(complexity, int) and complexity >= 80:
        extra_keywords += ["intricate details", "ornate", "complex geometry"]
    if isinstance(complexity, int) and complexity <= 20:
        extra_keywords += ["ultra minimal", "few elements", "monoline"]

    enhanced_prompt = (
        "A minimalist flat vector logo icon of "
        f"{sd_prompt}, " +
        (", ".join(extra_keywords) + ", " if extra_keywords else "") +
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
# 11b. MOODBOARD GENERATION — 4 parallel SDXL calls
# ═══════════════════════════════════════════════════════════════════
async def generate_moodboard(archetype: str, colors: str, brand_name: str | None = None) -> dict:
    """
    Generate 4 images for a moodboard: Texture/Pattern, Lifestyle/Environment,
    Typography Style, and Product Mockup. Returns dict with public URLs.
    """
    archetype = (archetype or "").strip() or "Minimalist"
    colors = (colors or "").strip() or "neutral, #111827, #e5e7eb, accent #7c3aed"

    prompts = {
        "texture": f"{archetype} brand texture or pattern, seamless, {colors}, ultra clean, elegant, minimal, 4k, studio lighting",
        "lifestyle": f"{archetype} lifestyle scene / environment embodying the brand mood, {colors}, editorial photography, shallow depth of field, cinematic lighting, 4k",
        "typography": f"{archetype} typography exploration, letterforms, type specimens on a poster, {colors}, graphic design poster, clean layout, high contrast, 4k",
        "mockup": f"{archetype} brand product mockup on neutral background, {colors}, studio shot, product photography, soft shadows, 4k",
    }

    async def _gen(kind: str, prompt: str) -> str:
        img: Image.Image = await hf_client.text_to_image(
            model="stabilityai/stable-diffusion-xl-base-1.0",
            prompt=prompt,
            width=768,
            height=768,
        )
        ts = int(time.time()*1000)
        base = f"{(brand_name or 'brand').lower().replace(' ', '_')}_{kind}_{ts}.png"
        save_path = MOOD_DIR / base
        img.save(save_path, "PNG")
        return f"/static/moodboard/{base}"

    texture_url, lifestyle_url, typography_url, mockup_url = await asyncio.gather(
        _gen("texture", prompts["texture"]),
        _gen("lifestyle", prompts["lifestyle"]),
        _gen("typography", prompts["typography"]),
        _gen("mockup", prompts["mockup"]),
    )

    return {
        "texture": texture_url,
        "lifestyle": lifestyle_url,
        "typography": typography_url,
        "mockup": mockup_url,
        "archetype": archetype,
        "colors": colors,
    }


# ═══════════════════════════════════════════════════════════════════
# 12. VOICE TRANSCRIPTION  (Groq Whisper)
# ═══════════════════════════════════════════════════════════════════
async def transcribe_voice(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Transcribe voice input using Groq's hosted Whisper model.
    Accepts raw audio bytes and returns transcribed text.
    """
    def _transcribe():
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = { "Authorization": f"Bearer {GROQ_API_KEY}" }
        files = {
            "file": (filename, audio_bytes, "audio/webm"),
            "model": (None, "whisper-large-v3"),
        }
        r = requests.post(url, headers=headers, files=files, timeout=120)
        r.raise_for_status()
        data = r.json()
        # OpenAI-style returns 'text'
        return data.get("text", "")

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
# 13b. MARKET CHECK PIPELINE — Scraper + Differentiation + Risk
# ═══════════════════════════════════════════════════════════════════
def _extract_html_fields(html: str) -> dict:
    title = ""
    desc = ""
    try:
        mt = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if mt:
            title = re.sub(r"\s+", " ", mt.group(1)).strip()
        md = re.search(
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
            html, re.IGNORECASE | re.DOTALL
        )
        if md:
            desc = re.sub(r"\s+", " ", md.group(1)).strip()
    except Exception:
        pass

    styles = []
    for m in re.finditer(r"<style[^>]*>([\s\S]*?)</style>", html, re.IGNORECASE):
        styles.append(m.group(1))
    for m in re.finditer(r'style\s*=\s*"(.*?)"', html, re.IGNORECASE | re.DOTALL):
        styles.append(m.group(1))
    # Extract hex colors
    hexes = set()
    for block in styles:
        for hx in re.findall(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b", block):
            # normalize short to long (e.g. #abc -> #aabbcc)
            if len(hx) == 4:
                hx = "#" + "".join(ch*2 for ch in hx[1:])
            hexes.add(hx.lower())
    primary_hexes = sorted(hexes)
    return {"title": title, "meta_description": desc, "hex_codes": primary_hexes}


async def scrape_competitors(urls: list[str]) -> list[dict]:
    """Fetch competitor pages and extract <title>, meta description, and CSS hex codes."""
    def _fetch(url: str) -> dict:
        try:
            resp = requests.get(url, timeout=15, headers={"User-Agent": "BrandCraftAI/1.0"})
            if resp.status_code >= 400:
                return {"url": url, "error": f"HTTP {resp.status_code}"}
            data = _extract_html_fields(resp.text or "")
            data["url"] = url
            return data
        except Exception as e:
            return {"url": url, "error": str(e)}

    tasks = [asyncio.to_thread(_fetch, u) for u in urls or []]
    if not tasks:
        return []
    return await asyncio.gather(*tasks)


async def suggest_positioning_from_competitors(scraped: list[dict]) -> str:
    summary = json.dumps(scraped, ensure_ascii=False)[:8000]
    system = "You are a senior brand strategist. Provide crisp, actionable brand positioning."
    user = (
        "Given these competitors (titles, meta descriptions, colors):\n"
        f"{summary}\n\n"
        "Suggest a differentiated brand positioning statement and 3-5 gap opportunities they are missing.\n"
        "Return a concise Markdown with sections: Positioning, Gaps, Notes."
    )
    return await asyncio.to_thread(_groq_chat, system, user, 0.6)


def _whois_via_api(domain: str) -> bool | None:
    """Return True if available, False if taken, None if unknown."""
    if not WHOISFREAKS_API_KEY:
        return None
    try:
        r = requests.get(f"https://api.whoisfreaks.com/v1.0/whois", params={
            "whois": "live",
            "apiKey": WHOISFREAKS_API_KEY,
            "domain": domain,
        }, timeout=12)
        if r.status_code != 200:
            return None
        data = r.json()
        # Heuristic: if domain_name/created_date present, assume registered
        registered = bool(data.get("domain_name") or data.get("created_date") or data.get("registry_data"))
        return False if registered else True
    except Exception:
        return None


def _whois_local(domain: str) -> bool | None:
    """Use python-whois; True if available (no record), False if registered, None on error."""
    try:
        import whois  # type: ignore
        w = whois.whois(domain)
        # When domain is not registered, many providers raise or return mostly None
        if not w or all(
            not getattr(w, k, None)
            for k in ("domain_name", "creation_date", "registrar")
        ):
            return True
        return False
    except Exception:
        return None


async def check_domain_availability(brand_name: str, tlds: list[str] | None = None) -> dict:
    name = re.sub(r"[^a-z0-9]+", "", brand_name.lower())
    tlds = tlds or [".com", ".ai", ".co"]
    results = {}
    for tld in tlds:
        dom = name + tld
        avail = _whois_via_api(dom)
        if avail is None:
            avail = _whois_local(dom)
        results[dom] = {"available": avail}
    return results


async def detect_name_risk(brand_name: str) -> dict:
    system = (
        "You are a linguistic risk analyst. Detect if a brand name has negative or vulgar slang meanings "
        "in major languages (Spanish, French, Hindi, Mandarin)."
    )
    user = (
        f'Brand name: "{brand_name}"\n\n'
        "Return JSON with:\n"
        '{ "flagged": true|false, "languages": [{ "lang": "...", "issue": "...", "severity": "low|med|high" }], "notes": "..." }\n'
        "Flag true only if there is a plausible negative slang or offensive meaning."
    )
    raw = await asyncio.to_thread(_groq_chat, system, user, 0.2)
    try:
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {"raw": raw}


async def market_check(brand_name: str, competitor_urls: list[str], tlds: list[str] | None = None) -> dict:
    scraped = await scrape_competitors(competitor_urls)
    positioning = await suggest_positioning_from_competitors(scraped)
    domains = await check_domain_availability(brand_name, tlds)
    risk = await detect_name_risk(brand_name)
    return {
        "brand_name": brand_name,
        "competitors": scraped,
        "positioning": positioning,
        "domains": domains,
        "name_risk": risk,
    }


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


# ═══════════════════════════════════════════════════════════════════
# 16. PITCH DECK (Groq text → python-pptx)
# ═══════════════════════════════════════════════════════════════════
async def generate_pitch_deck_text(brand_name: str, brand_dna: str) -> dict:
    system = "You are a world-class startup pitch writer and brand strategist."
    user = (
        f'Create concise slide content for 7 slides for brand "{brand_name}".\n'
        f"Brand DNA: {brand_dna}\n\n"
        "Slides: Problem, Solution, Market, Revenue, Team, Vision, Branding.\n"
        "Return JSON: { slides: { Problem: '...', Solution: '...', ... } } with punchy, slide-ready bullets."
    )
    raw = await asyncio.to_thread(_groq_chat, system, user, 0.7)
    try:
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    # Fallback to wrap as text
    return {"slides": {"Raw": raw}}


async def build_pitch_deck_pptx(slide_map: dict, primary_hex: str = "#7C3AED", secondary_hex: str = "#06B6D4") -> str:
    """
    Build a .pptx file using python-pptx with brand colors applied.
    Returns the public URL path to the saved PPTX.
    """
    try:
        from pptx import Presentation  # type: ignore
        from pptx.util import Inches, Pt  # type: ignore
        from pptx.dml.color import RGBColor  # type: ignore
    except Exception:
        # Dependency missing; return error marker
        raise RuntimeError("python-pptx is not installed")

    def _rgb(hexstr: str):
        hx = hexstr.lstrip("#")
        if len(hx) == 3:
            hx = "".join(ch*2 for ch in hx)
        r = int(hx[0:2], 16); g = int(hx[2:4], 16); b = int(hx[4:6], 16)
        return RGBColor(r, g, b)

    prs = Presentation()
    # Apply a simple layout per slide: title + body
    for title, body in slide_map.items():
        slide = prs.slides.add_slide(prs.slide_layouts[1])  # Title and Content
        slide.shapes.title.text = str(title)
        tf = slide.shapes.placeholders[1].text_frame
        tf.clear()
        for line in str(body).split("\n"):
            p = tf.add_paragraph()
            p.text = line.strip()
            p.level = 0
        # Color accents
        for shape in slide.shapes:
            try:
                fill = shape.fill
                if not fill:
                    continue
                fill.solid()
                fill.fore_color.rgb = _rgb(primary_hex)
                # Make it subtle for content placeholders
                if shape.has_text_frame:
                    fill.transparency = 0.92
            except Exception:
                continue
        # Title color
        try:
            title_shape = slide.shapes.title
            for r in title_shape.text_frame.paragraphs:
                for run in r.runs:
                    run.font.color.rgb = _rgb(secondary_hex)
                    run.font.size = Pt(40)
        except Exception:
            pass

    fname = f"pitch_{int(time.time())}.pptx"
    save_path = DECK_DIR / fname
    prs.save(save_path)
    return f"/static/decks/{fname}"


# ═══════════════════════════════════════════════════════════════════
# 17. CONSISTENCY VALIDATOR (Text via Granite; Image via BLIP + Granite)
# ═══════════════════════════════════════════════════════════════════
async def validate_consistency(brand_dna: str, about_text: str | None = None, image_bytes: bytes | None = None) -> dict:
    description = None
    if image_bytes:
        try:
            # Caption the image first
            caption = await hf_client.image_to_text(
                model="Salesforce/blip-image-captioning-large",
                image=image_bytes,
            )
            # HF may return a list of dicts or a string
            if isinstance(caption, list) and caption and isinstance(caption[0], dict):
                description = str(caption[0].get("generated_text") or caption[0].get("caption") or "")
            else:
                description = str(caption)
        except Exception:
            # Fallback: still proceed with a generic caption so the evaluation runs
            description = "An image was provided; auto-captioning unavailable."

    # Build prompt input
    content = about_text or description or ""
    if not content:
        content = "An image was provided; no text available."

    prompt = (
        "Assess consistency of the input against the Brand DNA.\n"
        f"Brand DNA: {brand_dna}\n"
        f"Input: {content}\n\n"
        "Return JSON only: { "
        '"score": 0-100, '
        '"verdict": "On-brand/Off-brand/Mixed", '
        '"reasons": ["...","...","..."], '
        '"fixes": ["...","..."] }'
    )

    # Use Granite model via Hugging Face for text generation
    try:
        granite = await hf_client.text_generation(
            model=GRANITE_MODEL,
            prompt=prompt,
            max_new_tokens=256,
            temperature=0.2,
        )
        raw = granite
        if isinstance(granite, dict) and "generated_text" in granite:
            raw = granite["generated_text"]
        match = re.search(r"\{[\s\S]*\}", str(raw))
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    # Fallback to Groq if Granite path fails
    raw = await asyncio.to_thread(_groq_chat, "You are a brand consistency evaluator.", prompt, 0.2)
    try:
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {"raw": raw}
