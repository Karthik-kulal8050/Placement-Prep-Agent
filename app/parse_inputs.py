import pymupdf as fitz
from pathlib import Path

def read_pdf_text(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()

def read_txt(path):
    return Path(path).read_text(encoding="utf-8").strip()

if __name__ == "__main__":
    resume = read_pdf_text("data/resume.pdf")
    jd = read_txt("data/jd1.txt")
    print("--- RESUME (First 300 chars) ---")
    print(resume[:300])
    print("\n --- JD (first 300 chars) ---")
    print(jd[:3000])
