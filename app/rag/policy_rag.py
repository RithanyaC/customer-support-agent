import os
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class LocalPolicyRAG:
    def __init__(self, policy_path: str | None = None):
        self.policy_path = Path(policy_path) if policy_path else Path(__file__).resolve().parents[2] / "data" / "policies.txt"
        self.documents = self._load_documents()
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.index = self.vectorizer.fit_transform(self.documents)

    def _load_documents(self):
        if not self.policy_path.exists():
            raise FileNotFoundError(f"Policy file not found: {self.policy_path}")
        text = self.policy_path.read_text(encoding="utf-8")
        chunks = re.split(r"(?=^\s*(?:Return Policy|Refund Policy|Exchange Policy|Warranty Policy|FAQ)\s*$)", text, flags=re.MULTILINE)
        cleaned = []
        for chunk in chunks:
            chunk = chunk.strip()
            if chunk:
                cleaned.append(chunk)
        return cleaned

    def retrieve(self, query: str, k: int = 3):
        if not query:
            return []
        transformed = self.vectorizer.transform([query])
        scores = cosine_similarity(transformed, self.index).flatten()
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
        results = []
        for idx, score in ranked[:k]:
            if score <= 0:
                continue
            section = self.documents[idx].splitlines()[0].strip() if self.documents[idx] else "Policy"
            results.append({"section": section, "text": self.documents[idx], "score": round(float(score), 4)})
        return results


def build_policy_query(state):
    msg = state.get("user_message", "")
    if state.get("intent") == "return":
        return f"return policy for {msg}"
    if state.get("intent") == "refund":
        return f"refund policy and processing timeline for {msg}"
    if state.get("intent") == "exchange":
        return f"exchange policy for {msg}"
    if state.get("intent") == "warranty":
        return f"warranty policy for {msg}"
    return msg
