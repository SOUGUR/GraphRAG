from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.config.settings import GOOGLE_API_KEY, LLM_MODEL, RERANK_TOP_N

_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a code-relevance judge. Given a user query and a list of code snippets, "
     "return ONLY a JSON array of the snippet IDs ordered from MOST to LEAST relevant. "
     "Drop any snippet that is clearly irrelevant. "
     "Output format: [\"id1\", \"id2\", ...]. No prose, no markdown."),
    ("human",
     "Query: {query}\n\nSnippets:\n{snippets_block}\n\nReturn JSON array of IDs:"),
])

def _get_llm():
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
    )

def rerank(query: str, candidates: list[dict], top_n: int = RERANK_TOP_N) -> list[dict]:
    """Use Gemini to rerank a merged list of candidates."""
    if not candidates:
        return []
    if len(candidates) <= top_n:
        return candidates

    # Build a block listing each candidate
    block_lines = []
    for i, c in enumerate(candidates):
        meta = c.get("metadata", {})
        name = meta.get("name") or meta.get("file_path") or c["id"]
        # Truncate text to keep prompt small
        snippet = (c.get("text") or "")[:600].replace("\n", " \\n ")
        block_lines.append(f"[{i}] id={c['id']} | {meta.get('type','')} | {name}\n{snippet}")
    snippets_block = "\n---\n".join(block_lines)

    try:
        llm = _get_llm()
        chain = _PROMPT | llm
        response = chain.invoke({"query": query, "snippets_block": snippets_block})
        content = response.content.strip()
        # Strip markdown fences if present
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        import json
        ordered_ids = json.loads(content)
        if not isinstance(ordered_ids, list):
            return candidates[:top_n]

        id_to_candidate = {c["id"]: c for c in candidates}
        reranked = [id_to_candidate[i] for i in ordered_ids if i in id_to_candidate]
        # Append any leftovers
        seen = {c["id"] for c in reranked}
        for c in candidates:
            if c["id"] not in seen:
                reranked.append(c)
        return reranked[:top_n]
    except Exception:
        # Fallback: keep original order
        return candidates[:top_n]