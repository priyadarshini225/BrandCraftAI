# ⬡ BizForge / BrandPilot AI
**GenAI-Powered End-to-End Branding Platform**

> Build complete brand identities in seconds using Groq LLaMA-3.3-70B, IBM Granite 3.3, and FLUX (via Pollinations.ai).

---

## 🚀 Quick Start

### Step 1 — Install Python dependencies
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### Step 2 — Add your API keys
Edit `backend/.env`:
```
GROQ_API_KEY=your_groq_api_key_here
HF_API_KEY=your_huggingface_api_key_here
```

**Get Groq API key:** https://console.groq.com → API Keys → Create Key  
**Get HuggingFace key:** https://huggingface.co → Settings → Access Tokens → New Token

### Step 3 — Start the backend
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4 — Open the frontend
Open `frontend/index.html` in your browser, or navigate to:
- Landing Page: `http://localhost:8000/app/index.html`
- AI Studio: `http://localhost:8000/app/branding.html`

---

## 🏗️ Project Structure

```
BrandCraftAI/
├── backend/
│   ├── main.py              # FastAPI routes (all POST endpoints)
│   ├── ai_services.py       # All AI model integrations
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # API keys (never commit)
│   └── static/
│       ├── logos/           # Generated logo PNG files
│       └── uploads/         # Voice audio uploads
└── frontend/
    ├── index.html           # Landing page
    ├── branding.html        # AI Studio (6-tab application)
    ├── css/
    │   └── animations.css   # @keyframe definitions only
    └── js/
        ├── api.js           # API helper functions & UI utilities
        ├── branding.js      # Studio page interactivity
        └── i18n.js          # Multilingual support (EN/ES/FR/DE/HI)
```

---

## 🤖 AI Models Used

| Feature | Model | Provider |
|---------|-------|----------|
| Brand Names, Taglines, Content | LLaMA-3.3-70B | Groq Cloud |
| Branding Chatbot | IBM Granite 3.3-8B-Instruct | HuggingFace |
| Logo Image Generation | FLUX | Pollinations.ai |
| Voice Transcription | Whisper Large v3 | Groq Cloud |

---

## 📡 API Endpoints

All endpoints are `POST` at `http://localhost:8000` (unless marked `GET`):

| Endpoint | Description |
|----------|-------------|
| `/api/generate-brand-names` | 10 brand name ideas |
| `/api/generate-taglines` | 10 tagline variations |
| `/api/generate-brand-story` | Brand narrative/About Us |
| `/api/generate-marketing-content` | Custom marketing copy |
| `/api/generate-social-posts` | Platform-specific social posts |
| `/api/generate-product-description` | E-commerce product copy |
| `/api/generate-email-campaign` | 3-email campaign sequence |
| `/api/generate-brand-guidelines` | Full brand guidelines doc |
| `/api/get-color-palette` | HEX color palette + rationale |
| `/api/generate-logo-prompt` | FLUX-optimised logo prompt |
| `/api/generate-logo` | Logo PNG via FLUX |
| `/api/analyze-sentiment` | Sentiment + brand alignment |
| `/api/analyze-competitors` | Competitive analysis |
| `/api/market-check` (GET) | Comprehensive Market Readiness Report |
| `/api/generate-moodboard` | AI-generated design moodboard |
| `/api/generate-pitch-deck` | Content + PPTX file generation |
| `/api/validate-consistency` | Brand DNA & Text Consistency Validator |
| `/api/validate-consistency-image` | Brand DNA & Image Consistency Validator |
| `/api/chat` | Multi-turn IBM Granite chatbot |
| `/api/transcribe-voice` | Audio → text (Whisper) |

---

## ✅ Feature Checklist

### Text Generation (Groq LLaMA-3.3-70B)
- [x] Brand name generation (10 ideas)
- [x] Tagline generation (10 variations)
- [x] Brand story / About Us
- [x] Marketing copy (ads, press release, manifesto)
- [x] Social media posts (5 platforms)
- [x] Product descriptions
- [x] Email campaign sequences (3-email)
- [x] Brand guidelines document

### Image Generation (FLUX via Pollinations.ai)
- [x] Logo generation via FLUX
- [x] Groq-generated optimised logo prompts
- [x] Logo download as PNG

### Design System
- [x] 5-color brand palette with HEX codes
- [x] Color swatch UI with click-to-copy
- [x] Brand guidelines document
- [x] Brand Moodboard Generation

### Strategy & Validation
- [x] Market Readiness Check
- [x] Pitch Deck Generation (Content + PPTX)
- [x] Brand DNA Consistency Validator (Text & Images)

### Analysis
- [x] Sentiment analysis with score visualization
- [x] Brand alignment scoring
- [x] Competitor analysis & positioning

### AI Interaction
- [x] Multi-turn IBM Granite chatbot
- [x] Voice input (Groq Whisper)
- [x] Session management
- [x] Conversation history

### UI/UX
- [x] Animated gradient background
- [x] Glassmorphism cards
- [x] Floating AI orbs
- [x] Tailwind CSS — zero plain CSS
- [x] 6-tab AI Studio
- [x] Loading animations
- [x] Copy-to-clipboard on all results
- [x] 5-language i18n (EN/ES/FR/DE/HI)
- [x] Theme toggle (dark/light)
- [x] Responsive layout (mobile + desktop)

---

## 🧪 Test Cases

1. **Brand Names** — Enter "HealthTech", "wellness, community", "Professional" → should return 10 names
2. **Logo** — Enter "NovaPulse", "FinTech", "geometric blue" → logo PNG generated
3. **Marketing Content** — Enter brand description, select "Taglines" → 10 taglines
4. **Color Palette** — Enter "SaaS", "Minimalist" → 5 HEX swatches with rationale
5. **Sentiment** — Paste "Empowering every heartbeat" → sentiment score + emotions
6. **AI Chat** — Ask "What makes a strong startup brand name?" → coherent advice
7. **Social Posts** — Brand name + description → 5 Instagram posts with hashtags

---

## 🔒 Security Notes
- Never commit `.env` to Git — add it to `.gitignore`
- All AI calls are server-side; API keys are never exposed to the browser
- CORS is open for local dev — restrict in production
