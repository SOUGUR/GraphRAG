import hashlib
import json
from functools import lru_cache
from pathlib import Path

CACHE_DIR = Path(__file__).parent.parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

def get_cache_key(project_id: str, query: str, top_n: int) -> str:
    """Generate a unique cache key."""
    data = f"{project_id}:{query}:{top_n}"
    return hashlib.md5(data.encode()).hexdigest()

def get_cached_response(project_id: str, query: str, top_n: int) -> dict | None:
    """Get cached response if available."""
    cache_key = get_cache_key(project_id, query, top_n)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def cache_response(project_id: str, query: str, top_n: int, response: dict) -> None:
    """Cache the response."""
    cache_key = get_cache_key(project_id, query, top_n)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    with open(cache_file, "w") as f:
        json.dump(response, f)