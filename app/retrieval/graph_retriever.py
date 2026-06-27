import re
from app.graph.neo4j_manager import neo4j_manager
from app.config.settings import TOP_K_GRAPH

def _extract_keywords(query: str) -> list[str]:
    """Extract identifier-like keywords from a natural-language query."""
    # Keep camelCase, snake_case, and capitalized words
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", query)
    # Filter out very short / common English stop words
    stop = {"the", "a", "an", "is", "are", "was", "were", "be", "of", "in", "on",
            "to", "for", "and", "or", "how", "what", "where", "why", "does", "do",
            "i", "you", "we", "they", "it", "this", "that", "my", "code", "function"}
    return [t for t in tokens if len(t) > 2 and t.lower() not in stop]

def graph_search(query: str, project_id: str, k: int = TOP_K_GRAPH) -> list[dict]:
    """
    Traverse the Neo4j graph to find code related to the query.
    Strategy:
      1. Find nodes whose name/docstring matches query keywords
      2. Pull in their immediate neighbors (callers, callees, parents, children)
      3. Return source code with a proximity score
    """
    keywords = _extract_keywords(query)
    if not keywords:
        return []

    results: dict[str, dict] = {}

    # --- Phase 1: direct matches on name / docstring ---
    match_query = """
    MATCH (n)
    WHERE n.project_id = $project_id
      AND (n:Function OR n:Class OR n:File OR n:Variable)
      AND (
        ANY(kw IN $keywords WHERE toLower(n.name) CONTAINS toLower(kw))
        OR ANY(kw IN $keywords WHERE toLower(COALESCE(n.module,'')) CONTAINS toLower(kw))
      )
    OPTIONAL MATCH (n)-[r]-(m)
    RETURN labels(n)[0] AS label, n.id AS id, n.name AS name,
           n.source_code AS source, n.path AS path,
           type(r) AS rel, labels(m)[0] AS neighbor_label, m.name AS neighbor_name
    LIMIT 200
    """
    with neo4j_manager.driver.session() as session:
        records = session.run(match_query, project_id=project_id, keywords=keywords).data()

    for rec in records:
        node_id = rec["id"]
        if node_id not in results:
            results[node_id] = {
                "id": node_id,
                "text": rec.get("source") or rec.get("name") or "",
                "metadata": {
                    "type": (rec.get("label") or "").lower(),
                    "name": rec.get("name"),
                    "path": rec.get("path"),
                    "project_id": project_id,
                    "graph_score": 0.0,
                    "related": [],
                },
                "score": 0.0,
            }
        # Direct match = high score
        results[node_id]["score"] = max(results[node_id]["score"], 1.0)
        results[node_id]["metadata"]["graph_score"] = results[node_id]["score"]

        # Neighbor = lower score, but still useful context
        if rec.get("neighbor_name") and rec.get("rel"):
            results[node_id]["metadata"]["related"].append({
                "relation": rec["rel"],
                "neighbor": rec["neighbor_name"],
                "neighbor_type": rec.get("neighbor_label"),
            })

    # --- Phase 2: 1-hop call / inherit expansion from matched nodes ---
    if results:
        matched_ids = list(results.keys())
        expand_query = """
        MATCH (seed)
        WHERE id(seed) IN $seed_ids
        MATCH (seed)-[r:CALLS|INHERITS|DEFINES]-(neighbor)
        WHERE neighbor.project_id = $project_id
          AND (neighbor:Function OR neighbor:Class)
          AND neighbor.source_code IS NOT NULL
        RETURN neighbor.id AS id, neighbor.name AS name,
               neighbor.source_code AS source, type(r) AS rel,
               labels(neighbor)[0] AS label
        LIMIT 100
        """
        with neo4j_manager.driver.session() as session:
            expanded = session.run(
                expand_query,
                seed_ids=[int(nid) for nid in matched_ids if nid.isdigit()] or matched_ids,
                project_id=project_id,
            ).data()

        for rec in expanded:
            nid = rec["id"]
            if nid in results:
                # Boost existing
                results[nid]["score"] = min(1.0, results[nid]["score"] + 0.3)
            else:
                results[nid] = {
                    "id": nid,
                    "text": rec.get("source") or "",
                    "metadata": {
                        "type": (rec.get("label") or "").lower(),
                        "name": rec.get("name"),
                        "project_id": project_id,
                        "graph_score": 0.3,
                        "related_via": rec.get("rel"),
                    },
                    "score": 0.3,
                }

    # Sort by score desc, take top k
    ranked = sorted(results.values(), key=lambda x: x["score"], reverse=True)[:k]
    # Normalize related lists to strings for JSON
    for r in ranked:
        if isinstance(r["metadata"].get("related"), list):
            r["metadata"]["related"] = [
                f"{x['relation']}->{x['neighbor']}" for x in r["metadata"]["related"][:10]
            ]
    return ranked