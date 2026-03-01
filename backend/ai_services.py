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
from huggingface_hub import AsyncInferenceClient, InferenceClient
from PIL import Image
import requests
import asyncio
import time

load_dotenv()

# ─── Clients ────────────────────────────────────────────────────────────────
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
HF_API_KEY     = os.getenv("HF_API_KEY", "")
WHOISFREAKS_API_KEY = os.getenv("WHOISFREAKS_API_KEY", "")

hf_client      = AsyncInferenceClient(token=HF_API_KEY)
hf_sync_client = InferenceClient(token=HF_API_KEY)  # sync, for use inside threads

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
        "the brand essence. Include multiple variations where applicable.\n"
        "IMPORTANT: Generate ONLY the exact 'Content type requested'. "
        "For example, if asked for Slogans, generate only slogans with it's description(which clearly explains or defines that slogan), do NOT generate Taglines"
    )
    return await asyncio.to_thread(_groq_chat, system, user, 0.85)


# ═══════════════════════════════════════════════════════════════════
# 3. LOGO PROMPT GENERATION  (Groq → structured preview prompt)
# ═══════════════════════════════════════════════════════════════════
async def generate_logo_prompt(
    brand_name: str,
    industry: str,
    keywords: str,
    description: str = "",
    mood: str = "",
    asset_type: str = "",
    typography: str = "",
    icon_style: str = "",
) -> str:
    """
    Generate a structured Gemini logo prompt (for user preview).
    """
    system = (
        "You are a professional logo designer. Write a precise image generation prompt "
        "for creating a professional logo. Specify: one clear icon/symbol concept, "
        "typography style, color palette, visual style, and white background. "
        "Be specific and concise. Output the prompt only, no explanation."
    )
    user = (
        f"Brand Name: {brand_name}\n"
        f"Industry: {industry}\n"
        f"Style Keywords: {keywords or 'minimalist, modern, clean'}\n"
        f"Mood: {mood or 'professional, trustworthy, memorable'}\n"
        f"Design Concept: {description or 'none'}\n"
        f"Asset Type Required: {asset_type or 'Flat Vector Logo'}\n"
        f"Typography Preference: {typography or 'Any'}\n"
        f"Icon Style Preference: {icon_style or 'Any'}\n\n"
        "Write a detailed logo generation prompt specifying: the exact icon/symbol, "
        "typography style, colors, flat/vector style, white background. "
        f'IMPORTANT: Explicitly state the exact brand name \\"{brand_name}\\" to ensure correct spelling in text/typography. '
        "Pay special attention to matching the Asset Type, Typography Preference, and Icon Style Preference."
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
# 11. LOGO GENERATION — Pollinations.ai (FLUX, completely free, no key)
# ═══════════════════════════════════════════════════════════════════
async def generate_logo_image(
    brand_name: str,
    industry: str,
    style_keywords: str,
    filename: str = "logo.png",
    description: str = "",
    mood: str = "",
    asset_type: str = "",
    typography: str = "",
    icon_style: str = "",
    minimalism: int | None = None,
    complexity: int | None = None,
    vibrancy: int | None = None,
) -> str:
    """
    Generate a brand logo image.
    Primary: HuggingFace FLUX.1-schnell (uses HF_API_KEY).
    Fallback: Pollinations.ai (free, no key).
    Returns the relative URL path to the saved logo file.
    """
    import urllib.parse
    import time

    # ----- Build a structured FLUX prompt via Groq (ChatGPT-level quality) -----
    _sys = (
        "You are a logo prompt engineer specialized in HuggingFace FLUX.1-schnell image generation. "
        "When given brand parameters, restructure them into ONE optimized FLUX prompt under 80 words. "
        "\n\nALWAYS follow this exact structure:\n"
        "[Render style] + [white background] + [icon description with colors] + "
        "[typography instruction] + [exact hex color codes] + [layout] + [mood/style tags]\n"
        "\nRULES:\n"
        "- Use hex codes directly (e.g. #0A1628, #00D4FF)\n"
        "- Specify spatial relationships (left icon, right text / icon above text)\n"
        "- Name exact font feel (Futura-style, geometric sans-serif, Neue Haas-like)\n"
        "- Say what NOT to include: no gradients, no shadows, no decorative elements\n"
        "- End with 2-3 style tags: e.g. minimal, flat vector, MedTech\n"
        "- IMPORTANT: You MUST include the exact brand name in quotes in the prompt so the AI spells it correctly.\n"
        "\nEXAMPLE OUTPUT (match this quality and length):\n"
        "\"Flat vector logo on white. Hexagonal shield outline #0A1628, electric cyan #00D4FF neural "
        "pathway lines inside branching into ECG heartbeat wave at center, circuit-synapse hybrid lines. "
        "Right side: bold geometric sans-serif wordmark reading \\\"Neulite\\\", brand name bold top, tagword lightweight smaller below. "
        "No gradients, no shadows. Logomark left, wordmark right. MedTech, clinical precision, AI-forward.\"\n"
        "\nOutput ONLY the prompt string — no explanation, no quotes around it."
    )

    icon_hint = description or ""
    _usr = (
        f"Brand name: {brand_name}\n"
        f"Industry: {industry}\n"
        f"Visual style: {style_keywords or 'minimal, modern, geometric'}\n"
        + (f"Typography style: {typography}\n" if typography else "")
        + (f"Icon style: {icon_style}\n" if icon_style else "")
        + (f"Mood / feeling: {mood}\n" if mood else "")
        + (f"Icon / symbol concept: {icon_hint}\n" if icon_hint else "")
        + "Generate the optimized FLUX logo prompt following the structure above."
    )
    try:
        prompt = _groq_chat(_sys, _usr, temperature=0.65, max_tokens=180).strip().strip('"').strip("'")
        prompt = " ".join(prompt.split())
        if len(prompt) > 400:
            prompt = prompt[:397] + "..."
    except Exception:
        typo_hint = f"{typography} font, " if typography else "geometric sans-serif, "
        mood_hint = f"{mood}, " if mood else ""
        prompt = (
            f"Flat vector logo on white. {industry} brand icon. "
            f"{typo_hint}{mood_hint}no gradients, no shadows. minimal, flat vector, professional."
        )




    # Strong negative prompt — aggressively prevent text/letters in generated image
    negative = (
        "text, letters, words, typography, brand name, label, caption, watermark, "
        "signature, alphabet, numbers, font, writing, calligraphy, "
        "photo, realistic, blurry, 3d render, dark background, multiple icons"
    )

    def _try_hf_flux() -> Image.Image:
        """PRIMARY: HuggingFace FLUX.1-schnell via InferenceClient.
        Retries up to 2 times on model-loading (503/loading) errors.
        """
        import logging
        last_exc = None
        for attempt in range(2):
            try:
                logging.warning(f"[Logo] HF FLUX attempt {attempt+1}/2")
                img = hf_sync_client.text_to_image(
                    prompt,
                    model="black-forest-labs/FLUX.1-schnell",
                )
                logging.warning("[Logo] HF FLUX → SUCCESS")
                return img.convert("RGBA")
            except Exception as e:
                last_exc = e
                err = str(e).lower()
                logging.warning(f"[Logo] HF FLUX attempt {attempt+1} failed: {e}")
                if "loading" in err or "503" in err:
                    time.sleep(15)
                    continue
                break  # non-transient error — don't retry
        raise last_exc or RuntimeError("HF FLUX failed")

    def _try_pollinations() -> Image.Image:
        """FALLBACK: Pollinations.ai with FLUX model — free, no key needed."""
        import urllib.parse as _up
        import logging
        seed = int(time.time()) % 99999
        short_prompt = prompt[:200]
        url = (
            f"https://image.pollinations.ai/prompt/{_up.quote(short_prompt)}"
            f"?width=512&height=512&model=flux&nologo=true&enhance=false&seed={seed}"
        )
        logging.warning(f"[Logo] Pollinations URL len={len(url)}")
        resp = requests.get(url, timeout=90)
        logging.warning(f"[Logo] Pollinations → HTTP {resp.status_code}")
        resp.raise_for_status()
        return Image.open(BytesIO(resp.content)).convert("RGBA")


    def _local_logo_fallback() -> Image.Image:
        """
        Industry-aware PIL fallback: picks the right icon template
        based on the brand's industry/style context, then applies brand colors.

        Templates:
          health/medical  → Hexagonal shield + ECG waveform + neural lines
          tech/ai/data    → Circuit grid with connected nodes
          finance/legal   → Upward growth arrow-diamond + data nodes
          nature/food/eco → Circular leaf / organic ring
          default         → Diamond with orbiting nodes + spokes
        """
        import math
        from PIL import ImageDraw

        SIZE = 512
        cx, cy = SIZE // 2, SIZE // 2

        # ── Detect industry context ──────────────────────────────────────
        ctx = f"{industry} {style_keywords or ''} {description or ''}".lower()

        HEALTH_KW  = {"health","medical","clinic","pharma","biotech","ecg","neuro",
                      "hospital","care","therapy","wellness","medtech","diagnostic"}
        TECH_KW    = {"tech","software","ai","data","cloud","cyber","digital","saas",
                      "machine learning","neural","circuit","robot","analytics","code"}
        FINANCE_KW = {"finance","fintech","bank","invest","capital","insurance",
                      "wealth","crypto","trading","accounting","legal","consult"}
        NATURE_KW  = {"food","restaurant","organic","eco","green","sustainability",
                      "nature","garden","farm","coffee","beauty","wellness","yoga"}

        def _ctx_match(kws): return any(k in ctx for k in kws)

        if _ctx_match(HEALTH_KW):
            template = "health"
        elif _ctx_match(TECH_KW):
            template = "tech"
        elif _ctx_match(FINANCE_KW):
            template = "finance"
        elif _ctx_match(NATURE_KW):
            template = "nature"
        else:
            template = "default"

        # ── Parse brand colors ───────────────────────────────────────────
        col_str = (colors or "").lower()
        import re as _re
        parsed = []
        for h in _re.findall(r'#([0-9a-f]{6})', col_str)[:2]:
            parsed.append((int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)))
        keyword_map = {
            "red":(139,10,26),"crimson":(180,20,30),"maroon":(100,8,20),
            "navy":(10,22,40),"midnight":(10,22,40),"blue":(37,99,235),
            "indigo":(79,70,229),"violet":(109,40,217),
            "teal":(20,184,166),"cyan":(0,212,255),"electric":(0,212,255),
            "green":(5,150,105),"emerald":(0,128,0),"lime":(77,175,74),
            "purple":(124,58,237),"orange":(234,88,12),"gold":(202,138,4),
            "pink":(219,39,119),"rose":(244,63,94),
        }
        if not parsed:
            for kw, rgb in keyword_map.items():
                if kw in col_str:
                    parsed.append(rgb)
                if len(parsed) == 2:
                    break

        # Default palette per template when no colors given
        _defaults = {
            "health":  ((10,22,40),   (0,212,255)),
            "tech":    ((15,23,42),   (99,102,241)),
            "finance": ((15,30,60),   (202,138,4)),
            "nature":  ((20,83,45),   (74,222,128)),
            "default": ((30,30,60),   (139,92,246)),
        }
        p = _defaults[template]
        primary   = parsed[0] if len(parsed) >= 1 else p[0]
        secondary = parsed[1] if len(parsed) >= 2 else p[1]

        img  = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        # ════════════════════════════════════════════════════════════════
        # TEMPLATE 1 — HEALTH / MEDTECH
        # Hexagonal shield + neural lines + ECG waveform
        # ════════════════════════════════════════════════════════════════
        if template == "health":
            HEX_R = 200
            hex_pts = [(cx + HEX_R*math.cos(math.radians(i*60-30)),
                        cy + HEX_R*math.sin(math.radians(i*60-30))) for i in range(6)]
            draw.polygon(hex_pts, fill=(*primary, 255))
            draw.polygon(hex_pts, outline=(*secondary, 255), width=6)
            inn_pts = [(cx + 170*math.cos(math.radians(i*60-30)),
                        cy + 170*math.sin(math.radians(i*60-30))) for i in range(6)]
            draw.polygon(inn_pts, outline=(*secondary, 100), width=2)
            # Neural lines
            for vx, vy in hex_pts:
                bx = int(vx*0.45 + cx*0.55); by = int(vy*0.45 + cy*0.55)
                draw.line([(int(vx),int(vy)),(bx,by)], fill=(*secondary,200), width=3)
                draw.ellipse([bx-7,by-7,bx+7,by+7], fill=(*secondary,255))
                draw.ellipse([bx-3,by-3,bx+3,by+3], fill=(255,255,255,200))
                draw.line([(bx,by),(cx-25,cy)], fill=(*secondary,110), width=2)
                draw.line([(bx,by),(cx+25,cy)], fill=(*secondary,80), width=1)
            # ECG
            ecg = [(-140,0),(-80,0),(-55,0),(-45,-18),(-35,0),(-18,0),
                   (0,-75),(12,45),(22,0),(40,0),(55,-20),(70,0),(140,0)]
            draw.line([(cx+dx,cy+dy) for dx,dy in ecg], fill=(*secondary,255), width=4)

        # ════════════════════════════════════════════════════════════════
        # TEMPLATE 2 — TECH / AI / SOFTWARE
        # Circuit-board square frame + connected nodes on a grid
        # ════════════════════════════════════════════════════════════════
        elif template == "tech":
            # Outer square (rotated 45° = diamond)
            sq = 185
            sq_pts = [(cx,cy-sq),(cx+sq,cy),(cx,cy+sq),(cx-sq,cy)]
            draw.polygon(sq_pts, fill=(*primary,255))
            draw.polygon(sq_pts, outline=(*secondary,255), width=5)
            # Inner square (axis-aligned)
            i_sq = 110
            draw.rectangle([cx-i_sq,cy-i_sq,cx+i_sq,cy+i_sq],
                           outline=(*secondary,100), width=2)
            # Grid nodes at intersections
            grid_offsets = [(-75,-75),(0,-75),(75,-75),
                            (-75,0),(0,0),(75,0),
                            (-75,75),(0,75),(75,75)]
            for gx, gy in grid_offsets:
                nx, ny = cx+gx, cy+gy
                draw.ellipse([nx-8,ny-8,nx+8,ny+8], fill=(*secondary,255))
                draw.ellipse([nx-3,ny-3,nx+3,ny+3], fill=(255,255,255,200))
            # Horizontal + vertical connection lines
            for gx, gy in grid_offsets:
                for dx2, dy2 in [(75,0),(0,75)]:
                    x2, y2 = cx+gx+dx2, cy+gy+dy2
                    if any(abs(x2-cx-ox)<1 and abs(y2-cy-oy)<1
                           for ox,oy in grid_offsets):
                        draw.line([(cx+gx,cy+gy),(x2,y2)],
                                  fill=(*secondary,150), width=2)
            # Central circuit cross
            draw.line([(cx-80,cy),(cx+80,cy)], fill=(*secondary,200), width=3)
            draw.line([(cx,cy-80),(cx,cy+80)], fill=(*secondary,200), width=3)
            draw.ellipse([cx-14,cy-14,cx+14,cy+14], fill=(*secondary,255))

        # ════════════════════════════════════════════════════════════════
        # TEMPLATE 3 — FINANCE / BUSINESS / LEGAL
        # Upward triangular arrow + bar chart nodes inside shield
        # ════════════════════════════════════════════════════════════════
        elif template == "finance":
            # Rounded shield outline
            draw.ellipse([cx-200,cy-200,cx+200,cy+200], fill=(*primary,255))
            draw.ellipse([cx-200,cy-200,cx+200,cy+200],
                         outline=(*secondary,255), width=5)
            draw.ellipse([cx-165,cy-165,cx+165,cy+165],
                         outline=(*secondary,80), width=2)
            # Rising arrow (upward triangle)
            arrow_pts = [(cx, cy-130),(cx-90, cy+80),(cx+90, cy+80)]
            draw.polygon(arrow_pts, fill=(*secondary,255))
            # Bar chart lines inside arrow
            bars = [(-55,60,20),(-20,80,50),(20,100,80),(55,60,20)]
            for bx_off, h, w in bars:
                bx = cx + bx_off
                draw.rectangle([bx-10, cy+80-h, bx+10, cy+80],
                               fill=(*primary,220))
            # Node dots on upward trend line
            trend = [(cx-80,cy+50),(cx-40,cy+10),(cx,cy-40),(cx+40,cy-90)]
            draw.line(trend, fill=(255,255,255,200), width=3)
            for tx,ty in trend:
                draw.ellipse([tx-7,ty-7,tx+7,ty+7], fill=(255,255,255,255))

        # ════════════════════════════════════════════════════════════════
        # TEMPLATE 4 — NATURE / FOOD / ECO / WELLNESS
        # Circular ring + stylized leaf in center
        # ════════════════════════════════════════════════════════════════
        elif template == "nature":
            # Outer ring
            draw.ellipse([cx-200,cy-200,cx+200,cy+200],
                         outline=(*secondary,255), width=8)
            draw.ellipse([cx-170,cy-170,cx+170,cy+170],
                         outline=(*secondary,80), width=2)
            # Inner filled circle
            draw.ellipse([cx-140,cy-140,cx+140,cy+140], fill=(*primary,255))
            # Leaf shape (two arcs meeting at top and bottom)
            leaf_pts = []
            for i in range(20):
                t = i / 19
                angle = math.pi * t - math.pi/2
                lx = cx + int(70 * math.sin(angle * 2))
                ly = cy - int(120 * math.cos(angle))
                leaf_pts.append((lx, ly))
            for i in range(20):
                t = i / 19
                angle = math.pi * t + math.pi/2
                lx = cx + int(30 * math.sin(angle * 2))
                ly = cy - int(120 * math.cos(angle))
                leaf_pts.append((lx, ly))
            if len(leaf_pts) > 2:
                draw.polygon(leaf_pts, fill=(*secondary,230))
            # Center stem
            draw.line([(cx,cy-120),(cx,cy+40)], fill=(255,255,255,180), width=3)
            # Small circular dots around ring (natural feel)
            for i in range(8):
                angle = math.radians(i*45)
                dx2 = int(185*math.cos(angle)); dy2 = int(185*math.sin(angle))
                draw.ellipse([cx+dx2-8,cy+dy2-8,cx+dx2+8,cy+dy2+8],
                             fill=(*secondary,255))

        # ════════════════════════════════════════════════════════════════
        # TEMPLATE 5 — DEFAULT / GENERIC
        # Diamond frame + 6 orbiting nodes + spoke lines + center hub
        # ════════════════════════════════════════════════════════════════
        else:
            # Diamond (square rotated 45°)
            D = 195
            dia_pts = [(cx,cy-D),(cx+D,cy),(cx,cy+D),(cx-D,cy)]
            draw.polygon(dia_pts, fill=(*primary,255))
            draw.polygon(dia_pts, outline=(*secondary,255), width=5)
            # Inner ring
            draw.ellipse([cx-120,cy-120,cx+120,cy+120],
                         outline=(*secondary,120), width=2)
            # 6 orbiting nodes
            for i in range(6):
                angle = math.radians(i*60 - 90)
                nx = int(cx + 150*math.cos(angle))
                ny = int(cy + 150*math.sin(angle))
                draw.line([(cx,cy),(nx,ny)], fill=(*secondary,80), width=2)
                nr = 16 if i%2==0 else 11
                fill_c = primary if i%2==0 else secondary
                draw.ellipse([nx-nr,ny-nr,nx+nr,ny+nr], fill=(*fill_c,255))
                draw.ellipse([nx-5,ny-5,nx+5,ny+5], fill=(255,255,255,200))
            # Center hub
            draw.ellipse([cx-22,cy-22,cx+22,cy+22], fill=(*secondary,255))
            draw.ellipse([cx-8,cy-8,cx+8,cy+8], fill=(255,255,255,220))

        return img




    def _fetch():
        import logging
        last_err = "unknown"
        for name, fn in [
            ("HF FLUX",      _try_hf_flux),
            ("Pollinations", _try_pollinations),
        ]:
            try:
                img = fn()
                logging.warning(f"[Logo] SUCCESS via {name}")
                return img
            except Exception as e:
                last_err = str(e)
                logging.warning(f"[Logo] FAILED {name}: {e}")
                time.sleep(1)
        logging.warning(f"[Logo] All providers failed ({last_err}). Using PIL fallback.")
        return _local_logo_fallback()


    image: Image.Image = await asyncio.to_thread(_fetch)

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
