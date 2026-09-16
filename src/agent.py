
import json
import os
import re
from groq import Groq

INTENTS = [f"I{i}" for i in range(1, 9)]
VALID_DECISIONS = {"Auto-handle", "Escalate"}

TAXONOMY = """
I1 Delivery Status & Delay
I2 Missing / Not Received
I3 Returns & Refunds
I4 Damaged / Wrong / Defective Product
I5 Order Cancellation / Modification
I6 Payment / Pricing / Charges
I7 Account / Security / Access
I8 Product / Technical / General Support
""".strip()


def hard_triggers(message):
    text = message.lower()

    rules = [
        (
            "fraud_or_unauthorized_activity",
            r"\b(unauthori[sz]ed|fraud|stolen|not me|someone used my|didn't make this|did not make this)\b"
        ),
        (
            "account_compromise",
            r"\b(hacked|account compromised|account taken over|can't access my account|cannot access my account)\b"
        ),
        (
            "legal_formal_dispute",
            r"\b(lawyer|attorney|legal action|lawsuit|consumer court|sue)\b"
        ),
        (
            "safety_issue",
            r"\b(injury|injured|unsafe|dangerous|fire|electric shock)\b"
        ),
    ]

    return [
        name
        for name, pattern in rules
        if re.search(pattern, text)
    ]


class HiverAgent:
    def __init__(self, retriever, model="openai/gpt-oss-20b"):
        key = os.getenv("GROQ_API_KEY")

        if not key:
            raise RuntimeError(
                "GROQ_API_KEY is missing. Copy .env.example to .env."
            )

        self.client = Groq(api_key=key)
        self.retriever = retriever
        self.model = model

    def ask(self, prompt, temperature=0.1, max_tokens=600):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            reasoning_effort="low",
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("Empty model response.")

        obj = json.loads(content)

        if not isinstance(obj, dict):
            raise ValueError("Expected JSON object.")

        return obj

    def run(self, message):

        # Node 1: classify intent
        cls = self.ask(
            f"""
Classify this customer-support message into exactly one intent.

{TAXONOMY}

Customer message:
{message}

Return JSON with keys intent and justification.
The intent must be exactly one of I1,I2,I3,I4,I5,I6,I7,I8.
""",
            max_tokens=350
        )

        if cls.get("intent") not in INTENTS:
            raise ValueError(
                "Invalid intent: " + str(cls.get("intent"))
            )

        # Node 2: retrieve historical examples
        retrieved = self.retriever.query(message, 3)

        evidence = "\n\n".join(
            f"""
Example {i+1}:
Customer issue: {x['customer_issue_text']}
Historical resolution: {x['final_resolution_text']}
"""
            for i, x in enumerate(retrieved)
        )

        # Node 3: draft reply
        draft = self.ask(
            f"""
Draft a concise customer-support reply.

Customer message:
{message}

Intent:
{cls["intent"]}

Historical examples:
{evidence}

Use the examples only as resolution guidance.
Do not copy case-specific names, dates, exact times, promises or timelines.
Do not claim access to the customer's account/order.
Do not invent current tracking or refund status.

Return JSON with key draft_reply.
""",
            temperature=0.2,
            max_tokens=650
        )

        reply = draft.get("draft_reply")

        if not reply:
            raise ValueError("Empty draft reply.")

        # Node 4: escalation decision
        flags = hard_triggers(message)

        if flags:
            return {
                "intent": cls["intent"],
                "justification": cls.get("justification", ""),
                "retrieved": retrieved,
                "draft_reply": reply,
                "decision": "Escalate",
                "decision_reason": (
                    "Hard rule triggered: " + ", ".join(flags)
                ),
                "hard_trigger_flags": flags,
            }

        dec = self.ask(
            f"""
Decide whether this customer-support case should be Auto-handle or Escalate.

Intent:
{cls["intent"]}

Customer message:
{message}

Proposed reply:
{reply}

Escalate for fraud/unauthorized activity, account compromise,
legal/formal disputes, safety issues, significant/disputed financial
issues, repeated failed resolution, insufficient information, or
account/order-specific actions the support channel cannot directly perform.

Return JSON with decision and decision_reason.
The decision must be exactly Auto-handle or Escalate.
""",
            max_tokens=350
        )

        if dec.get("decision") not in VALID_DECISIONS:
            raise ValueError(
                "Invalid decision: " + str(dec.get("decision"))
            )

        return {
            "intent": cls["intent"],
            "justification": cls.get("justification", ""),
            "retrieved": retrieved,
            "draft_reply": reply,
            "decision": dec["decision"],
            "decision_reason": dec.get("decision_reason", ""),
            "hard_trigger_flags": [],
        }
