# Hiver AmazonHelp AI Support Agent

An AI customer-support agent built for the Hiver SDE Intern take-home using the AmazonHelp portion of the Kaggle Customer Support on Twitter dataset.

The system classifies customer messages into eight data-derived intents, retrieves historically resolved examples, drafts a grounded reply, and decides Auto-handle vs. Escalate with a reason. The evaluated RAG workflow has four application stages: classification, retrieval, reply drafting, and escalation decisioning.

## Setup

```bash
git clone <https://github.com/meghaganesh-m5/hiver-amazonhelp-ai-agent>
cd hiver-amazonhelp-ai-agent
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install:
```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your own Groq API key.

Never commit `.env` or a real API key.

## Quick demo

```bash
python demo.py
```

The demo loads the pre-built 8,178-row Pool B corpus and FAISS index and processes 10 representative customer messages end-to-end. It prints intent, retrieval results, draft reply and escalation decision.

It does **not** regenerate the 215-example evaluation.

Expected runtime is a few minutes on a normal laptop, including first-time SentenceTransformer model loading.

## Full evaluation

The full evaluation was completed separately on the frozen 215-example Golden Set. Saved outputs are under `results/`.

| System | Intent Accuracy | Intent Macro-F1 | Decision Accuracy | Escalate Precision | Escalate Recall |
|---|---:|---:|---:|---:|---:|
| Trivial baseline | 16.74% | 3.59% | 49.30% | 0.00% | 0.00% |
| Zero-shot Groq | 73.49% | 72.65% | 58.60% | 61.90% | 47.71% |
| RAG Groq | 73.02% | 70.74% | 69.30% | 68.70% | 72.48% |

The main observed effect is similar intent performance for zero-shot and RAG, with stronger escalation-decision metrics for RAG.

## Repository structure

- `data/` — frozen Pool B and Golden Set
- `index/` — FAISS index and metadata
- `src/` — runnable retrieval and agent implementation
- `results/` — completed evaluations
- `notebooks/` — selected project notebooks
- `demo.py` — small end-to-end demo

The raw `twcs.csv` is intentionally excluded.

## Report and decision log

- `report.md`
- `decision_log.md`

## Known limitations

Known issues include historical-fact/timeframe transfer, weaker retrieval for some security queries, awkward multi-source composition, escalation boundary variance, and neighboring intent confusion. Full details are in `report.md`.

## Docker

```bash
docker build -t hiver-amazonhelp-agent .
docker run --rm -e GROQ_API_KEY=your_key_here hiver-amazonhelp-agent
```



