import re
import os

files = [
    r'c:\Users\devil\OneDrive\Desktop\BrandCraftAI\frontend\index.html', 
    r'c:\Users\devil\OneDrive\Desktop\BrandCraftAI\frontend\branding.html'
]

style_replacement = """
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }

    body {
      font-family: 'Inter', system-ui, sans-serif;
      background: #FFFFFF;
      color: #1A1A1A;
      overflow-x: hidden;
      min-height: 100vh;
    }

    /* Mesh gradient - Peach to Soft Pink & Sage Mist to White */
    .mesh-bg {
      position: fixed; inset: 0; z-index: 0; pointer-events: none;
      background:
        radial-gradient(ellipse 80% 60% at 0% 0%,   rgba(247,197,160,0.50) 0%, transparent 60%),
        radial-gradient(ellipse 70% 60% at 100% 20%, rgba(244,160,160,0.40) 0%, transparent 55%),
        radial-gradient(ellipse 60% 50% at 40% 90%,  rgba(200,213,192,0.40) 0%, transparent 50%),
        radial-gradient(ellipse 50% 40% at 80% 70%,  rgba(125,181,160,0.25) 0%, transparent 50%);
      background-color: #F9F9F9;
    }

    /* Grid lines */
    .grid-lines {
      position: fixed; inset: 0; z-index: 0; pointer-events: none;
      background-image:
        linear-gradient(rgba(125,181,160,0.15) 1px, transparent 1px),
        linear-gradient(90deg, rgba(125,181,160,0.15) 1px, transparent 1px);
      background-size: 60px 60px;
    }

    /* Bubbles */
    .bubbles-container { position: fixed; inset: 0; z-index: 1; pointer-events: none; overflow: hidden; }
    .bubble {
      position: absolute;
      animation: floatBubble linear infinite;
    }
    @keyframes floatBubble {
      0%   { transform: translateY(0) translateX(0) scale(0.7); opacity: 0; }
      8%   { opacity: 1; }
      50%  { transform: translateY(-50vh) translateX(calc(var(--drift) * 0.5)) scale(1); }
      92%  { opacity: 0.8; }
      100% { transform: translateY(-115vh) translateX(var(--drift)) scale(1.1); opacity: 0; }
    }
    @keyframes ambientFloat {
      0%   { transform: translate(0,0) scale(1);   opacity: 0; }
      15%  { opacity: 1; }
      50%  { transform: translate(var(--dx), var(--dy)) scale(1.12); }
      85%  { opacity: 0.75; }
      100% { transform: translate(calc(var(--dx)*2), calc(var(--dy)*2)) scale(0.85); opacity: 0; }
    }
    @keyframes sideDrift {
      0%   { transform: translateX(0) translateY(var(--drift)) scale(0.8); opacity: 0; }
      10%  { opacity: 0.9; }
      90%  { opacity: 0.6; }
      100% { transform: translateX(var(--dx)) translateY(calc(var(--drift) + var(--dy))) scale(1.05); opacity: 0; }
    }

    /* Liquid Glass */
    .glass {
      background: rgba(255,255,255,0.6);
      backdrop-filter: blur(20px) saturate(160%); -webkit-backdrop-filter: blur(20px) saturate(160%);
      border: 1px solid rgba(125, 181, 160, 0.3);
      box-shadow: inset 0 0 10px rgba(255,255,255,0.5), 0 4px 20px rgba(0,0,0,0.05);
    }
    .glass-bright {
      background: rgba(255,255,255,0.8);
      backdrop-filter: blur(24px) saturate(180%); -webkit-backdrop-filter: blur(24px) saturate(180%);
      border: 1px solid rgba(125, 181, 160, 0.4);
      box-shadow: inset 0 0 10px rgba(255,255,255,0.8), 0 4px 20px rgba(0,0,0,0.05);
    }
    .glass-card {
      background: rgba(255,255,255,0.5);
      backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
      border: 1px solid rgba(125, 181, 160, 0.3);
      border-radius: 20px;
    }

    /* Gradient text */
    .grad {
      background: linear-gradient(135deg, #FF5F6D 0%, #F4A0A0 50%, #F7C5A0 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }

    /* Buttons */
    .btn-glow {
      position: relative;
      background: linear-gradient(135deg, #FF5F6D 0%, #F4A0A0 60%, #F7C5A0 100%);
      background-size: 200% 200%; color: #fff; border: none; cursor: pointer;
      overflow: hidden; transition: all 0.3s ease;
      animation: pulseGlow 3s ease-in-out infinite;
      box-shadow: 0 4px 15px rgba(255, 95, 109, 0.3);
    }
    .btn-glow::before {
      content: ""; position: absolute; inset: 0;
      background: linear-gradient(135deg, rgba(255,255,255,0.4), transparent);
      opacity: 0; transition: opacity 0.3s;
    }
    .btn-glow:hover::before { opacity: 1; }
    .btn-glow:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(255, 95, 109, 0.5); }
    .btn-glow:disabled { opacity: 0.45; cursor: not-allowed; transform: none; animation: none; box-shadow: none; }

    .btn-outline {
      background: rgba(255, 255, 255, 0.5); border: 1px solid rgba(125, 181, 160, 0.5);
      color: #1A1A1A; cursor: pointer; transition: all 0.3s ease; backdrop-filter: blur(8px);
    }
    .btn-outline:hover {
      background: rgba(244, 160, 160, 0.2); border-color: #FF5F6D;
      color: #FF5F6D; transform: translateY(-1px);
    }

    /* Feature card */
    .feat-card { transition: all 0.35s cubic-bezier(0.34,1.56,0.64,1); cursor: pointer; }
    .feat-card:hover {
      transform: translateY(-8px) scale(1.01);
      background: rgba(255, 255, 255, 0.8) !important;
      border-color: rgba(255, 95, 109, 0.45) !important;
      box-shadow: 0 24px 64px rgba(244, 160, 160, 0.2), 0 0 0 1px rgba(255, 95, 109, 0.2);
    }

    /* Stat card */
    .stat-card { transition: all 0.3s ease; }
    .stat-card:hover { transform: scale(1.05); border-color: rgba(255, 95, 109, 0.5) !important; }

    /* Scroll reveal */
    .reveal { opacity: 0; transform: translateY(32px); transition: opacity 0.7s ease, transform 0.7s ease; }
    .reveal.visible { opacity: 1; transform: translateY(0); }
    .d1 { transition-delay: 0.1s; } .d2 { transition-delay: 0.2s; } .d3 { transition-delay: 0.3s; }
    .d4 { transition-delay: 0.4s; } .d5 { transition-delay: 0.5s; } .d6 { transition-delay: 0.6s; }

    /* Browser mockup */
    .browser-frame { background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(125, 181, 160, 0.3); border-radius: 16px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1); }
    .browser-bar { background: rgba(255, 255, 255, 0.4); border-bottom: 1px solid rgba(125, 181, 160, 0.2); padding: 10px 16px; display: flex; align-items: center; gap: 8px; }
    .dot { width: 10px; height: 10px; border-radius: 50%; }

    /* Hero glow */
    .hero-glow {
      position: absolute; width: 700px; height: 700px; border-radius: 50%;
      background: radial-gradient(circle, rgba(255, 95, 109, 0.15) 0%, transparent 65%);
      left: 50%; top: 50%; transform: translate(-50%, -50%); pointer-events: none; z-index: 0;
    }

    /* Badge pulse */
    .badge-dot { width: 7px; height: 7px; border-radius: 50%; background: #FF5F6D; box-shadow: 0 0 8px rgba(255, 95, 109, 0.8); animation: badgePulse 2s ease-in-out infinite; }
    @keyframes badgePulse { 0%,100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.5); opacity: 0.7; } }

    /* Typed cursor */
    #typed-text::after { content: "|"; animation: blink 1s step-end infinite; color: #FF5F6D; }
    @keyframes blink { 0%,50% { opacity: 1; } 51%,100% { opacity: 0; } }

    /* Chip */
    .chip { display: inline-flex; align-items: center; gap: 6px; padding: 5px 14px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
    .icon-box { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 22px; background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(125, 181, 160, 0.3); flex-shrink: 0; }
    .footer-link { color: #555555; font-size: 13px; transition: color 0.2s; text-decoration: none; }
    .footer-link:hover { color: #FF5F6D; }

    /* Spin slow */
    @keyframes spinSlow { from { transform: translate(-50%,-50%) rotate(0deg); } to { transform: translate(-50%,-50%) rotate(360deg); } }
    .spin-slow { animation: spinSlow 20s linear infinite; }
    .spin-slow-rev { animation: spinSlow 14s linear infinite reverse; }

    /* Inputs */
    .dark-input {
      background: rgba(255, 255, 255, 0.5); border: 1px solid rgba(125, 181, 160, 0.4);
      color: #1A1A1A; border-radius: 12px; padding: 11px 14px; width: 100%; font-size: 14px;
      transition: all 0.2s ease; outline: none; font-family: inherit; backdrop-filter: blur(8px);
    }
    .dark-input:focus { border-color: #FF5F6D; background: rgba(255, 255, 255, 0.8); box-shadow: 0 0 0 3px rgba(255, 95, 109, 0.15); }
    .dark-input::placeholder { color: rgba(26, 26, 26, 0.4); }

    select.dark-input {
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23FF5F6D' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
      background-repeat: no-repeat; background-position: right 14px center; padding-right: 38px; cursor: pointer; -webkit-appearance: none; appearance: none;
    }
    .dark-input option, select option { background: #FFFFFF; color: #1A1A1A; }
    #lang-selector { background-color: rgba(255, 255, 255, 0.6); -webkit-appearance: none; appearance: none; color: #1A1A1A; border: 1px solid rgba(125,181,160,0.5); }

    /* Tabs */
    .tab-btn {
      padding: 9px 16px; border-radius: 10px; font-size: 12px; font-weight: 600;
      color: rgba(26, 26, 26, 0.6); transition: all 0.25s ease; white-space: nowrap;
      border: 1px solid transparent; cursor: pointer; background: transparent;
    }
    .tab-btn:hover { color: #1A1A1A; background: rgba(255, 255, 255, 0.5); }
    .tab-btn.active { color: #FF5F6D; background: rgba(255, 95, 109, 0.1); border-color: rgba(255, 95, 109, 0.3); box-shadow: 0 0 15px rgba(255, 95, 109, 0.1); }
    .tab-content { display: none; }
    .tab-content.active { display: block; animation: fadeInUp 0.35s ease-out; }

    .sub-tab-btn {
      padding: 6px 13px; border-radius: 8px; font-size: 11px; font-weight: 600;
      color: rgba(26, 26, 26, 0.6); border: 1px solid rgba(125, 181, 160, 0.3);
      cursor: pointer; transition: all 0.2s ease; background: transparent;
    }
    .sub-tab-btn:hover { color: #1A1A1A; background: rgba(255, 255, 255, 0.5); }
    .sub-tab-btn.active { color: #FF5F6D; background: rgba(255, 95, 109, 0.1); border-color: rgba(255, 95, 109, 0.3); }
    .sub-tab-content { display: none; }
    .sub-tab-content.active { display: block; animation: fadeInUp 0.3s ease-out; }

    /* Results */
    .result-area {
      min-height: 120px; border-radius: 14px; background: rgba(255, 255, 255, 0.4);
      border: 1px solid rgba(125, 181, 160, 0.3); padding: 18px; margin-top: 14px; backdrop-filter: blur(4px);
    }
    label { display: block; font-size: 11px; font-weight: 700; color: rgba(26, 26, 26, 0.6); text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 6px; }

    /* Chat */
    .chat-messages { height: 360px; overflow-y: auto; scrollbar-width: thin; scrollbar-color: rgba(255, 95, 109, 0.3) transparent; }
    .chat-bubble-user {
      background: linear-gradient(135deg, rgba(255, 95, 109, 0.15), rgba(247, 197, 160, 0.15));
      border: 1px solid rgba(255, 95, 109, 0.3); border-radius: 16px 16px 4px 16px;
      padding: 11px 15px; margin-left: auto; max-width: 80%; font-size: 14px; color: #1A1A1A;
    }
    .chat-bubble-ai {
      background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(125, 181, 160, 0.3);
      border-radius: 16px 16px 16px 4px; padding: 11px 15px; max-width: 80%; font-size: 14px; line-height: 1.6; color: #1A1A1A;
    }

    /* Miscellaneous */
    .color-swatch { width: 46px; height: 46px; border-radius: 10px; cursor: pointer; transition: transform 0.2s; border: 2px solid rgba(255, 255, 255, 0.6); box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .color-swatch:hover { transform: scale(1.12); }
    .logo-preview img { max-width: 100%; max-height: 300px; border-radius: 12px; border: 1px solid rgba(125, 181, 160, 0.3); }

    .kw-tag {
      display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;
      background: rgba(255, 95, 109, 0.1); border: 1px solid rgba(255, 95, 109, 0.3); color: #FF5F6D; cursor: pointer; transition: all 0.2s;
    }
    .kw-tag:hover { background: rgba(255, 95, 109, 0.2); }
    .kw-tag .rm { color: rgba(255, 95, 109, 0.6); font-size: 11px; }

    .brand-result-card { cursor: pointer; border-radius: 16px; padding: 14px; background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(125, 181, 160, 0.3); transition: all 0.25s ease; }
    .brand-result-card:hover { background: rgba(255, 255, 255, 0.8); border-color: rgba(255, 95, 109, 0.4); }
    .brand-result-card.selected { background: rgba(255, 95, 109, 0.1); border-color: rgba(255, 95, 109, 0.5); }
    
    .top-rec-card { border-radius: 20px; padding: 22px; background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(125, 181, 160, 0.4); }

    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 95, 109, 0.4); border-radius: 4px; }
    .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
    .scrollbar-hide::-webkit-scrollbar { display: none; }

    #sidebar {
      width: 340px; min-width: 220px; max-width: 60vw; flex-shrink: 0;
      border-right: 1px solid rgba(125, 181, 160, 0.3); overflow-y: auto;
      overflow-x: hidden; background: rgba(255, 255, 255, 0.3); position: relative;
      display: flex; flex-direction: column;
    }
    #resize-handle {
      position: absolute; top: 0; right: -3px; width: 6px; height: 100%;
      cursor: col-resize; z-index: 50; transition: background 0.15s;
    }
    #resize-handle:hover, #resize-handle.active { background: rgba(255, 95, 109, 0.4); }
    body.resizing { cursor: col-resize !important; user-select: none !important; }
    body.resizing * { cursor: col-resize !important; user-select: none !important; }

    #main-panel { flex: 1; overflow-y: auto; }

    @media (max-width: 768px) {
      #sidebar { width: 100% !important; min-width: unset; max-width: unset; border-right: none; border-bottom: 1px solid rgba(125, 181, 160, 0.3); }
      #resize-handle { display: none; }
      body { height: auto; }
    }

    .panel-overlay { position: fixed; inset: 0; background: rgba(255, 255, 255, 0.6); backdrop-filter: blur(4px); z-index: 200; opacity: 0; pointer-events: none; transition: opacity 0.3s ease; }
    .panel-overlay.open { opacity: 1; pointer-events: all; }

    .slide-panel {
      position: fixed; top: 0; right: 0; height: 100vh; width: 440px; max-width: 96vw;
      z-index: 201; background: #FFFFFF; border-left: 1px solid rgba(125, 181, 160, 0.3);
      transform: translateX(100%); transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
      overflow-y: auto; display: flex; flex-direction: column;
      box-shadow: -10px 0 30px rgba(0,0,0,0.05);
    }
    .slide-panel.open { transform: translateX(0); }

    .panel-header {
      position: sticky; top: 0; z-index: 10; background: rgba(255, 255, 255, 0.8);
      backdrop-filter: blur(20px); border-bottom: 1px solid rgba(125, 181, 160, 0.3);
      padding: 20px 24px; display: flex; align-items: center; justify-content: space-between;
    }
    .panel-close {
      width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
      background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(125, 181, 160, 0.3);
      color: #7DB5A0; cursor: pointer; font-size: 16px; transition: all 0.2s;
    }
    .panel-close:hover { background: rgba(255, 95, 109, 0.1); color: #FF5F6D; border-color: rgba(255, 95, 109, 0.3); }

    .panel-body { padding: 24px; flex: 1; }
    .panel-section { margin-bottom: 28px; }
    .panel-section-title { font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #FF5F6D; margin-bottom: 12px; }

    .project-card {
      background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(125, 181, 160, 0.3);
      border-radius: 14px; padding: 14px 16px; margin-bottom: 10px; transition: all 0.2s;
    }
    .project-card:hover { background: rgba(255, 255, 255, 0.8); border-color: #FF5F6D; }

    .settings-btn {
      padding: 9px 18px; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer;
      transition: all 0.2s; border: 1px solid rgba(125, 181, 160, 0.3);
      background: rgba(255, 255, 255, 0.6); color: #1A1A1A;
    }
    .settings-btn:hover { background: rgba(255, 95, 109, 0.1); border-color: #FF5F6D; color: #FF5F6D; }
    .settings-btn.danger:hover { background: rgba(255, 95, 109, 0.1); border-color: #FF5F6D; color: #FF5F6D; }
    .settings-btn.primary { background: linear-gradient(135deg, #FF5F6D, #F4A0A0); border-color: transparent; color: #fff; box-shadow: 0 4px 10px rgba(255, 95, 109, 0.3); }
    .settings-btn.primary:hover { opacity: 0.9; transform: translateY(-1px); box-shadow: 0 6px 15px rgba(255, 95, 109, 0.4); }

    .empty-state { text-align: center; padding: 40px 20px; color: #7DB5A0; }
    .empty-state .icon { font-size: 40px; margin-bottom: 12px; opacity: 0.6; }
"""

for filepath in files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Replace <style> block
        content = re.sub(r'<style>.*?</style>', f'<style>\\n{style_replacement}\\n  </style>', content, flags=re.DOTALL)
        
        # 2. Text colors
        content = content.replace('text-white', 'text-[#1A1A1A]')
        content = content.replace('text-slate-400', 'text-gray-600')
        content = content.replace('text-slate-300', 'text-gray-600')
        content = content.replace('text-slate-500', 'text-gray-500')
        
        # 3. Background/Border colors
        content = re.sub(r'bg-white/5(?![0-9])', 'bg-white/60', content)
        content = re.sub(r'bg-white/10(?![0-9])', 'bg-white/60', content)
        content = re.sub(r'bg-white/8(?![0-9])', 'bg-white/60', content)
        content = re.sub(r'bg-white/6(?![0-9])', 'bg-white/60', content)
        content = content.replace('bg-[#0c0c23]', 'bg-white')
        
        # 4. Remove dark class
        content = content.replace('class="dark"', '')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

print("Styles updated successfully.")
