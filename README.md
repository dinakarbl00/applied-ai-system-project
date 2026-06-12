# 🐾 PawPal+ AI Care Advisor

An AI-powered pet care assistant built with a production-grade architecture:
context-aware LLM responses, confidence scoring, a guardrail system, and a
15-case evaluation harness — all accessible via a live Streamlit web app.

🔗 **[Live Demo →](https://pawpal-plus-axsgn2plvys4jshtkmhk47.streamlit.app/)**

---

## What It Does

- **AI Care Advisor** — ask any pet care question and get a personalized answer
  using your pet's profile (name, species, breed, age) as context
- **Conversation history** — the advisor remembers earlier questions within a
  session and gives contextually aware follow-up answers
- **Confidence scoring** — every response includes a self-reported confidence
  score; responses below 0.4 are automatically flagged
- **Guardrail system** — off-topic questions are detected and rejected with a
  clear explanation
- **Evaluation harness** — 15 predefined test cases across 5 categories
  (Nutrition, Exercise, Health, Edge Cases, Guardrails) with live results
  visible in the app dashboard
- **Pet management** — add pets and schedule care tasks (walk, feeding,
  medication, vet) with priority levels, due dates, and recurrence

---

## Evaluation Results

| Metric | Result |
|--------|--------|
| Tests passed | 15 / 15 |
| Avg confidence (legitimate inputs) | 89% |
| Guardrail trigger rate | 100% (3/3) |

---

## Architecture

    ┌─────────────────────────────────────────┐
    │              Streamlit UI               │
    │   AI Advisor │ Eval Dashboard │ Pets    │
    └──────────────┬──────────────────────────┘
                   │
    ┌──────────────▼──────────────┐
    │         ai_advisor.py       │
    │  - Pet context injection    │
    │  - Conversation history     │
    │  - Confidence parsing       │
    │  - Guardrail logic          │
    └──────────────┬──────────────┘
                   │
    ┌──────────────▼──────────────┐
    │    Groq API (LLaMA 3.3 70B) │
    │  llama-3.3-70b-versatile    │
    └──────────────┬──────────────┘
                   │
    ┌──────────────▼──────────────┐
    │       pawpal_system.py      │
    │  Owner │ Pet │ Task         │
    │  Scheduler │ JSON persist   │
    └─────────────────────────────┘

---

## Design Decisions

**Why Groq over Gemini?**
Groq's free tier offers 30 RPM with sub-second latency on LLaMA 3.3 70B —
significantly faster and more reliable for a demo app than Gemini's 5 RPM
free tier. The trade-off is a dependency on Groq's infrastructure, mitigated
by standard try/except error handling.

**Why self-reported confidence scoring?**
Asking the model to append `CONFIDENCE: 0.XX` to every response is a
lightweight reliability signal that requires no additional model calls or
infrastructure. The known limitation — that LLMs tend to report high
confidence even on borderline questions — is documented honestly and would
be addressed in a production system with a separate validation model or
retrieval-grounded verification step.

**Why separate the AI layer from the scheduling layer?**
`ai_advisor.py` has zero imports from the scheduling logic in
`pawpal_system.py` beyond the `Pet` dataclass. This means the scheduling
system runs fully without an API key, and the AI layer can be swapped to a
different model provider without touching any core logic.

**Why 15 eval test cases instead of the original 6?**
6 cases is enough to verify basic behavior but insufficient to claim
reliability. 15 cases across 5 categories — including edge cases like vague
questions and species mismatches — gives a more honest picture of where the
system succeeds and where it degrades.

---

## Local Setup

    git clone https://github.com/dinakarbl/pawpal-plus.git
    cd pawpal-plus
    pip install -r requirements.txt

Create a `.env` file in the project root:

    GROQ_API_KEY=your_key_here

Get a free key at https://console.groq.com

Then run:

    streamlit run app.py      # launch the web app
    python evaluate.py        # run the eval harness in CLI
    python ai_advisor.py      # run the CLI demo

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| LLM | LLaMA 3.3 70B via Groq API |
| Frontend | Streamlit |
| Core logic | Python dataclasses |
| Persistence | JSON |
| Evaluation | Custom eval harness (evaluate.py) |
| Deployment | Streamlit Community Cloud |