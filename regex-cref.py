import os
import re

# Regex to match single references: e.g., "Section \ref{label}" or "Table~\ref{label}"
pattern_single = re.compile(r'\b(?:Section|Figure|Table|Appendix|Equation)s?(?:~| )\\ref\{([^}]+)\}')

# Regex to match double references: e.g., "Figures \ref{label1} and \ref{label2}"
pattern_double = re.compile(r'\b(?:Section|Figure|Table|Appendix|Equation)s?(?:~| )\\ref\{([^}]+)\}\s+and(?:~| )\\ref\{([^}]+)\}')

def apply_cleveref(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Replace double references first (e.g., Figures \ref{a} and \ref{b} -> \cref{a,b})
    content = pattern_double.sub(r'\\cref{\1,\2}', content)
    
    # 2. Replace single references (e.g., Section \ref{a} -> \cref{a})
    content = pattern_single.sub(r'\\cref{\1}', content)

    # Only write back if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[SUCCESS] Upgraded references in: {filepath}")
    else:
        print(f"[SKIPPED] No references needed upgrading in: {filepath}")

# Walk through all directories and subdirectories
print("Starting Overleaf/LaTeX reference upgrade...")
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.tex'):
            full_path = os.path.join(root, file)
            apply_cleveref(full_path)
            
print("Upgrade complete! You can now commit and push to GitHub.")