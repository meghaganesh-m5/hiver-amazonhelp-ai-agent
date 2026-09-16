
from pathlib import Path
from dotenv import load_dotenv

from src.retrieval import Retrieval
from src.agent import HiverAgent

ROOT = Path(__file__).resolve().parent

load_dotenv(ROOT / ".env")

retriever = Retrieval(
    ROOT / "data/pool_b_final.csv",
    ROOT / "index/pool_b.index",
    ROOT / "index/pool_b_metadata.json",
)

agent = HiverAgent(retriever)

MESSAGES = [
    "My order is late and the tracking has not changed.",
    "The tracking says delivered but I never received the package.",
    "I want to return the item and get a refund.",
    "The product arrived damaged.",
    "Please cancel my order.",
    "I was charged more than I expected.",
    "Someone made an unauthorized charge on my account.",
    "The app is not working properly.",
    "Where is my package? It was supposed to arrive yesterday.",
    "The item I received is the wrong product.",
]

for i, message in enumerate(MESSAGES, 1):

    print("\n" + "=" * 70)
    print("CASE", i)
    print("Customer:", message)

    result = agent.run(message)

    print("Intent:", result["intent"])

    print(
        "Retrievals:",
        [
            (
                x["conversation_id"],
                round(x["score"], 3)
            )
            for x in result["retrieved"]
        ]
    )

    print("Draft:", result["draft_reply"])
    print("Decision:", result["decision"])
    print("Reason:", result["decision_reason"])
