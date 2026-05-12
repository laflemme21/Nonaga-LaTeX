import os
import re
from pathlib import Path
import sys

def process_latex_file(filepath):
    try:
        # Read file with UTF-8 encoding
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping {filepath} due to encoding issues (not UTF-8).")
        return

    original_content = content
    placeholders = {}
    placeholder_idx = 0

    # Function to replace matched sensitive LaTeX with a unique placeholder
    def mask(match):
        nonlocal placeholder_idx
        p = f"__PROT_{placeholder_idx}__"
        placeholders[p] = match.group(0)
        placeholder_idx += 1
        return p

    # ==========================================
    # 1. MULTILINE PROTECTIONS (Math & Code)
    # ==========================================
    MULTILINE_PROTECTIONS = [
        # Verbatim and Code Environments
        r'\\begin\{(verbatim|lstlisting|minted|spverbatim|alltt|comment)\}.*?\\end\{\1\}',
        # Math Environments
        r'\\begin\{(equation|align|gather|multline|eqnarray|math|displaymath|tikzcd|tikzpicture)\*?\}.*?\\end\{\1\*?\}',
        # Display Math
        r'(?<!\\)\$\$.*?(?<!\\)\$\$',
        r'\\\[.*?\\\]',
        # Inline Math
        r'(?<!\\)\$.*?(?<!\\)\$',
        r'\\\([^)]*?\\\)'
    ]

    for pattern in MULTILINE_PROTECTIONS:
        content = re.sub(pattern, mask, content, flags=re.DOTALL)

    # ==========================================
    # 2. SINGLE-LINE PROTECTIONS (Commands & Text)
    # ==========================================
    SINGLELINE_PROTECTIONS = [
        # Comments (everything after %)
        r'%.*',
        # Inline Verbatim \verb|...|
        r'\\verb(?P<delim>[^a-zA-Z0-9]).*?(?P=delim)',
        # Code-span commands — content is always an identifier, never prose
        r'\\texttt\{[^}]*\}',
        # Commands taking paths, URLs, references
        r'\\(?:includegraphics|url|href|input|include|cite[a-zA-Z]*|ref|cref|autoref|pageref|label|bibliography|bibliographystyle)(?:\[.*?\])?\{.*?\}',
        # Raw URLs and Emails
        r'https?://[^\s{}]+',
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        # Initials/Acronyms (e.g., J.R.R., U.S.A.)
        r'\b(?:[A-Z]\.){2,}',
        # Known abbreviations with internal periods
        r'\b(?:e\.g\.|i\.e\.|et al\.|etc\.|Ph\.D\.|M\.D\.|B\.S\.|M\.S\.|B\.A\.|M\.A\.|U\.S\.|U\.K\.|vs\.|cf\.|viz\.|al\.)',
        # Known file extensions often referenced in text
        r'\b[\w-]+\.(?:tex|bib|png|jpg|jpeg|pdf|txt|csv|json|jsonl|yaml|yml|py|js|cls|sty|eps|svg|bbl|aux|log|out)\b'
    ]

    for pattern in SINGLELINE_PROTECTIONS:
        content = re.sub(pattern, mask, content)

    # ==========================================
    # 3. APPLY PUNCTUATION FIXES (Safe Text Only)
    # ==========================================
    
    # Rule A: Letter followed by period/comma, then Letter or Number.
    # Matches: "word.Word" -> "word. Word", "text,1" -> "text, 1"
    content = re.sub(r'([a-zA-Z][.,])(?=[a-zA-Z0-9])', r'\1 ', content)

    # Rule B: Number followed by period/comma, then Letter.
    # Matches: "1.Introduction" -> "1. Introduction"
    # Note: Deliberately ignores Number -> Punctuation -> Number to protect "3.14" and "1,000"
    content = re.sub(r'([0-9][.,])(?=[a-zA-Z])', r'\1 ', content)

    # ==========================================
    # 4. RESTORE PROTECTIONS
    # ==========================================
    # Sort keys by their index in reverse order to undo safely
    for p in sorted(placeholders.keys(), key=lambda x: int(x.split('_')[3]), reverse=True):
        content = content.replace(p, placeholders[p])

    # If changes were made, write back to the file
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed spacing in: {filepath}")

def fix_tex_directory(directory):
    target_dir = Path(directory)
    
    if not target_dir.is_dir():
        print(f"Error: '{directory}' is not a valid directory.")
        return

    tex_files = list(target_dir.rglob('*.tex'))
    
    if not tex_files:
        print("No .tex files found in the specified directory.")
        return

    print(f"Found {len(tex_files)} .tex file(s). Processing...")
    
    for filepath in tex_files:
        process_latex_file(filepath)

if __name__ == "__main__":
    # If a directory is passed via terminal, use it. Otherwise, use current directory.
    target_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"Scanning directory: {os.path.abspath(target_path)}")
    fix_tex_directory(target_path)
    print("Done!")