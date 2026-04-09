import os
import time
import re
from openai import OpenAI

# ==============================
# Configuration
# ==============================

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://models.inference.ai.azure.com"
)

INPUT_FILE = "source/dowson_mythology_cleaned.txt.txt"
OUTPUT_FILE = "data/triplets_raw.txt"
BATCH_SIZE = 3
MAX_CHARS = 12000

# ==============================
# Load and split text
# ==============================

def load_entries(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Split entries based on uppercase headings
    entries = re.split(r'\n(?=[A-Z][A-Z\-]+\.)', text)
    entries = [e.strip() for e in entries if len(e.strip()) > 50]

    return entries

# ==============================
# Prompt
# ==============================

SYSTEM_PROMPT = """
You are a knowledge graph extractor for Hindu mythology.

STRICT RULES:

1. Output ONLY triplets:
{"Subject" : "Relation" : "Object"}

2. ONLY ONE subject and ONE object per triplet

3. NO lists like A,B,C

4. Use ONLY information from given text
DO NOT use external knowledge

5. Normalize names:
- Fix broken OCR names like:
  Su-bhadra → Subhadra
  Dur-yodhana → Duryodhana

6. Allowed relations:

Family:
Father Of, Mother Of,
Son Of, Daughter Of,
Brother Of, Sister Of,
Husband Of, Wife Of, Spouse Of,
Grandfather Of, Grandmother Of,
Grandson Of, Granddaughter Of,
Great-Grandfather Of, Great-Grandmother Of,
Great Grandson Of, Great Granddaughter Of,
Ancestor Of, Descendant Of,
Uncle Of, Aunt Of,
Nephew Of, Niece Of,
Cousin Of

Social:
Friend, Enemy Of

Learning:
Student Of, Teacher Of,

Power:
King Of, Servat Of, Ruler Of

Other:
Is, Also Known As, Killed, Killed By, Devotee Of

7. Apply bidirectional relations ONLY for:
Family + Friend

8. DO NOT use:
fight, fought

9. NO explanation
ONLY triplets

10. Extract maximum relationships
"""

# ==============================
# API Call
# ==============================

def call_api(entry):
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": entry}
                ],
                temperature=0
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Retry {attempt+1}: {e}")
            time.sleep(2)

    return ""

# ==============================
# Clean output
# ==============================

def clean_output(text):
    lines = text.split("\n")
    return "\n".join(
        line.strip() for line in lines
        if line.strip().startswith("{") and line.strip().endswith("}")
    )

# ==============================
# Main pipeline
# ==============================

def main():
    entries = load_entries(INPUT_FILE)

    print(f"Total entries: {len(entries)}")

    for i in range(0, len(entries), BATCH_SIZE):
        print(f"Processing {i}/{len(entries)}")

        batch = entries[i:i+BATCH_SIZE]
        combined_input = "\n\n".join(batch)

        if len(combined_input) > MAX_CHARS:
            combined_input = combined_input[:MAX_CHARS]

        raw_output = call_api(combined_input)

        if not raw_output:
            continue

        cleaned = clean_output(raw_output)

        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(cleaned + "\n\n")

        time.sleep(2)

if __name__ == "__main__":
    main()