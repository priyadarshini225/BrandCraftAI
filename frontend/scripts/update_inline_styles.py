import re
import os

files = [
    r'c:\Users\devil\OneDrive\Desktop\BrandCraftAI\frontend\index.html', 
    r'c:\Users\devil\OneDrive\Desktop\BrandCraftAI\frontend\branding.html'
]

for filepath in files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Text colors
        content = re.sub(r'\btext-cyan-[345]00\b', 'text-[#7DB5A0]', content)
        content = re.sub(r'\btext-emerald-[345]00\b', 'text-[#7DB5A0]', content)
        content = re.sub(r'\btext-violet-[345]00\b', 'text-[#FF5F6D]', content)
        content = re.sub(r'\btext-rose-[345]00\b', 'text-[#FF5F6D]', content)
        content = re.sub(r'\btext-amber-[345]00\b', 'text-[#F7C5A0]', content)
        content = re.sub(r'\btext-yellow-[345]00\b', 'text-[#F7C5A0]', content)
        content = re.sub(r'\btext-red-[45]00\b', 'text-[#FF5F6D]', content)
        content = re.sub(r'\btext-white\b', 'text-[#1A1A1A]', content)

        # Backgrounds
        content = re.sub(r'\bbg-cyan-500/([0-9]+)\b', r'bg-[#7DB5A0]/\1', content)
        content = re.sub(r'\bbg-emerald-500/([0-9]+)\b', r'bg-[#7DB5A0]/\1', content)
        content = re.sub(r'\bbg-violet-[56]00/([0-9]+)\b', r'bg-[#FF5F6D]/\1', content)
        content = re.sub(r'\bbg-violet-[56]00\b', 'bg-[#FF5F6D]', content)
        content = re.sub(r'\bbg-red-[45]00/([0-9]+)\b', r'bg-[#FF5F6D]/\1', content)
        content = re.sub(r'\bbg-white/10\b', 'bg-white/60', content)
        content = re.sub(r'\bbg-white/5\b', 'bg-white/60', content)
        content = re.sub(r'\bbg-white/6\b', 'bg-white/60', content)
        content = re.sub(r'\bbg-white/8\b', 'bg-white/60', content)
        content = re.sub(r'\bbg-white/20\b', 'bg-white/80', content)
        content = re.sub(r'\bbg-black/40\b', 'bg-white/60', content)

        # Borders
        content = re.sub(r'\bborder-cyan-[45]00/([0-9]+)\b', r'border-[#7DB5A0]/\1', content)
        content = re.sub(r'\bborder-emerald-[45]00/([0-9]+)\b', r'border-[#7DB5A0]/\1', content)
        content = re.sub(r'\bborder-violet-[56]00/([0-9]+)\b', r'border-[#FF5F6D]/\1', content)
        content = re.sub(r'\bborder-violet-[56]00\b', 'border-[#FF5F6D]', content)
        content = re.sub(r'\bborder-white/([0-9]+)\b', 'border-[#C8D5C0]', content)
        content = re.sub(r'\bborder-red-[45]00/([0-9]+)\b', r'border-[#FF5F6D]/\1', content)

        # Gradients
        content = re.sub(r'\bfrom-violet-[56]00\b', 'from-[#FF5F6D]', content)
        content = re.sub(r'\bto-cyan-[45]00\b', 'to-[#F4A0A0]', content)
        content = re.sub(r'\bfrom-cyan-[45]00\b', 'from-[#7DB5A0]', content)
        content = re.sub(r'\bto-violet-[56]00\b', 'to-[#FF5F6D]', content)

        # Shadows
        content = re.sub(r'\bshadow-violet-[56]00/([0-9]+)\b', r'shadow-[#FF5F6D]/\1', content)
        content = re.sub(r'\bshadow-black/([0-9]+)\b', r'shadow-black/\1', content)
        content = re.sub(r'\bshadow-black/60\b', 'shadow-gray-200', content)

        # Hover states
        content = re.sub(r'\bhover:text-white\b', 'hover:text-[#FF5F6D]', content)
        content = re.sub(r'\bhover:bg-white/6\b', 'hover:bg-white', content)
        content = re.sub(r'\bhover:bg-cyan-500/([0-9]+)\b', r'hover:bg-[#7DB5A0]/\1', content)
        content = re.sub(r'\bhover:bg-emerald-500/([0-9]+)\b', r'hover:bg-[#7DB5A0]/\1', content)
        content = re.sub(r'\bhover:bg-violet-[56]00/([0-9]+)\b', r'hover:bg-[#FF5F6D]/\1', content)
        
        # Additional cleanups
        content = content.replace('class="dark"', '')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

print('Tailwind utility classes mapped to new palette.')
