import os

# The exact string we want to inject
magic_comment = "% !TEX root = ../finalReport.tex\n"

print("Scanning chapters directory...")

# Walk through the chapters folder
for dirpath, _, filenames in os.walk('chapters'):
    for file in filenames:
        if file.endswith('.tex'):
            filepath = os.path.join(dirpath, file)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Only add it if it's not already there
            if not content.startswith('% !TEX root'):
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(magic_comment + content)
                print(f"[SUCCESS] Added magic comment to: {filepath}")
            else:
                print(f"[SKIPPED] Already exists in: {filepath}")

print("Done! All subfiles are now linked to the root.")