from typing import Any


def _score(query: str, text: str) -> int:
    q_terms = [term for term in query.lower().split() if term]
    lower = text.lower()
    return sum(1 for term in q_terms if term in lower)


def run_search(query: str, documents: list[dict[str, Any]], top_k: int = 3) -> list[dict[str, Any]]:
    if not query.strip():
        return []

    ranked: list[tuple[int, dict[str, Any]]] = []
    for doc in documents:
        text = f"{doc.get('title', '')}\n{doc.get('content', '')}"
        points = _score(query, text)
        if points > 0:
            ranked.append((points, doc))

    ranked.sort(key=lambda item: item[0], reverse=True)
    results: list[dict[str, Any]] = []
    for score, doc in ranked[:top_k]:
        snippet = doc.get("content", "")[:240].replace("\n", " ")
        results.append(
            {
                "document_id": doc.get("id"),
                "title": doc.get("title"),
                "score": score,
                "snippet": snippet,
            }
        )
    return results

