# 🎯 Placement Prep Agent

An AI agent that compares a resume against a job description, identifies skill gaps, and recommends what to prioritize learning next — using tool-calling to ground its analysis in real-time web search rather than static text comparison alone.

**🔗 Live demo:** https://placement-prep-agent-t47c.onrender.com/

## Architecture
Resume (PDF) + Job Description (text)
↓
LLM (Groq, Llama 3.3 / gpt-oss-120b)
↓
Decides: answer directly, or call a tool?
├── search_web(query) → verify skill relevance / interview trends
└── find_learning_resource(skill) → suggest a concrete next step
↓
Structured JSON: matched skills, gaps, fit %, top priority, resource link


## Key engineering decisions

- **Tool-calling agent vs single-pass LLM call**: evaluated both approaches head-to-head on 3 real job descriptions. The agentic (tool-using) version consistently surfaced 2–5 additional specific gaps per JD — verified to be genuinely present in the source JD text but missed by the single-pass baseline, particularly requirements phrased as responsibilities (e.g., "monitor model performance") rather than named technologies.
- **Constructive framing over raw gap-listing**: an early version simply listed missing skills, which read as discouraging rather than actionable. Redesigned the prompt and output schema to surface one `top_priority_to_learn` recommendation instead of an undifferentiated list, with a concrete `learning_resource` link — shifting the tool from "critic" to "coach."
- **Resilient resource links**: web-search-sourced links occasionally return stale URLs. Mitigated by preferring stable, high-authority platforms (Coursera, AWS, Hugging Face, etc.) when available, and falling back to a live search-query link (which cannot 404) otherwise.
- **Lightweight by design**: unlike a RAG system, this agent needs no local embedding models or vector search — all reasoning happens via the Groq API. This kept the deployed footprint small enough to run reliably on Render's free tier without the memory constraints that affect embedding-heavy apps.

## Evaluation

Compared baseline (single-pass JD/resume comparison) against the agentic (tool-calling) version on 3 real job descriptions (ML Engineer, AI/ML Software Engineer roles, all fresher-level).

| | Baseline | Agentic |
|---|---|---|
| Gaps identified (avg. per JD) | Fewer, keyword-level | 2–5 more per JD, including responsibility-phrased requirements |
| Grounding | Document text only | Document text + live search verification |
| Output | Flat gap list | Prioritized single focus area + concrete resource |

All additional gaps surfaced by the agentic version were manually verified against the source JD text to confirm they weren't hallucinated.

## Features

- Upload any resume (PDF) + paste any job description
- Agent decides, on its own, when to search the web vs. answer directly
- Structured output: matched skills, gaps, fit %, one prioritized next step, and a resource link
- REST API (FastAPI) + simple web UI
- Dockerized, deployed on Render

## Known limitations

- **Resource links aren't always current**: web search can return outdated URLs. Mitigated via stable-domain preference and a guaranteed-working search-link fallback, but not 100% guaranteed to always be a perfect, specific link.
- **No persistence**: each analysis is independent; there's no history of past analyses or tracking of skill progress over time.
- **Single search backend**: uses DuckDuckGo search, which is free but less comprehensive than paid search APIs (e.g., Tavily, Serper).

## Tech stack

**Backend:** Python, FastAPI, Groq (Llama 3.3 / gpt-oss-120b), PyMuPDF, DuckDuckGo Search (tool-calling)
**Frontend:** Vanilla HTML/CSS/JS
**Infra:** Docker, Render

## Run locally

```bash
git clone <your-repo-url>
cd placement-agent
pip install -r requirements.txt
# add GROQ_API_KEY to .env
python -m uvicorn app.main:app --reload
```

Or with Docker:
```bash
docker build -t placement-agent .
docker run -p 8000:8000 --env-file .env placement-agent
```

## Evaluation methodology

See `app/compare_eval.py`. Runs the same job description through both the baseline and agentic pipelines, prints a diff of matched/missing skills and fit percentage, and surfaces the agentic version's additional reasoning (`additional_notes`) for manual verification against source JD text.