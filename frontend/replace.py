import os

files = ['index.html', 'css/style.css', 'js/app.js']

replacements = {
    'var(--emerald)': 'var(--gold)',
    'var(--emerald-soft)': 'var(--gold-soft)',
    'var(--emerald-deep)': 'var(--gold)',
    '16, 185, 129': '245, 158, 11',
    '52, 211, 153': '251, 191, 36',
    '5, 150, 105': '217, 119, 6',
    '#10B981': '#F59E0B',
    '#34D399': '#FBBF24',
    '#059669': '#D97706',
    '--emerald:': '--emerald-old:',
    '--emerald-soft:': '--emerald-soft-old:',
    '--emerald-deep:': '--emerald-deep-old:'
}

for filename in files:
    filepath = os.path.join('e:\\Codes\\Finovo\\frontend', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Replacements complete.")
