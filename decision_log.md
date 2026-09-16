# Decision Log

1. **AmazonHelp selected** for volume, intent diversity and a clear escalation split.
2. **LangGraph selected** for explicit application stages and escalation branching.
3. **FAISS selected over Chroma** for a lightweight, portable retrieval artifact.
4. **Eight intents derived from data** rather than borrowing an unrelated taxonomy.
5. **Intent = what; risk = whether** so the same intent can have different escalation outcomes.
6. **Golden Set stratified for coverage** so rare/high-risk intents are represented.
7. **Trivial baseline excludes Golden Set** to avoid bias from deliberate Golden Set balancing.
8. **Semantic-only retrieval retained** instead of intent-tagging to reduce cost/complexity.
9. **Resolved example definition tightened** to exclude generic deflections.
10. **Escalating cases still receive drafts** so humans have a useful starting point.
11. **Hard triggers precede LLM escalation reasoning** for deterministic safety handling.
12. **Model choice evolved from Claude/Gemini experiments to Groq** because of practical budget/access constraints.
13. **Evidence evaluator designed but not included** in the frozen evaluation; retained as a next-step improvement.
14. **Human agreement measured on 25 examples** because double-labelling all 215 was not feasible.
15. **Pathological reconstructed threads filtered downstream** because the affected fraction was small.
