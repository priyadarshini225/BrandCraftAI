import re
import os

files = [
    r'c:\Users\devil\OneDrive\Desktop\BrandCraftAI\frontend\index.html',
    r'c:\Users\devil\OneDrive\Desktop\BrandCraftAI\frontend\branding.html',
    r'c:\Users\devil\OneDrive\Desktop\BrandCraftAI\frontend\js\branding.js'
]

transform_map = {
    # Text
    r'\btext-cyan-([345]00)(?![\w/])': r'text-[#7DB5A0] dark:text-cyan-\1',
    r'\btext-emerald-([345]00)(?![\w/])': r'text-[#7DB5A0] dark:text-emerald-\1',
    r'\btext-violet-([345]00)(?![\w/])': r'text-[#FF5F6D] dark:text-violet-\1',
    r'\btext-rose-([345]00)(?![\w/])': r'text-[#FF5F6D] dark:text-rose-\1',
    r'\btext-amber-([345]00)(?![\w/])': r'text-[#F7C5A0] dark:text-amber-\1',
    r'\btext-yellow-([345]00)(?![\w/])': r'text-[#F7C5A0] dark:text-yellow-\1',
    r'\btext-white(?![\w/])': r'text-[#1A1A1A] dark:text-white',
    r'\btext-slate-200(?![\w/])': r'text-gray-700 dark:text-slate-200',
    r'\btext-slate-300(?![\w/])': r'text-gray-600 dark:text-slate-300',
    r'\btext-gray-300(?![\w/])': r'text-gray-600 dark:text-gray-300',
    r'\btext-slate-400(?![\w/])': r'text-gray-600 dark:text-slate-400',
    r'\btext-slate-500(?![\w/])': r'text-gray-500 dark:text-slate-500',

    # Backgrounds
    r'\bbg-cyan-500/([0-9]+)(?![\w/])': r'bg-[#7DB5A0]/\1 dark:bg-cyan-500/\1',
    r'\bbg-emerald-500/([0-9]+)(?![\w/])': r'bg-[#7DB5A0]/\1 dark:bg-emerald-500/\1',
    r'\bbg-violet-([56]00)/([0-9]+)(?![\w/])': r'bg-[#FF5F6D]/\2 dark:bg-violet-\1/\2',
    r'\bbg-violet-([56]00)(?![\w/])': r'bg-[#FF5F6D] dark:bg-violet-\1',
    r'\bbg-red-[45]00/([0-9]+)(?![\w/])': r'bg-[#FF5F6D]/\1 dark:bg-red-500/\1',
    
    r'\bbg-white/5(?![\w/])': r'bg-white/60 dark:bg-white/5',
    r'\bbg-white/6(?![\w/])': r'bg-white/60 dark:bg-white/6',
    r'\bbg-white/8(?![\w/])': r'bg-white/60 dark:bg-white/8',
    r'\bbg-white/10(?![\w/])': r'bg-white/60 dark:bg-white/10',
    r'\bbg-white/20(?![\w/])': r'bg-white/80 dark:bg-white/20',
    r'\bbg-black/40(?![\w/])': r'bg-white/60 dark:bg-black/40',

    # Borders
    r'\bborder-cyan-[45]00/([0-9]+)(?![\w/])': r'border-[#7DB5A0]/\1 dark:border-cyan-500/\1',
    r'\bborder-emerald-[45]00/([0-9]+)(?![\w/])': r'border-[#7DB5A0]/\1 dark:border-emerald-500/\1',
    r'\bborder-violet-[56]00/([0-9]+)(?![\w/])': r'border-[#FF5F6D]/\1 dark:border-violet-500/\1',
    r'\bborder-violet-[56]00(?![\w/])': r'border-[#FF5F6D] dark:border-violet-500',
    r'\bborder-white/([0-9]+)(?![\w/])': r'border-[#C8D5C0] dark:border-white/\1',
    
    # Shadows
    r'\bshadow-violet-[56]00/([0-9]+)(?![\w/])': r'shadow-[#FF5F6D]/\1 dark:shadow-violet-500/\1',
    r'\bshadow-emerald-400/([0-9]+)(?![\w/])': r'shadow-[#7DB5A0]/\1 dark:shadow-emerald-400/\1',

    # Hovers
    r'\bhover:text-white(?![\w/])': r'hover:text-[#FF5F6D] dark:hover:text-white',
    r'\bhover:bg-white/6(?![\w/])': r'hover:bg-white/80 dark:hover:bg-white/6',
    r'\bhover:bg-violet-[56]00/([0-9]+)(?![\w/])': r'hover:bg-[#FF5F6D]/\1 dark:hover:bg-violet-500/\1',

    # Accents & focus
    r'\baccent-violet-[56]00(?![\w/])': r'accent-[#FF5F6D] dark:accent-violet-500',
    r'\baccent-cyan-[45]00(?![\w/])': r'accent-[#7DB5A0] dark:accent-cyan-500',
    r'\bfocus:border-violet-[45]00(?![\w/])': r'focus:border-[#FF5F6D] dark:focus:border-violet-400',

    # Gradients
    r'\bfrom-violet-[56]00(?![\w/])': r'from-[#FF5F6D] dark:from-violet-600',
    r'\bto-cyan-[45]00(?![\w/])': r'to-[#F4A0A0] dark:to-cyan-400',
    r'\bfrom-cyan-[45]00(?![\w/])': r'from-[#7DB5A0] dark:from-cyan-400',
    r'\bto-violet-[56]00(?![\w/])': r'to-[#FF5F6D] dark:to-violet-500',
}

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply CSS classes
    for pattern, replacement in transform_map.items():
        content = re.sub(pattern, replacement, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Added dual dark/light mode Tailwind prefixes.")
