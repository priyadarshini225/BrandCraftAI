/**
 * branding.js — BizForge / BrandPilot AI
 * All interactive logic for the AI Studio (branding.html).
 * Tab switching, form handlers, voice input, chat, rendering.
 * NOTE: API_BASE is declared in api.js (loaded before this file).
 */

// ─── Session ──────────────────────────────────────────────────────────────────
let chatSessionId = "session_" + Date.now();
function applyHashNavigation() {
  const el = document.getElementById("session-id-display");
  if (el) el.textContent = chatSessionId;
  const hash = window.location.hash.replace("#", "");
  const hashMap = { "brand-names": "brand-names", "logo": "logo", "content": "content", "design": "design", "analysis": "analysis", "chat": "chat" };
  if (!hash) return;
  const [top, sub] = hash.split(":");
  // Gracefully redirect old deck link to marketing content
  const normalizedSub = (sub === "deck") ? "marketing" : sub;
  const topKey = hashMap[top] ? top : (hashMap[hash] ? hash : null);
  if (!topKey) return;
  const tabBtn = document.querySelector(`[onclick="switchTab('${hashMap[topKey] || topKey}', this)"]`);
  if (tabBtn) switchTab(hashMap[topKey] || topKey, tabBtn);
  else {
    const panel = document.getElementById(`tabpanel-${hashMap[topKey] || topKey}`);
    if (panel) { panel.classList.add("active"); }
  }
  if (normalizedSub) {
    setTimeout(() => {
      const btn = document.querySelector(`#tabpanel-${hashMap[topKey] || topKey} .sub-tab-btn[onclick="switchSubTab('${hashMap[topKey] || topKey}','${normalizedSub}',this)"]`);
      if (btn && typeof window.switchSubTab === "function") {
        window.switchSubTab(hashMap[topKey] || topKey, normalizedSub, btn);
      }
    }, 50);
  }
}

document.addEventListener("DOMContentLoaded", applyHashNavigation);
window.addEventListener("hashchange", applyHashNavigation);

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
      <div class="w-full h-1 rounded-full overflow-hidden bg-white/60 dark:bg-white/10">
        <div class="h-full rounded-full"
          style="width:0%;background:linear-gradient(90deg,#7c3aed,#06b6d4,#ec4899);
                 animation:loadingBar 3s ease-in-out forwards;background-size:200%">
        </div>
      </div>
      <p class="text-[#7DB5A0] dark:text-cyan-300 text-sm font-medium">
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

  // Detect if text contains markdown headers, bold, or lists
  const isMarkdown = typeof text === 'string' && (text.includes('**') || text.includes('#') || text.includes('- '));

  // Parse with marked if available, otherwise just escape
  let contentHtml = "";
  if (isMarkdown && typeof marked !== 'undefined') {
    contentHtml = `<div class="markdown-prose text-[#1A1A1A] dark:text-gray-200 text-sm leading-relaxed font-sans">${marked.parse(text)}</div>`;
  } else {
    const escaped = String(text).replace(/</g, "&lt;").replace(/>/g, "&gt;");
    contentHtml = `<pre class="whitespace-pre-wrap text-[#1A1A1A] dark:text-gray-200 text-sm leading-relaxed font-sans">${escaped}</pre>`;
  }

  el.innerHTML = `
    <div style="animation:fadeInUp 0.4s ease-out">
      ${title ? `<p class="text-[#7DB5A0] dark:text-cyan-400 font-semibold text-xs uppercase tracking-wider mb-3">${title}</p>` : ""}
      ${contentHtml}
      <button onclick='copyText(this, ${JSON.stringify(text)})'
        class="mt-3 px-4 py-1.5 text-xs font-semibold rounded-full border border-[#FF5F6D]/50 dark:border-violet-500/50
               text-[#FF5F6D] dark:text-violet-300 hover:bg-[#FF5F6D]/20 dark:bg-violet-500/20 transition-all duration-200">
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
    btn.classList.add("text-[#7DB5A0] dark:text-emerald-400");
    setTimeout(() => { btn.innerHTML = orig; btn.classList.remove("text-[#7DB5A0] dark:text-emerald-400"); }, 2000);
  }).catch(() => alert("Copy failed. Please copy manually."));
}

/**
 * Show error inside a result container.
 */
function showErr(id, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = `
    <div class="flex items-center gap-3 p-4 rounded-xl bg-[#FF5F6D]/10 dark:bg-red-500/10 border border-red-500/30"
         style="animation:fadeInUp 0.3s ease-out">
      <span class="text-2xl">⚠️</span>
      <div>
        <p class="text-red-400 font-semibold text-sm">Error</p>
        <p class="text-red-300 text-xs mt-1">${msg}</p>
      </div>
    </div>`;
}

/**
 * Display text content as animated cards if it looks like a list,
 * otherwise fall back to a single card display.
 */
function displayContentCards(id, text, title = "") {
  const el = document.getElementById(id);
  if (!el) return;

  // Split text into lines to detect lists or paragraphs
  const lines = text.split('\n').filter(l => l.trim().length > 0);
  let cardsData = [];

  // Very basic markdown list parsing
  // Matches "1. Text", "- Text", "* Text", "• Text", "Title: Text"
  const listRegex = /^((?:\d+\.|\-|\*|•)\s+|\*\*?([^:]+):\*\*?\s+)(.*)$/;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    // Skip introductory text (like "Here are some slogans:")
    if (i === 0 && (line.toLowerCase().includes("here are") || line.toLowerCase().includes("certainly") || !line.match(listRegex)) && lines.length > 2) {
      if (line.length < 150) continue; // Skip short intros
    }

    const match = line.match(listRegex);
    if (match && match[3]) {
      // It's a list item
      const titleText = match[2] ? match[2].trim() : `Option ${cardsData.length + 1}`;
      cardsData.push({ title: titleText, fullLine: line });
    } else if (line.length > 20) {
      // Just a raw paragraph, treat as a card if it's substantial
      cardsData.push({ title: `Option ${cardsData.length + 1}`, fullLine: line });
    }
  }

  // If we couldn't parse it well, just show it as a single card
  if (cardsData.length === 0 || cardsData.length === 1) {
    cardsData = [{ title: "Generated Content", fullLine: text }];
  }

  // Ensure title displays at the top
  const titleHtml = title ? `<p class="text-[#7DB5A0] dark:text-cyan-400 font-semibold text-xs uppercase tracking-wider mb-4 animate-[fadeInUp_0.4s_ease-out]">${title}</p>` : "";

  const cardsHtml = cardsData.map((item, index) => {
    // Parse markdown bold **text** -> span
    let displayHtml = item.fullLine.replace(/\*\*(.*?)\*\*/g, '<span class="font-bold text-[#1A1A1A] dark:text-white">$1</span>');

    // Clean up purely markdown list prefixes if we pulled a title out
    displayHtml = displayHtml.replace(/^(\d+\.|\-|\*|•)\s+/, '');

    // Escape for inline copy
    const safeText = item.fullLine.replace(/'/g, "\\'").replace(/"/g, "&quot;").replace(/\n/g, '\\n');

    return `
    <div class="brand-result-card relative group p-5 flex flex-col justify-between overflow-hidden mb-4" 
         style="animation: fadeInUp 0.5s ease-out forwards; animation-delay: ${index * 0.1}s; opacity: 0;"
         onclick="copyText(this, '${safeText}')">
      
      <!-- Subtle top gradient glow on hover -->
      <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#FF5F6D] to-[#F4A0A0] dark:from-violet-500 dark:to-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

      <div>
        <div class="flex items-center gap-2 mb-3">
          <div class="w-2 h-2 rounded-full bg-[#FF5F6D] dark:bg-violet-400 opacity-50 shadow-[0_0_8px_rgba(255,95,109,0.5)] dark:shadow-[0_0_8px_rgba(139,92,246,0.5)]"></div>
          <h4 class="text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-slate-500 relative inline-block group-hover:text-[#FF5F6D] dark:group-hover:text-violet-300 transition-colors duration-300">
            ${item.title}
          </h4>
        </div>
        
        <p class="text-sm text-gray-700 dark:text-slate-300 leading-relaxed font-sans">
           ${displayHtml}
        </p>
      </div>
      
      <div class="mt-4 flex justify-end items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style="transition-delay: 50ms;">
        <span class="text-[10px] font-bold uppercase tracking-wider text-[#FF5F6D] dark:text-violet-400">📋 Copy</span>
      </div>
    </div>
  `;
  }).join('');

  el.innerHTML = `<div>${titleHtml}${cardsHtml}</div>`;
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
  const tone = document.getElementById("bn-tone").value;

  if (!industry || !keywords) {
    showErr("bn-result", "Please fill in Industry and Keywords fields.");
    return;
  }
  loading("bn-result", "Generating brand names...");
  try {
    const res = await post("/api/generate-brand-names", {
      industry, keywords, tone, description, language: getLanguageName(),
    });

    // Parse JSON response for cards
    let namesData = [];
    try {
      namesData = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
    } catch (e) {
      console.warn("Could not parse JSON, falling back", e);
      // Fallback: if it's not JSON, maybe it's the old format? 
      // But we changed backend to return JSON.
      showText("bn-result", res.data, "Brand Suggestions");
      return;
    }

    if (Array.isArray(namesData)) {
      displayBrandCards(namesData);
    } else {
      showText("bn-result", res.data, "Brand Suggestions");
    }
  } catch (e) {
    showErr("bn-result", e.message);
  }
}

/**
 * Display JSON brand names as interactive UI cards.
 */
function displayBrandCards(namesData) {
  const el = document.getElementById("bn-result");
  if (!el) return;

  const cardsHtml = namesData.map((item, index) => {
    // Escape single quotes for inline JS
    const safeName = item.name.replace(/'/g, "\\'");
    // Empty p tag that we will fill with JS
    return `
    <div class="brand-result-card relative group p-5 flex flex-col justify-between overflow-hidden" 
         style="animation: fadeInUp 0.5s ease-out forwards; animation-delay: ${index * 0.15}s; opacity: 0;"
         onclick="copyText(this, '${safeName}')">
      
      <!-- Subtle top gradient glow on hover to feel 'active' -->
      <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#FF5F6D] to-[#F4A0A0] dark:from-violet-500 dark:to-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

      <div>
        <div class="flex items-center gap-2 mb-2">
          <div class="w-8 h-8 rounded-full bg-[#FF5F6D]/10 dark:bg-violet-500/10 text-[#FF5F6D] dark:text-violet-400 flex items-center justify-center font-bold text-xs"
               style="animation: scaleIn 0.4s ease-out forwards; animation-delay: ${(index * 0.15) + 0.2}s; opacity: 0;">
            ${item.name.charAt(0)}
          </div>
          <h4 class="text-xl font-bold font-display text-[#1A1A1A] dark:text-white relative inline-block group-hover:text-[#FF5F6D] dark:group-hover:text-violet-300 transition-colors duration-300"
              style="animation: fadeIn 0.4s ease-out forwards; animation-delay: ${(index * 0.15) + 0.3}s; opacity: 0;">
            ${item.name}
          </h4>
        </div>
        
        <p id="desc-${index}" class="text-xs text-gray-600 dark:text-slate-400 leading-relaxed mt-3 min-h-[40px]"
           style="opacity: 0; transition: opacity 0.3s ease;">
           <!-- Text will be typed here -->
        </p>
      </div>
      
      <div class="mt-4 flex justify-end items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style="transition-delay: 50ms;">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span class="text-[10px] font-bold uppercase tracking-wider text-[#FF5F6D] dark:text-violet-400">Copy Name</span>
      </div>
    </div>
  `;
  }).join('');

  el.innerHTML = cardsHtml;

  // Typewriter effect function
  const typeWriter = (elementId, text, speed, delay) => {
    setTimeout(() => {
      const el = document.getElementById(elementId);
      if (!el) return;
      el.style.opacity = '1'; // Fade in the container first
      el.innerHTML = '<span class="typing-cursor">|</span>'; // Add a cursor
      let i = 0;
      const type = () => {
        if (i < text.length) {
          // Replace cursor, add char, append cursor
          el.innerHTML = text.substring(0, i + 1) + '<span class="typing-cursor font-normal opacity-50">|</span>';
          i++;
          setTimeout(type, speed + (Math.random() * 10 - 5)); // Add slight randomness to typing speed
        } else {
          // Remove cursor when done
          el.innerHTML = text;
        }
      };
      type();
    }, delay);
  };

  // Trigger typewriter for each card's description after they fade in
  namesData.forEach((item, index) => {
    // Start typing shortly after the card itself finishes animating in.
    // Base delay for whole block + stagger delay + animation time
    const startDelay = (index * 150) + 600;
    typeWriter(`desc-${index}`, item.rationale, 15, startDelay);
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// MARKET READINESS REPORT
// ─────────────────────────────────────────────────────────────────────────────
async function genMarketCheck() {
  const brand_name = document.getElementById("mk-brand").value.trim();
  const urlsText = document.getElementById("mk-urls").value.trim();
  const tldsText = document.getElementById("mk-tlds").value.trim();
  if (!brand_name || !urlsText) {
    showErr("mk-result", "Please fill in Brand Name and Competitor URLs.");
    return;
  }
  loading("mk-result", "Running market readiness report...");
  try {
    const qs = new URLSearchParams({
      brand_name,
      competitor_urls: urlsText,
    });
    if (tldsText) qs.set("tlds", tldsText);
    const res = await fetch(`${API_BASE}/api/market-check?${qs.toString()}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    renderMarketCheck("mk-result", data.data);
  } catch (e) {
    showErr("mk-result", e.message);
  }
}

function renderMarketCheck(containerId, data) {
  const el = document.getElementById(containerId);
  if (!el) return;
  const comp = (data.competitors || []).map(c => `
    <div class="p-3 rounded-xl bg-white/60 dark:bg-white/5 border border-[#C8D5C0] dark:border-white/10">
      <p class="text-[#1A1A1A] dark:text-white text-sm font-semibold">${c.title || c.url || "Unknown"}</p>
      ${c.meta_description ? `<p class="text-xs text-gray-600 dark:text-slate-400 mt-1">${c.meta_description}</p>` : ""}
      ${c.hex_codes && c.hex_codes.length ? `
        <div class="flex gap-1 mt-2">${c.hex_codes.slice(0, 8).map(h => `
          <span title="${h}" class="w-4 h-4 rounded border border-[#C8D5C0] dark:border-white/20" style="background:${h}"></span>
        `).join("")}</div>` : ""}
    </div>
  `).join("");

  const domains = data.domains ? Object.entries(data.domains).map(([dom, info]) => `
    <div class="flex items-center justify-between p-2 rounded-lg bg-white/60 dark:bg-white/5 border border-[#C8D5C0] dark:border-white/10">
      <span class="text-xs text-[#1A1A1A] dark:text-white">${dom}</span>
      <span class="text-xs ${info.available ? "text-[#7DB5A0] dark:text-emerald-400" : "text-[#FF5F6D] dark:text-rose-400"}">
        ${info.available === true ? "Available" : info.available === false ? "Taken" : "Unknown"}
      </span>
    </div>`).join("") : "";

  const risk = data.name_risk;
  const risks = risk && risk.languages ? risk.languages.map(r => `
    <li class="text-xs ${r.severity === "high" ? "text-[#FF5F6D] dark:text-rose-400" : r.severity === "med" ? "text-[#F7C5A0] dark:text-amber-300" : "text-gray-600 dark:text-slate-300"}">• ${r.lang}: ${r.issue} (${r.severity})</li>
  `).join("") : "";

  el.innerHTML = `
    <div style="animation:fadeInUp 0.4s ease-out" class="space-y-4">
      <div>
        <p class="text-xs text-gray-500 uppercase tracking-wider mb-2">Positioning</p>
        <div class="p-3 rounded-xl bg-white/60 dark:bg-white/5 border border-[#C8D5C0] dark:border-white/10 whitespace-pre-wrap text-sm text-gray-200">${(data.positioning || "").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</div>
      </div>
      <div>
        <p class="text-xs text-gray-500 uppercase tracking-wider mb-2">Competitors</p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          ${comp || '<p class="text-xs text-gray-500 dark:text-slate-500">No competitors parsed.</p>'}
        </div>
      </div>
      <div>
        <p class="text-xs text-gray-500 uppercase tracking-wider mb-2">Domains</p>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-2">${domains || '<p class="text-xs text-gray-500 dark:text-slate-500">No domain data.</p>'}</div>
      </div>
      <div>
        <p class="text-xs text-gray-500 uppercase tracking-wider mb-2">Name Risk</p>
        ${risks ? `<ul class="space-y-1">${risks}</ul>` : '<p class="text-xs text-gray-500 dark:text-slate-500">No risks flagged.</p>'}
      </div>
    </div>`;
}

// ─────────────────────────────────────────────────────────────────────────────
// CONSISTENCY VALIDATOR
// ─────────────────────────────────────────────────────────────────────────────
async function genConsistencyText() {
  const brand_dna = document.getElementById("cv-dna").value.trim();
  const about_text = document.getElementById("cv-text").value.trim();
  if (!brand_dna || !about_text) {
    showErr("cv-result", "Please provide Brand DNA and Text.");
    return;
  }
  loading("cv-result", "Checking text consistency...");
  try {
    const res = await post("/api/validate-consistency", { brand_dna, about_text });
    renderConsistency("cv-result", res.data);
  } catch (e) {
    showErr("cv-result", e.message);
  }
}

async function genConsistencyImage() {
  const brand_dna = document.getElementById("cv-dna").value.trim();
  const f = document.getElementById("cv-image").files[0];
  if (!brand_dna || !f) {
    showErr("cv-result", "Please provide Brand DNA and choose an image.");
    return;
  }
  loading("cv-result", "Checking image consistency...");
  try {
    const form = new FormData();
    form.append("brand_dna", brand_dna);
    form.append("image", f, f.name);
    const resp = await fetch(`${API_BASE}/api/validate-consistency-image`, { method: "POST", body: form });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new Error(data.detail || `HTTP ${resp.status}`);
    if (data && data.success && data.data) {
      renderConsistency("cv-result", data.data);
    } else {
      throw new Error(typeof data === 'object' ? JSON.stringify(data) : 'Unexpected response');
    }
  } catch (e) {
    const msg = (e && e.message) ? e.message : String(e);
    showErr("cv-result", msg);
  }
}

function renderConsistency(containerId, data) {
  const el = document.getElementById(containerId);
  if (!el) return;
  if (data.raw) { showText(containerId, data.raw, "Consistency"); return; }
  const score = data.score ?? Math.round((data.brand_alignment_score || 0) * 100);
  const verdict = data.verdict || "Result";
  const reasons = (data.reasons || []).map(r => `<li class="text-xs text-[#F7C5A0] dark:text-amber-300">• ${r}</li>`).join("");
  const fixes = (data.fixes || []).map(r => `<li class="text-xs text-[#7DB5A0] dark:text-emerald-300">• ${r}</li>`).join("");
  el.innerHTML = `
    <div style="animation:fadeInUp 0.4s ease-out" class="space-y-4">
      <div class="flex items-center justify-between">
        <p class="text-xs text-gray-500 uppercase tracking-wider">Consistency Score</p>
        <p class="text-lg font-bold text-[#7DB5A0] dark:text-cyan-300">${score}%</p>
      </div>
      <div>
        <p class="text-xs text-gray-500 uppercase tracking-wider mb-1">Verdict</p>
        <p class="text-sm text-[#1A1A1A] dark:text-white font-semibold">${verdict}</p>
      </div>
      ${reasons ? `<div><p class="text-xs text-gray-500 mb-1">What feels off</p><ul class="space-y-1">${reasons}</ul></div>` : ""}
      ${fixes ? `<div><p class="text-xs text-gray-500 mb-1">Suggestions</p><ul class="space-y-1">${fixes}</ul></div>` : ""}
    </div>`;
}

// Deck feature removed from UI per request
// ═══════════════════════════════════════════════════════════════════
// TAB 2 — LOGO GENERATOR
// ═══════════════════════════════════════════════════════════════════

async function genLogoPrompt() {
  const brand_name = document.getElementById("logo-name").value.trim();
  const industry = document.getElementById("logo-industry").value.trim();
  const style_keywords = document.getElementById("logo-style")?.value?.trim() || "";
  const typography = document.getElementById("logo-typography")?.value || "";
  const icon_style = document.getElementById("logo-icon-style")?.value || "";
  const mood = document.getElementById("logo-mood")?.value?.trim() || "";
  const description = document.getElementById("logo-icon-concept")?.value?.trim() || "";

  if (!brand_name || !industry) {
    showErr("logo-result", "Please fill in Brand Name and Industry.");
    return;
  }
  loading("logo-prompt-result", "Building logo prompt...");
  document.getElementById("logo-prompt-result").style.display = "block";
  try {
    const res = await post("/api/generate-logo-prompt", {
      brand_name, industry, style_keywords, typography, icon_style, mood, description
    });
    showText("logo-prompt-result", res.data || "", "Logo Prompt");
  } catch (e) {
    showErr("logo-prompt-result", e.message);
  }
}

async function genLogo() {
  const brand_name = document.getElementById("logo-name").value.trim();
  const industry = document.getElementById("logo-industry").value.trim();
  const style_keywords = document.getElementById("logo-style")?.value?.trim() || "";
  const typography = document.getElementById("logo-typography")?.value || "";
  const icon_style = document.getElementById("logo-icon-style")?.value || "";
  const mood = document.getElementById("logo-mood")?.value?.trim() || "";
  const description = document.getElementById("logo-icon-concept")?.value?.trim() || "";

  if (!brand_name || !industry) {
    showErr("logo-result", "Please fill in Brand Name and Industry.");
    return;
  }
  loading("logo-result", "Creating your logo — this may take up to 30s...");
  document.getElementById("logo-prompt-result").style.display = "none";
  try {
    const res = await post("/api/generate-logo", {
      brand_name, industry, style_keywords, typography, icon_style, mood, description
    });
    const imageUrl = `${API_BASE}${res.data.image_url}`;
    document.getElementById("logo-result").innerHTML = `
      <div style="animation:scaleIn 0.5s ease-out">
        <p class="text-[#7DB5A0] dark:text-cyan-400 font-semibold text-xs uppercase tracking-wider mb-3">✨ Generated Logo</p>
        <img src="${imageUrl}" alt="Logo for ${brand_name}" class="max-w-full max-h-72 rounded-xl border border-[#C8D5C0] dark:border-white/10 mx-auto block" />
        <div class="flex gap-3 mt-4 justify-center">
          <a href="${imageUrl}" download="${brand_name}_logo.png"
            class="px-4 py-2 text-xs font-semibold rounded-full bg-[#FF5F6D]/20 dark:bg-violet-500/20 border border-[#FF5F6D]/50 dark:border-violet-500/50
                   text-[#FF5F6D] dark:text-violet-300 hover:bg-[#FF5F6D]/30 dark:bg-violet-500/30 transition-all">
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
  const content_type = document.getElementById("mc-type").value;
  const tone = document.getElementById("mc-tone").value;

  if (!brand_description) {
    showErr("mc-result", "Please provide a brand description.");
    return;
  }
  loading("mc-result", "Crafting marketing content...");
  try {
    const res = await post("/api/generate-marketing-content", {
      brand_description, tone, content_type, language: getLanguageName(),
    });
    // Check if user requested multiple items (Slogans, Taglines, Catchphrases, etc)
    if (content_type.toLowerCase().includes("slogan") ||
      content_type.toLowerCase().includes("tagline") ||
      content_type.toLowerCase().includes("ad copy")) {
      displayContentCards("mc-result", res.data, content_type.toUpperCase());
    } else {
      showText("mc-result", res.data, content_type.toUpperCase());
    }
  } catch (e) {
    showErr("mc-result", e.message);
  }
}

async function genSocialPosts() {
  const brand_name = document.getElementById("sp-brand").value.trim();
  const product_description = document.getElementById("sp-desc").value.trim();
  const platform = document.getElementById("sp-platform").value;
  const tone = document.getElementById("sp-tone").value;

  if (!brand_name || !product_description) {
    showErr("sp-result", "Please fill in Brand Name and Product Description.");
    return;
  }
  loading("sp-result", `Generating ${platform} posts...`);
  try {
    const res = await post("/api/generate-social-posts", {
      brand_name, product_description, platform, tone, language: getLanguageName(),
    });
    displayContentCards("sp-result", res.data, `${platform.toUpperCase()} SOCIAL POSTS`);
  } catch (e) {
    showErr("sp-result", e.message);
  }
}

async function genProductDesc() {
  const product_name = document.getElementById("pd-name").value.trim();
  const features = document.getElementById("pd-features").value.trim();
  const target_audience = document.getElementById("pd-audience").value.trim();
  const tone = document.getElementById("pd-tone").value;

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
  const brand_name = document.getElementById("ec-brand").value.trim();
  const campaign_goal = document.getElementById("ec-goal").value.trim();
  const product_service = document.getElementById("ec-product").value.trim();
  const tone = document.getElementById("ec-tone").value;

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
  const industry = document.getElementById("bs-industry").value.trim();
  const mission = document.getElementById("bs-mission").value.trim();
  const tone = document.getElementById("bs-tone").value;

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
  const tone = document.getElementById("ds-tone").value;

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
    showText(containerId, data.raw, "Color Palette");
    return;
  }

  const colors = ["primary", "secondary", "accent", "background", "text"];
  const swatches = colors.map((key, i) => {
    const c = data[key];
    if (!c) return "";
    // Offset each card slightly to look like a spread of playing cards
    const rotation = (i - 2) * 5;
    const translateX = (i - 2) * 10;

    return `
      <div class="relative group" style="transform: rotate(${rotation}deg) translateX(${translateX}px); margin-bottom: 20px;">
        <div class="w-24 h-36 rounded-xl border border-[#C8D5C0] dark:border-white/20 shadow-2xl transition-all duration-300 group-hover:-translate-y-4 group-hover:rotate-0 flex flex-col overflow-hidden glass-bright"
             style="background: ${c.hex}; cursor: pointer;"
             onclick="copyText(this, '${c.hex}')">
          <div class="flex-1"></div>
          <div class="bg-white/60 dark:bg-black/40 backdrop-blur-md p-2 text-center">
            <p class="text-[10px] font-black text-[#1A1A1A] dark:text-white leading-none">${c.hex}</p>
            <p class="text-[8px] text-white/70 uppercase tracking-tighter mt-1 truncate">${c.name}</p>
          </div>
        </div>
      </div>`;
  }).join("");

  el.innerHTML = `
    <div style="animation:fadeInUp 0.4s ease-out" class="py-8 overflow-hidden">
      <p class="text-[#7DB5A0] dark:text-cyan-400 font-semibold text-xs uppercase tracking-wider mb-8 text-center">Brand Color Palette</p>
      <div class="flex justify-center items-center h-48 -space-x-12 px-10">
        ${swatches}
      </div>
      ${data.rationale ? `
        <div class="mt-12 p-4 rounded-2xl bg-white/60 dark:bg-white/5 border border-[#C8D5C0] dark:border-white/10 mx-auto max-w-lg">
          <p class="text-xs text-gray-600 dark:text-gray-300 leading-relaxed text-center italic">"${data.rationale}"</p>
        </div>` : ""}
      <div class="flex justify-center mt-6">
        <button onclick='copyText(this, ${JSON.stringify(JSON.stringify(data))})'
          class="px-5 py-2 text-xs font-bold rounded-full bg-[#FF5F6D]/10 dark:bg-violet-500/10 border border-[#FF5F6D]/40 dark:border-violet-500/40
                 text-[#FF5F6D] dark:text-violet-300 hover:bg-[#FF5F6D]/20 dark:bg-violet-500/20 transition-all">
          📋 Export Palette JSON
        </button>
      </div>
    </div>`;
}

async function genBrandGuidelines() {
  const brand_name = document.getElementById("dg-brand").value.trim();
  const industry = document.getElementById("ds-industry").value.trim();
  const mission = document.getElementById("dg-mission").value.trim();
  const tone = document.getElementById("ds-tone").value;
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
  const text = document.getElementById("sa-text").value.trim();
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
    Positive: "text-[#7DB5A0] dark:text-emerald-400",
    Negative: "text-red-400",
    Neutral: "text-[#F7C5A0] dark:text-yellow-400",
  }[data.overall_sentiment] || "text-gray-400";

  const scoreBar = (score) => {
    const pct = Math.round((score || 0) * 100);
    return `
      <div class="flex items-center gap-3">
        <div class="flex-1 h-2 bg-white/60 dark:bg-white/10 rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all duration-700"
               style="width:${pct}%;background:linear-gradient(90deg,#7c3aed,#06b6d4)"></div>
        </div>
        <span class="text-xs font-bold text-[#7DB5A0] dark:text-cyan-300 w-8 text-right">${pct}%</span>
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
            ${data.emotions.map(e => `<span class="px-3 py-1 text-xs rounded-full bg-[#FF5F6D]/20 dark:bg-violet-500/20 border border-[#FF5F6D]/30 dark:border-violet-500/30 text-[#FF5F6D] dark:text-violet-300">${e}</span>`).join("")}
          </div>
        </div>` : ""}

      ${data.strengths ? `
        <div>
          <p class="text-xs text-gray-500 mb-2">✅ Strengths</p>
          <ul class="space-y-1">${data.strengths.map(s => `<li class="text-xs text-[#7DB5A0] dark:text-emerald-300">• ${s}</li>`).join("")}</ul>
        </div>` : ""}

      ${data.improvements ? `
        <div>
          <p class="text-xs text-gray-500 mb-2">💡 Improvements</p>
          <ul class="space-y-1">${data.improvements.map(i => `<li class="text-xs text-[#F7C5A0] dark:text-amber-300">• ${i}</li>`).join("")}</ul>
        </div>` : ""}

      ${data.recommendation ? `
        <div class="p-3 rounded-xl bg-[#7DB5A0]/10 dark:bg-cyan-500/10 border border-[#7DB5A0]/20 dark:border-cyan-500/20">
          <p class="text-xs text-[#7DB5A0] dark:text-cyan-300 leading-relaxed">💬 ${data.recommendation}</p>
        </div>` : ""}
    </div>`;
}

async function genCompetitor() {
  const brand_name = document.getElementById("ca-brand").value.trim();
  const industry = document.getElementById("ca-industry").value.trim();
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
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#7DB5A0] dark:from-cyan-400 to-[#FF5F6D] dark:to-violet-500
                    flex items-center justify-center text-sm flex-shrink-0">You</div>
      </div>`;
  } else if (role === "ai") {
    html = `
      <div class="flex gap-3" style="animation:fadeInUp 0.3s ease-out">
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#FF5F6D] dark:from-violet-600 to-[#F4A0A0] dark:to-cyan-400
                    flex items-center justify-center text-sm flex-shrink-0">🤖</div>
        <div class="chat-bubble-ai">
          <p class="whitespace-pre-wrap leading-relaxed">${escaped}</p>
        </div>
      </div>`;
  } else {
    html = `
      <div class="flex gap-3" style="animation:fadeInUp 0.3s ease-out">
        <div class="w-8 h-8 rounded-full bg-[#FF5F6D]/30 dark:bg-red-500/30 flex items-center justify-center text-sm flex-shrink-0">⚠️</div>
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
      <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#FF5F6D] dark:from-violet-600 to-[#F4A0A0] dark:to-cyan-400
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

// Attach dynamic re-generation on slider mouseUp
document.addEventListener("DOMContentLoaded", () => {
  ["slider-minimalism", "slider-complexity", "slider-vibrancy"].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("mouseup", () => {
        // Re-generate image when slider released if required fields present
        const brand_name = document.getElementById("logo-name")?.value?.trim();
        const industry = document.getElementById("logo-industry")?.value?.trim();
        if (brand_name && industry) {
          genLogo();
        }
      });
      // also on touchend for mobile
      el.addEventListener("touchend", () => {
        const brand_name = document.getElementById("logo-name")?.value?.trim();
        const industry = document.getElementById("logo-industry")?.value?.trim();
        if (brand_name && industry) {
          genLogo();
        }
      }, { passive: true });
    }
  });
});

async function clearChat() {
  try {
    await fetch(`${API_BASE}/api/chat/${chatSessionId}`, { method: "DELETE" });
  } catch (_) { }
  chatSessionId = "session_" + Date.now();
  const idDisplay = document.getElementById("session-id-display");
  if (idDisplay) idDisplay.textContent = chatSessionId;

  const container = document.getElementById("chat-messages");
  if (container) {
    container.innerHTML = `
      <div class="flex gap-3">
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#FF5F6D] dark:from-violet-600 to-[#F4A0A0] dark:to-cyan-400
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
let audioChunks = [];
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

// ═══════════════════════════════════════════════════════════════════
// SIDEBAR RESIZER
// ═══════════════════════════════════════════════════════════════════
document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const resizer = document.getElementById("sidebar-resizer");
  if (!sidebar || !resizer) return;

  let isResizing = false;

  resizer.addEventListener("mousedown", (e) => {
    isResizing = true;
    document.body.style.cursor = "col-resize";
    resizer.classList.add("is-resizing");
    // Prevent text selection while dragging
    e.preventDefault();
  });

  document.addEventListener("mousemove", (e) => {
    if (!isResizing) return;

    // Calculate new width based on mouse X position
    let newWidth = e.clientX;

    // Constraints
    if (newWidth < 250) newWidth = 250;
    if (newWidth > 600) newWidth = 600;

    sidebar.style.width = newWidth + "px";
  });

  document.addEventListener("mouseup", () => {
    if (isResizing) {
      isResizing = false;
      document.body.style.cursor = "default";
      resizer.classList.remove("is-resizing");
    }
  });
});

