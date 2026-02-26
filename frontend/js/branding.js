/**
 * branding.js — BizForge / BrandPilot AI
 * All interactive logic for the AI Studio (branding.html).
 * Tab switching, form handlers, voice input, chat, rendering.
 * NOTE: API_BASE is declared in api.js (loaded before this file).
 */

// ─── Session ──────────────────────────────────────────────────────────────────
let chatSessionId = "session_" + Date.now();
document.addEventListener("DOMContentLoaded", () => {
  const el = document.getElementById("session-id-display");
  if (el) el.textContent = chatSessionId;

  // Open tab from URL hash (e.g. branding.html#logo)
  const hash = window.location.hash.replace("#", "");
  const hashMap = {
    "brand-names": "brand-names",
    "logo": "logo",
    "content": "content",
    "design": "design",
    "analysis": "analysis",
    "chat": "chat",
  };
  if (hash && hashMap[hash]) {
    const tabBtn = document.querySelector(`[onclick="switchTab('${hashMap[hash]}', this)"]`);
    if (tabBtn) switchTab(hashMap[hash], tabBtn);
    else {
      // fallback: activate by id directly
      const panel = document.getElementById(`tabpanel-${hashMap[hash]}`);
      if (panel) { panel.classList.add("active"); }
    }
  }
});

// ═══════════════════════════════════════════════════════════════════
// GENERIC HELPERS
// ═══════════════════════════════════════════════════════════════════

/**
 * POST to the backend and return parsed JSON.
 */
async function post(endpoint, body) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

/**
 * Show a loading spinner inside a result container.
 */
function loading(id, msg = "AI is generating your content...") {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = `
    <div class="flex flex-col items-center gap-4 py-8">
      <div class="w-full h-1 rounded-full overflow-hidden bg-white/10">
        <div class="h-full rounded-full"
          style="width:0%;background:linear-gradient(90deg,#7c3aed,#06b6d4,#ec4899);
                 animation:loadingBar 3s ease-in-out forwards;background-size:200%">
        </div>
      </div>
      <p class="text-cyan-300 text-sm font-medium">
        <span style="animation:blink 1s step-end infinite">▌</span> ${msg}
      </p>
    </div>`;
}

/**
 * Show plain text result with a copy button.
 */
function showText(id, text, title = "") {
  const el = document.getElementById(id);
  if (!el) return;
  const escaped = String(text).replace(/</g, "&lt;").replace(/>/g, "&gt;");
  el.innerHTML = `
    <div style="animation:fadeInUp 0.4s ease-out">
      ${title ? `<p class="text-cyan-400 font-semibold text-xs uppercase tracking-wider mb-3">${title}</p>` : ""}
      <pre class="whitespace-pre-wrap text-gray-200 text-sm leading-relaxed font-sans">${escaped}</pre>
      <button onclick='copyText(this, ${JSON.stringify(text)})'
        class="mt-3 px-4 py-1.5 text-xs font-semibold rounded-full border border-violet-500/50
               text-violet-300 hover:bg-violet-500/20 transition-all duration-200">
        📋 Copy
      </button>
    </div>`;
}

/**
 * Copy text to clipboard and give button feedback.
 */
function copyText(btn, text) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.innerHTML;
    btn.innerHTML = "✅ Copied!";
    btn.classList.add("text-emerald-400");
    setTimeout(() => { btn.innerHTML = orig; btn.classList.remove("text-emerald-400"); }, 2000);
  }).catch(() => alert("Copy failed. Please copy manually."));
}

/**
 * Show error inside a result container.
 */
function showErr(id, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = `
    <div class="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/30"
         style="animation:fadeInUp 0.3s ease-out">
      <span class="text-2xl">⚠️</span>
      <div>
        <p class="text-red-400 font-semibold text-sm">Error</p>
        <p class="text-red-300 text-xs mt-1">${msg}</p>
      </div>
    </div>`;
}

/**
 * Get currently selected language (from i18n.js or localStorage).
 */
function getLang() {
  return localStorage.getItem("bizforge_lang") || "en";
}

const LANG_NAMES = { en: "English", es: "Spanish", fr: "French", de: "German", hi: "Hindi" };
function getLanguageName() { return LANG_NAMES[getLang()] || "English"; }


// ═══════════════════════════════════════════════════════════════════
// TAB 1 — BRAND NAMES
// ═══════════════════════════════════════════════════════════════════

async function genBrandNames() {
  const description = document.getElementById("bn-description")?.value?.trim() || "";
  const industry = document.getElementById("bn-industry").value.trim();
  const keywords = document.getElementById("bn-keywords").value.trim();
  const tone     = document.getElementById("bn-tone").value;

  if (!industry || !keywords) {
    showErr("bn-result", "Please fill in Industry and Keywords fields.");
    return;
  }
  loading("bn-result", "Generating brand names with LLaMA-3.3-70B...");
  try {
    const res = await post("/api/generate-brand-names", {
      industry, keywords, tone, description, language: getLanguageName(),
    });
    showText("bn-result", res.data, "Brand Name Suggestions");
  } catch (e) {
    showErr("bn-result", e.message);
  }
}

// ═══════════════════════════════════════════════════════════════════
// TAB 2 — LOGO GENERATOR
// ═══════════════════════════════════════════════════════════════════

async function genLogoPrompt() {
  const brand_name     = document.getElementById("logo-name").value.trim();
  const industry       = document.getElementById("logo-industry").value.trim();
  const style_keywords = document.getElementById("logo-style").value.trim();

  if (!brand_name || !industry) {
    showErr("logo-result", "Please fill in Brand Name and Industry.");
    return;
  }
  loading("logo-prompt-result", "Generating SDXL prompt...");
  document.getElementById("logo-prompt-result").style.display = "block";
  try {
    const res = await post("/api/generate-logo-prompt", { brand_name, industry, style_keywords });
    showText("logo-prompt-result", res.data, "Stable Diffusion XL Prompt");
  } catch (e) {
    showErr("logo-prompt-result", e.message);
  }
}

async function genLogo() {
  const brand_name     = document.getElementById("logo-name").value.trim();
  const industry       = document.getElementById("logo-industry").value.trim();
  const style_keywords = document.getElementById("logo-style").value.trim();

  if (!brand_name || !industry) {
    showErr("logo-result", "Please fill in Brand Name and Industry.");
    return;
  }
  loading("logo-result", "Creating your logo with Stable Diffusion XL — this may take up to 30s...");
  document.getElementById("logo-prompt-result").style.display = "none";
  try {
    const res = await post("/api/generate-logo", { brand_name, industry, style_keywords });
    const imageUrl = `${API_BASE}${res.data.image_url}`;
    document.getElementById("logo-result").innerHTML = `
      <div style="animation:scaleIn 0.5s ease-out">
        <p class="text-cyan-400 font-semibold text-xs uppercase tracking-wider mb-3">Generated Logo</p>
        <img src="${imageUrl}" alt="Logo for ${brand_name}" class="max-w-full max-h-72 rounded-xl border border-white/10 mx-auto block" />
        <div class="flex gap-3 mt-4 justify-center">
          <a href="${imageUrl}" download="${brand_name}_logo.png"
            class="px-4 py-2 text-xs font-semibold rounded-full bg-violet-500/20 border border-violet-500/50
                   text-violet-300 hover:bg-violet-500/30 transition-all">
            ⬇️ Download PNG
          </a>
        </div>
      </div>`;
  } catch (e) {
    showErr("logo-result", e.message);
  }
}


// ═══════════════════════════════════════════════════════════════════
// TAB 3 — MARKETING CONTENT
// ═══════════════════════════════════════════════════════════════════

async function genMarketingContent() {
  const brand_description = document.getElementById("mc-desc").value.trim();
  const content_type      = document.getElementById("mc-type").value;
  const tone              = document.getElementById("mc-tone").value;

  if (!brand_description) {
    showErr("mc-result", "Please provide a brand description.");
    return;
  }
  loading("mc-result", "Crafting marketing content...");
  try {
    const res = await post("/api/generate-marketing-content", {
      brand_description, tone, content_type, language: getLanguageName(),
    });
    showText("mc-result", res.data, content_type);
  } catch (e) {
    showErr("mc-result", e.message);
  }
}

async function genSocialPosts() {
  const brand_name          = document.getElementById("sp-brand").value.trim();
  const product_description = document.getElementById("sp-desc").value.trim();
  const platform            = document.getElementById("sp-platform").value;
  const tone                = document.getElementById("sp-tone").value;

  if (!brand_name || !product_description) {
    showErr("sp-result", "Please fill in Brand Name and Product Description.");
    return;
  }
  loading("sp-result", `Generating ${platform} posts...`);
  try {
    const res = await post("/api/generate-social-posts", {
      brand_name, product_description, platform, tone, language: getLanguageName(),
    });
    showText("sp-result", res.data, `${platform} Social Posts`);
  } catch (e) {
    showErr("sp-result", e.message);
  }
}

async function genProductDesc() {
  const product_name    = document.getElementById("pd-name").value.trim();
  const features        = document.getElementById("pd-features").value.trim();
  const target_audience = document.getElementById("pd-audience").value.trim();
  const tone            = document.getElementById("pd-tone").value;

  if (!product_name || !features) {
    showErr("pd-result", "Please fill in Product Name and Features.");
    return;
  }
  loading("pd-result", "Writing product description...");
  try {
    const res = await post("/api/generate-product-description", {
      product_name, features, target_audience, tone, language: getLanguageName(),
    });
    showText("pd-result", res.data, "Product Description");
  } catch (e) {
    showErr("pd-result", e.message);
  }
}

async function genEmailCampaign() {
  const brand_name     = document.getElementById("ec-brand").value.trim();
  const campaign_goal  = document.getElementById("ec-goal").value.trim();
  const product_service = document.getElementById("ec-product").value.trim();
  const tone           = document.getElementById("ec-tone").value;

  if (!brand_name || !campaign_goal) {
    showErr("ec-result", "Please fill in Brand Name and Campaign Goal.");
    return;
  }
  loading("ec-result", "Writing your 3-email campaign sequence...");
  try {
    const res = await post("/api/generate-email-campaign", {
      brand_name, campaign_goal, product_service, tone, language: getLanguageName(),
    });
    showText("ec-result", res.data, "Email Campaign Sequence");
  } catch (e) {
    showErr("ec-result", e.message);
  }
}

async function genBrandStory() {
  const brand_name = document.getElementById("bs-name").value.trim();
  const industry   = document.getElementById("bs-industry").value.trim();
  const mission    = document.getElementById("bs-mission").value.trim();
  const tone       = document.getElementById("bs-tone").value;

  if (!brand_name || !industry) {
    showErr("bs-result", "Please fill in Brand Name and Industry.");
    return;
  }
  loading("bs-result", "Crafting your brand story...");
  try {
    const res = await post("/api/generate-brand-story", {
      brand_name, industry, mission, tone, language: getLanguageName(),
    });
    showText("bs-result", res.data, "Brand Story");
  } catch (e) {
    showErr("bs-result", e.message);
  }
}


// ═══════════════════════════════════════════════════════════════════
// TAB 4 — DESIGN SYSTEM
// ═══════════════════════════════════════════════════════════════════

async function genColorPalette() {
  const industry = document.getElementById("ds-industry").value.trim();
  const tone     = document.getElementById("ds-tone").value;

  if (!industry) {
    showErr("ds-palette", "Please enter an industry.");
    return;
  }
  loading("ds-palette", "Generating brand color palette...");
  try {
    const res = await post("/api/get-color-palette", { tone, industry });
    renderColorPalette("ds-palette", res.data);
  } catch (e) {
    showErr("ds-palette", e.message);
  }
}

/**
 * Render color swatches from palette data.
 */
function renderColorPalette(containerId, data) {
  const el = document.getElementById(containerId);
  if (!el) return;

  if (data.raw) {
    // Fallback: show raw text
    showText(containerId, data.raw, "Color Palette");
    return;
  }

  const colors = ["primary", "secondary", "accent", "background", "text"];
  const swatches = colors.map((key) => {
    const c = data[key];
    if (!c) return "";
    return `
      <div class="flex flex-col items-center gap-2">
        <div class="color-swatch" style="background:${c.hex}" title="Click to copy ${c.hex}"
             onclick="copyText(this, '${c.hex}'); this.style.transform='scale(0.9)'; setTimeout(()=>this.style.transform='',200)">
        </div>
        <div class="text-center">
          <p class="text-xs font-bold text-gray-200">${c.hex}</p>
          <p class="text-xs text-gray-500">${c.name}</p>
          <p class="text-xs text-gray-600 leading-tight mt-0.5">${c.usage}</p>
        </div>
      </div>`;
  }).join("");

  el.innerHTML = `
    <div style="animation:fadeInUp 0.4s ease-out">
      <p class="text-cyan-400 font-semibold text-xs uppercase tracking-wider mb-4">Brand Color Palette</p>
      <div class="grid grid-cols-5 gap-3">${swatches}</div>
      ${data.rationale ? `
        <div class="mt-5 p-3 rounded-xl bg-white/5 border border-white/10">
          <p class="text-xs text-gray-400 leading-relaxed">💡 ${data.rationale}</p>
        </div>` : ""}
      <button onclick='copyText(this, ${JSON.stringify(JSON.stringify(data))})'
        class="mt-3 px-4 py-1.5 text-xs font-semibold rounded-full border border-violet-500/50
               text-violet-300 hover:bg-violet-500/20 transition-all">
        📋 Copy JSON
      </button>
    </div>`;
}

async function genBrandGuidelines() {
  const brand_name   = document.getElementById("dg-brand").value.trim();
  const industry     = document.getElementById("ds-industry").value.trim();
  const mission      = document.getElementById("dg-mission").value.trim();
  const tone         = document.getElementById("ds-tone").value;
  const color_palette = "See color palette above";

  if (!brand_name || !industry) {
    showErr("dg-result", "Please fill in Brand Name and Industry (in the form above).");
    return;
  }
  loading("dg-result", "Writing brand guidelines document...");
  try {
    const res = await post("/api/generate-brand-guidelines", {
      brand_name, industry, mission, tone, color_palette, language: getLanguageName(),
    });
    showText("dg-result", res.data, "Brand Guidelines");
  } catch (e) {
    showErr("dg-result", e.message);
  }
}


// ═══════════════════════════════════════════════════════════════════
// TAB 5 — ANALYSIS
// ═══════════════════════════════════════════════════════════════════

async function genSentiment() {
  const text       = document.getElementById("sa-text").value.trim();
  const brand_tone = document.getElementById("sa-tone").value;

  if (!text) {
    showErr("sa-result", "Please enter text to analyse.");
    return;
  }
  loading("sa-result", "Analysing sentiment and brand alignment...");
  try {
    const res = await post("/api/analyze-sentiment", { text, brand_tone });
    renderSentiment("sa-result", res.data);
  } catch (e) {
    showErr("sa-result", e.message);
  }
}

/**
 * Render structured sentiment analysis result.
 */
function renderSentiment(containerId, data) {
  const el = document.getElementById(containerId);
  if (!el) return;

  if (data.raw) {
    showText(containerId, data.raw, "Sentiment Analysis");
    return;
  }

  const sentimentColor = {
    Positive: "text-emerald-400",
    Negative: "text-red-400",
    Neutral:  "text-yellow-400",
  }[data.overall_sentiment] || "text-gray-400";

  const scoreBar = (score) => {
    const pct = Math.round((score || 0) * 100);
    return `
      <div class="flex items-center gap-3">
        <div class="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all duration-700"
               style="width:${pct}%;background:linear-gradient(90deg,#7c3aed,#06b6d4)"></div>
        </div>
        <span class="text-xs font-bold text-cyan-300 w-8 text-right">${pct}%</span>
      </div>`;
  };

  el.innerHTML = `
    <div style="animation:fadeInUp 0.4s ease-out" class="space-y-4">
      <div class="flex items-center gap-4">
        <span class="text-3xl">${data.overall_sentiment === "Positive" ? "😊" : data.overall_sentiment === "Negative" ? "😟" : "😐"}</span>
        <div>
          <p class="text-xs text-gray-500 uppercase tracking-wider">Overall Sentiment</p>
          <p class="text-lg font-bold ${sentimentColor}">${data.overall_sentiment}</p>
        </div>
      </div>

      <div>
        <p class="text-xs text-gray-500 mb-1">Sentiment Score</p>
        ${scoreBar(data.sentiment_score)}
      </div>
      <div>
        <p class="text-xs text-gray-500 mb-1">Brand Alignment</p>
        ${scoreBar(data.brand_alignment_score)}
      </div>

      ${data.emotions ? `
        <div>
          <p class="text-xs text-gray-500 mb-2">Detected Emotions</p>
          <div class="flex flex-wrap gap-2">
            ${data.emotions.map(e => `<span class="px-3 py-1 text-xs rounded-full bg-violet-500/20 border border-violet-500/30 text-violet-300">${e}</span>`).join("")}
          </div>
        </div>` : ""}

      ${data.strengths ? `
        <div>
          <p class="text-xs text-gray-500 mb-2">✅ Strengths</p>
          <ul class="space-y-1">${data.strengths.map(s => `<li class="text-xs text-emerald-300">• ${s}</li>`).join("")}</ul>
        </div>` : ""}

      ${data.improvements ? `
        <div>
          <p class="text-xs text-gray-500 mb-2">💡 Improvements</p>
          <ul class="space-y-1">${data.improvements.map(i => `<li class="text-xs text-amber-300">• ${i}</li>`).join("")}</ul>
        </div>` : ""}

      ${data.recommendation ? `
        <div class="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
          <p class="text-xs text-cyan-300 leading-relaxed">💬 ${data.recommendation}</p>
        </div>` : ""}
    </div>`;
}

async function genCompetitor() {
  const brand_name  = document.getElementById("ca-brand").value.trim();
  const industry    = document.getElementById("ca-industry").value.trim();
  const target_market = document.getElementById("ca-market").value.trim();

  if (!brand_name || !industry) {
    showErr("ca-result", "Please fill in Brand Name and Industry.");
    return;
  }
  loading("ca-result", "Analysing competitive landscape...");
  try {
    const res = await post("/api/analyze-competitors", {
      brand_name, industry, target_market, language: getLanguageName(),
    });
    showText("ca-result", res.data, "Competitive Analysis");
  } catch (e) {
    showErr("ca-result", e.message);
  }
}


// ═══════════════════════════════════════════════════════════════════
// TAB 6 — AI CHAT (IBM Granite)
// ═══════════════════════════════════════════════════════════════════

function handleChatKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendChatMessage();
  }
}

async function sendChatMessage() {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (!message) return;

  input.value = "";
  appendChatBubble("user", message);

  // Typing indicator
  const typingId = appendTypingIndicator();

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: chatSessionId }),
    });
    const data = await res.json();
    removeTypingIndicator(typingId);

    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    appendChatBubble("ai", data.data.reply);
  } catch (e) {
    removeTypingIndicator(typingId);
    appendChatBubble("error", `❌ ${e.message}`);
  }
}

function appendChatBubble(role, text) {
  const container = document.getElementById("chat-messages");
  if (!container) return;

  const escaped = String(text).replace(/</g, "&lt;").replace(/>/g, "&gt;");
  let html = "";

  if (role === "user") {
    html = `
      <div class="flex justify-end gap-3" style="animation:fadeInUp 0.3s ease-out">
        <div class="chat-bubble-user">
          <p>${escaped}</p>
        </div>
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-violet-500
                    flex items-center justify-center text-sm flex-shrink-0">You</div>
      </div>`;
  } else if (role === "ai") {
    html = `
      <div class="flex gap-3" style="animation:fadeInUp 0.3s ease-out">
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500
                    flex items-center justify-center text-sm flex-shrink-0">🤖</div>
        <div class="chat-bubble-ai">
          <p class="whitespace-pre-wrap leading-relaxed">${escaped}</p>
        </div>
      </div>`;
  } else {
    html = `
      <div class="flex gap-3" style="animation:fadeInUp 0.3s ease-out">
        <div class="w-8 h-8 rounded-full bg-red-500/30 flex items-center justify-center text-sm flex-shrink-0">⚠️</div>
        <div class="chat-bubble-ai border-red-500/30">
          <p class="text-red-400 text-sm">${escaped}</p>
        </div>
      </div>`;
  }

  const div = document.createElement("div");
  div.innerHTML = html;
  container.appendChild(div.firstElementChild);
  container.scrollTop = container.scrollHeight;
}

function appendTypingIndicator() {
  const id = "typing-" + Date.now();
  const container = document.getElementById("chat-messages");
  if (!container) return id;

  const html = `
    <div id="${id}" class="flex gap-3">
      <div class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500
                  flex items-center justify-center text-sm flex-shrink-0">🤖</div>
      <div class="chat-bubble-ai">
        <div class="flex gap-1 items-center py-1">
          <div class="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" style="animation-delay:0ms"></div>
          <div class="w-2 h-2 rounded-full bg-violet-400 animate-bounce" style="animation-delay:150ms"></div>
          <div class="w-2 h-2 rounded-full bg-pink-400 animate-bounce" style="animation-delay:300ms"></div>
        </div>
      </div>
    </div>`;
  const div = document.createElement("div");
  div.innerHTML = html;
  container.appendChild(div.firstElementChild);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

async function clearChat() {
  try {
    await fetch(`${API_BASE}/api/chat/${chatSessionId}`, { method: "DELETE" });
  } catch (_) {}
  chatSessionId = "session_" + Date.now();
  const idDisplay = document.getElementById("session-id-display");
  if (idDisplay) idDisplay.textContent = chatSessionId;

  const container = document.getElementById("chat-messages");
  if (container) {
    container.innerHTML = `
      <div class="flex gap-3">
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500
                    flex items-center justify-center text-sm flex-shrink-0">🤖</div>
        <div class="chat-bubble-ai">
          <p>Conversation cleared! How can I help with your branding today? 🚀</p>
        </div>
      </div>`;
  }
}


// ═══════════════════════════════════════════════════════════════════
// VOICE INPUT (Groq Whisper)
// ═══════════════════════════════════════════════════════════════════

let mediaRecorder = null;
let audioChunks   = [];
let voiceTargetId = null;

/**
 * Start voice recording. Fills the target input when done.
 * @param {string} targetInputId - id of input/textarea to fill
 */
async function startVoice(targetInputId) {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    // Stop ongoing recording
    mediaRecorder.stop();
    return;
  }

  if (!navigator.mediaDevices) {
    alert("Voice input is not supported in this browser.");
    return;
  }

  voiceTargetId = targetInputId;
  const btn = document.activeElement;

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);

    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      const blob = new Blob(audioChunks, { type: "audio/webm" });

      // Send to backend
      const form = new FormData();
      form.append("audio", blob, "voice.webm");

      try {
        const res = await fetch(`${API_BASE}/api/transcribe-voice`, {
          method: "POST",
          body: form,
        });
        const data = await res.json();
        if (data.success && data.data.transcription) {
          const target = document.getElementById(voiceTargetId);
          if (target) {
            target.value = data.data.transcription;
            target.focus();
          }
        }
      } catch (err) {
        console.error("Transcription error:", err);
      }
    };

    // Record for max 8 seconds
    mediaRecorder.start();
    setTimeout(() => {
      if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
      }
    }, 8000);

    // Visual feedback on button
    if (btn) {
      btn.style.background = "rgba(239,68,68,0.4)";
      btn.title = "Recording... click to stop";
    }

  } catch (err) {
    alert("Microphone access denied: " + err.message);
  }
}
