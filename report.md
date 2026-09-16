# Hiver AmazonHelp AI Support Agent — Evaluation Report

## 1. Problem framing

The goal is an AI customer-support system for AmazonHelp that classifies incoming messages, retrieves historically resolved support examples, drafts a grounded response, and decides whether the case can be auto-handled or should be escalated.

Good means consistent intent classification, useful historical grounding without invented current facts, concise replies, and conservative escalation for high-risk or account-specific cases.

The project deliberately did not build fine-tuning, intent-tagged retrieval, multi-language support, or production account integrations.

## 2. Data and evaluation

The Golden Set contains 215 manually labelled examples across eight frozen intents. Pool B contains 8,178 resolved historical examples. The Golden Set and Pool B were isolated with zero exact and near-duplicate overlap.

Retrieval uses normalized all-MiniLM-L6-v2 embeddings with FAISS IndexFlatIP.

## 3. System architecture

```text
Customer message
      |
classify_intent
      |
retrieve_context
      |
draft_reply
      |
decide_escalation
      |
Final intent + evidence + draft + decision + reason
```

Deterministic hard-trigger rules handle fraud/unauthorized activity, account compromise, legal/formal disputes, and safety cases before LLM escalation reasoning.

## 4. Results

| System | Intent Accuracy | Intent Macro-F1 | Decision Accuracy | Escalate Precision | Escalate Recall |
|---|---:|---:|---:|---:|---:|
| Trivial baseline | 16.74% | 3.59% | 49.30% | 0.00% | 0.00% |
| Zero-shot Groq | 73.49% | 72.65% | 58.60% | 61.90% | 47.71% |
| RAG Groq | 73.02% | 70.74% | 69.30% | 68.70% | 72.48% |

Zero-shot substantially improves intent classification over the trivial baseline. RAG has similar intent performance to zero-shot but improves escalation decision accuracy, escalation precision and escalation recall.

Reply quality was evaluated on groundedness, correctness, tone and helpfulness. Human-vs-LLM agreement was measured on a 25-example sample. The strongest observed agreement was RAG groundedness (Spearman rho = 0.590, p = 0.002, n = 25).

## 5. Failure analysis

### 1. Historical-fact and timeframe transfer
Retrieved operational details can be reused as current guarantees.

**Hypothesis:** retrieval does not inherently distinguish reusable resolution guidance from case-specific facts.

**Next step:** evidence verification/filtering before drafting.

### 2. Weak retrieval for security-related queries
Security/fraud messages can retrieve generic payment/account examples because retrieval is semantic-only.

**Next step:** intent-aware retrieval or a dedicated security route.

### 3. Awkward multi-source reply composition
Different retrieved resolution paths can be combined into an unnatural response.

**Next step:** reranking and evidence filtering.

### 4. Escalation-decision variance
Borderline cancellation, modification, disputed-charge and incomplete cases can vary.

**Next step:** stronger policy rules and targeted examples.

### 5. Intent boundary confusion
Neighboring categories such as delivery vs. missing-not-received and payment vs. account/security can be difficult in short Twitter messages.

**Next step:** targeted boundary examples and intent-aware retrieval.

## 6. What is misleading about my headline number?

The RAG intent accuracy of 73.0% is not a production accuracy estimate. The Golden Set was deliberately balanced for coverage rather than real-world frequency, contains 215 examples, and uses one annotator. Retrieval quality varies by intent and escalation policy contains judgement calls. Human-vs-LLM agreement was measured on a 25-example sample.

## 7. What I would build next week

1. Intent-aware retrieval.
2. A second human annotator and adjudication.
3. A stronger paid-model comparison.
4. An evidence evaluator/filter before drafting.
5. More targeted boundary examples.

## 8. Reproducibility

The repository contains the frozen Golden Set, Pool B, FAISS index and completed baseline/RAG/judge outputs. The README demo is intentionally separate from the full evaluation.
