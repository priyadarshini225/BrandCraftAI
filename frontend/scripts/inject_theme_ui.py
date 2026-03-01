import os
import re

html_files = [
    r'c:\Users\devil\OneDrive\Desktop\BrandCraftAI\frontend\index.html',
    r'c:\Users\devil\OneDrive\Desktop\BrandCraftAI\frontend\branding.html'
]

css_block = """
    /* Liquid Glass Light Mode (Default) */
    body {
      background: #F9F9F9;
      color: #1A1A1A;
    }
    .mesh-bg {
      background:
        radial-gradient(ellipse 80% 60% at 0% 0%,   rgba(247,197,160,0.50) 0%, transparent 60%),
        radial-gradient(ellipse 70% 60% at 100% 20%, rgba(244,160,160,0.40) 0%, transparent 55%),
        radial-gradient(ellipse 60% 50% at 40% 90%,  rgba(200,213,192,0.40) 0%, transparent 50%),
        radial-gradient(ellipse 50% 40% at 80% 70%,  rgba(125,181,160,0.25) 0%, transparent 50%);
      background-color: #F9F9F9;
    }
    .grid-lines {
      background-image:
        linear-gradient(rgba(125,181,160,0.15) 1px, transparent 1px),
        linear-gradient(90deg, rgba(125,181,160,0.15) 1px, transparent 1px);
    }
    .glass {
      background: rgba(255,255,255,0.6);
      border: 1px solid rgba(125, 181, 160, 0.3);
      box-shadow: inset 0 0 10px rgba(255,255,255,0.5), 0 4px 20px rgba(0,0,0,0.05);
    }
    .glass-bright {
      background: rgba(255,255,255,0.8);
      border: 1px solid rgba(125, 181, 160, 0.4);
      box-shadow: inset 0 0 10px rgba(255,255,255,0.8), 0 4px 20px rgba(0,0,0,0.05);
    }
    .glass-card {
      background: rgba(255, 255, 255, 0.45);
      border: 1px solid rgba(125, 181, 160, 0.3);
    }
    .btn-glow {
      background: linear-gradient(135deg, #FF5F6D 0%, #F4A0A0 60%, #F7C5A0 100%);
      box-shadow: 0 4px 15px rgba(255, 95, 109, 0.3);
    }
    .btn-glow::before {
      background: linear-gradient(135deg, rgba(255,255,255,0.4), transparent);
    }
    .btn-glow:hover { box-shadow: 0 10px 25px rgba(255, 95, 109, 0.5); }
    
    .btn-outline {
      background: rgba(255, 255, 255, 0.5); border: 1px solid rgba(125, 181, 160, 0.5);
      color: #1A1A1A;
    }
    .btn-outline:hover {
      background: rgba(244, 160, 160, 0.2); border-color: #FF5F6D;
      color: #FF5F6D;
    }
    .grad {
      background: linear-gradient(135deg, #FF5F6D 0%, #F4A0A0 50%, #F7C5A0 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }
    .feat-card:hover {
      background: rgba(255, 255, 255, 0.8) !important;
      border-color: rgba(255, 95, 109, 0.45) !important;
      box-shadow: 0 24px 64px rgba(244, 160, 160, 0.2), 0 0 0 1px rgba(255, 95, 109, 0.2);
    }
    .browser-frame { background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(125, 181, 160, 0.3); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1); }
    .browser-bar { background: rgba(255, 255, 255, 0.4); border-bottom: 1px solid rgba(125, 181, 160, 0.2); }
    .hero-glow {
      background: radial-gradient(circle, rgba(255, 95, 109, 0.15) 0%, transparent 65%);
    }
    .badge-dot { background: #FF5F6D; box-shadow: 0 0 8px rgba(255, 95, 109, 0.8); }
    #typed-text::after { color: #FF5F6D; }
    .icon-box { background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(125, 181, 160, 0.3); }

    /* Dark Mode Overrides */
    html.dark body { background: #060614; color: #f1f5f9; }
    html.dark .mesh-bg {
      background:
        radial-gradient(ellipse 80% 60% at 0% 0%,   rgba(124,58,237,0.20) 0%, transparent 60%),
        radial-gradient(ellipse 70% 60% at 100% 20%, rgba(6,182,212,0.14)  0%, transparent 55%),
        radial-gradient(ellipse 60% 50% at 40% 90%,  rgba(236,72,153,0.11) 0%, transparent 50%),
        radial-gradient(ellipse 50% 40% at 80% 70%,  rgba(16,185,129,0.08) 0%, transparent 50%);
      background-color: #060614;
    }
    html.dark .grid-lines {
      background-image:
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
    }
    html.dark .glass {
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.09);
      box-shadow: none;
    }
    html.dark .glass-bright {
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.13);
      box-shadow: none;
    }
    html.dark .glass-card {
      background: rgba(255, 255, 255, 0.045);
      border: 1px solid rgba(255, 255, 255, 0.10);
      box-shadow: none;
    }
    html.dark .btn-glow {
      background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 60%, #ec4899 100%);
      box-shadow: none;
    }
    html.dark .btn-glow::before {
      background: linear-gradient(135deg, rgba(255,255,255,0.15), transparent);
    }
    html.dark .btn-glow:hover { box-shadow: 0 20px 60px rgba(124,58,237,0.55); }
    html.dark .btn-outline {
      background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.18); color: #e2e8f0;
    }
    html.dark .btn-outline:hover {
      background: rgba(255,255,255,0.12); border-color: rgba(139,92,246,0.5); color: #fff;
    }
    html.dark .grad {
      background: linear-gradient(135deg, #a78bfa 0%, #67e8f9 50%, #f472b6 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }
    html.dark .feat-card:hover {
      background: rgba(255,255,255,0.08) !important;
      border-color: rgba(6,182,212,0.45) !important;
      box-shadow: 0 24px 64px rgba(6,182,212,0.12), 0 0 0 1px rgba(6,182,212,0.2);
    }
    html.dark .browser-frame { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.10); box-shadow: none; }
    html.dark .browser-bar { background: rgba(255,255,255,0.06); border-bottom: 1px solid rgba(255,255,255,0.08); }
    html.dark .hero-glow {
      background: radial-gradient(circle, rgba(124,58,237,0.13) 0%, transparent 65%);
    }
    html.dark .badge-dot { background: #a78bfa; box-shadow: 0 0 8px rgba(167,139,250,0.8); }
    html.dark #typed-text::after { color: #a78bfa; }
    html.dark .icon-box { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.10); }
    html.dark .tab-btn.active { color: #a78bfa; background: rgba(167, 139, 250, 0.1); border-color: rgba(167, 139, 250, 0.3); box-shadow: 0 0 15px rgba(167, 139, 250, 0.1); }
"""

toggle_ui = """
        <button id="theme-toggle" class="bg-white/60 dark:bg-white/5 border border-[#C8D5C0] dark:border-white/20 w-9 h-9 rounded-full flex items-center justify-center text-[#1A1A1A] dark:text-white hover:bg-white/80 dark:hover:bg-white/10 transition-all mr-2">
          <!-- Moon icon (shows in light mode) -->
          <svg id="theme-icon-dark" class="w-4 h-4 hidden dark:block" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
          <!-- Sun icon (shows in dark mode) -->
          <svg id="theme-icon-light" class="w-4 h-4 block dark:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>
        </button>
"""

toggle_script = """
  <script>
    const themeBtn = document.getElementById('theme-toggle');
    function applyTheme(isDark) {
      if (isDark) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
      }
    }
    const stored = localStorage.getItem('theme');
    // Default to light mode unless dark is explicitly stored or pref is set
    if (stored === 'dark') {
      applyTheme(true);
    } else if (stored === 'light') {
      applyTheme(false);
    } else {
      applyTheme(false); // Default Light
    }
    if (themeBtn) {
      themeBtn.addEventListener('click', () => {
        const isDark = document.documentElement.classList.contains('dark');
        applyTheme(!isDark);
      });
    }
  </script>
"""

for fpath in html_files:
    if not os.path.exists(fpath): continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Append CSS Block (only if not already added)
    if '/* Liquid Glass Light Mode (Default) */' not in content:
        content = content.replace('</style>', css_block + '\n  </style>')

    # Insert toggle UI right before <select id="lang-selector">
    if 'id="theme-toggle"' not in content:
        content = re.sub(r'(<select id="lang-selector")', toggle_ui + r'\n        \1', content)
        
    # Insert javascript bundle
    if 'document.documentElement.classList.contains(\'dark\')' not in content:
        content = content.replace('</body>', toggle_script + '\n</body>')

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Injected dual theme CSS, UI button, and Javascript toggles.")
