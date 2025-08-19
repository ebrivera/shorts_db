from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import sqlite3, json, math, time
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from index.faiss_index import search as vec_search

app = FastAPI(title="OmniShorts", version="0.1.0")


#### consts and models
DAY_IN_SECONDS = 86400.0


## this will define what a VIDEO obj looks like
class VideoResult(BaseModel):
    id: str
    title: str
    url: str
    embed_html: str
    score: float
    similarity: float
    recency: float
    popularity: float
    creator_name: str
    published_at: str


# Defines what the response for a search is
class SearchResponse(BaseModel):
    query: str
    results: List[VideoResult]
    total_found: int
    filters_applied: Dict[str, Any]




## db connections
def db():
    """connect db with row factory"""
    c = sqlite3.connect("youtube_shorts.db")
    c.row_factory = sqlite3.Row
    return c

def parse_view_count(stats_json: str) -> int:
    """Extract view count from YouTube stats JSON"""
    
    stats = json.loads(stats_json or "{}")
    return int(stats.get("viewCount", 0))



### helper functions
def parse_view_count(stats_json: str) -> int:
    stats = json.loads(stats_json or {}) # failsafe 
    return int(stats.get("viewCount", 0))


def recency_score(published_at: str) -> float:
    if not published_at:
        return 0.0

    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    days_passed = (datetime.now(timezone.utc) - dt).total_seconds() / DAY_IN_SECONDS

    if days_passed <= 2.0:
        return 1.0
    elif days_passed >= 7.0:
        return 0.0
    
    # this is going to calculate linear dropoff 
    return max(0.0, 1.0 - (days_passed - 2.0) / 5.0 ) 

def normalize_scores(scores: List[float]) -> List[float]:
    if not values:
        return values

    min_val, max_val = min(scores), max(scores)

    ## numbers that are the same will be given equal scores
    if math.isclose(min_val, max_val, rel_tol=1e-9):
        return [0.5 for _ in values]  # neutral score instead of 0

    return [(v - min_val) / (max_val - min_val) for v in values]

# todo
def diversity_pentalty(results: List[tuple], diversity: bool) -> List[tuple]:
    return results



@app.get("/v1/search", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length = 1, description="search query"),
    k: int = Query(10, ge: 1, le: 50, description="number of results"),
    days: int = Query(7, ge=1, le=10, description="Max age in days"),
    region: str = Query(None, description="region filter (ie US, SG)"),
    diversity: bool = Query(True, description="creator diversity"),
    weight_similarity: float = Query(0.6, ge=0.0, le=1.0),
    weight_recency: float = Query(0.2, ge=0.0, le=1.0), 
    weight_popularity: float = Query(0.2, ge=0.0, le=1.0)    
    ):

    start_time = time.time()

    total_weight = w_similarity + w_recency + w_popularity
    if not math.isclose(total_weight, 1.0, rel_tol=0.01):
        raise HTTPException(
            status_code=400, 
            detail=f"weights must sum to 1.0, instead: {total_weight:.3f}"
        )

    candidate_count = min(k * 3, 100)
    vector_results = vec_search(q, top_k=candidate_count)

    if not vector_results:
        return SearchResponse(
            query=q, results=[], total_found=0,
            filters_applied={"days": days, "region": region}
        )
    
    # get metadata for candidates
    video_ids = [video_id for video_id, _ in vector_results]


    # this is in order to help with anti-sql injections
    placeholders = ",".join("?" * len(video_ids))
    query_sql = f"""
        SELECT id, title, url, embed_html, published_at, region, 
               creator_name, stats, creator_id
        FROM shorts 
        WHERE id IN ({placeholders}) 
        AND tombstoned_at IS NULL
    """

    video_metadata = {}
    with db() as conn:
        for row in conn.execute(query_sql, video_ids):
            video_metadata[row["id"]] = dict(row) # create a dictionary with the id's

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    candidates = []


    for video_id, similarity in vector_results:
        video = video_metadata.get(video_id)
        if not video:
            continue

        if video.get("published_at"):
            pub_date = datetime.fromisoformat(
                video["published_at"].replace("Z", "+00:00")
            )
            if pub_date < cutoff_date:
                continue
        candidates.append((video_id, float(similarity), video))

    if not candidates:
        return SearchResponse(
            query=q, results=[], total_found=0,
            filters_applied={"days": days,"filtered_out": len(vector_results)}
        )

    similarities = [similarity for _, similarity, _ in candidates]
    recency_scores = [recency_score(video.get("published_at", "")) 
        for _, _, video in candidates]

    view_counts = [parse_view_count(video.get("stats", "{}")) for _, _, video in candidates]

    log_view_counts = [math.log1p(count) for count in view_counts]
    popularity_scores = normalize_scores(log_view_counts)

    scored_results = []
    for (video_id, similarity, video), recency, popularity in zip(candidates, recency_scores, popularity_scores):
        # Weighted combination
        final_score = (weight_similarity * similarity + 
                      weight_recency * recency + 
                      weight_popularity * popularity)
        
        scored_results.append((final_score, video))

    scored_results.sort(key=lambda x: x[0], reverse=True)
    top_results = scored_results[:k]

    

    









if __name__ == "__main__":
    parse_view_count()

