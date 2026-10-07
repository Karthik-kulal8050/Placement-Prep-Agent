import json 
from .parse_inputs import read_pdf_text, read_txt
from .analyze import gap_analysis , agentic_gap_analysis

JD_FILES = ["data/jd1.txt", "data/jd2.txt", "data/jd3.txt"]

def run_comparison():
    resume = read_pdf_text("data/resume.pdf")

    for jd_file in JD_FILES:
        jd = read_txt(jd_file)
        print(f"\n{'='*60}")
        print(f"JD:{jd_file}")
        print('='*60)

        print("\n --- BASELINE (no tools) ---")
        try:
            baseline = gap_analysis(resume, jd)
            print(json.dumps(baseline, indent=2))
        except Exception as e:
            print(f"ERROR: {e}")
            baseline = None
        print("\n--- AGENTIC (with search) ---")
        try:
            agentic = agentic_gap_analysis(
                resume, jd,
                user_question = "Are any of the missing or partially-matched skills commonly asked about in interviews for this kind of role? Search if it would help."
            )
            print(json.dumps(agentic, indent=2))
        except Exception as e:
            print(f"ERROR: {e}")
            agentic = None

        print(f"\n --- DIFF NOTES for {jd_file} ---")
        if baseline and agentic:
            b_missing = set(baseline.get("missing_skills", []))
            a_missing = set(agentic.get("missing_skills", []))
            print(f"Baseline missing: {b_missing}")
            print(f"Agentic missing: {a_missing}")
            print(f"Baseline fit%:{baseline.get('overall_fit_percent')} | Agentic fit%: {agentic.get('overall_fit_percent')}")
            print(f"Agentic additional_notes: {agentic.get('additional_notes', '')[:300]}")

if __name__ == "__main__":
    run_comparison()
