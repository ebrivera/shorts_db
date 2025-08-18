import os, datetime as dt
from sources.youtube_embedded import get_video_data
from storage.db import init, conn, upsert_video

def run(q: str, region: str, days: int = 7, max_results: int = 25):
    init()
    since = (dt.datetime.utcnow() - dt.timedelta(days=days)).isoformat("T") + "Z"
    items = get_video_data(
        query=q, 
        region=region, 
        since=since, 
        max_rqesults=max_results
    )
    
    print(f"Found {len(items)} videos from YouTube API")  # Debug line
    
    with conn() as c:
        for it in items:
            print(f"Inserting: {it['id']} - {it['title']}")  # Debug line
            upsert_video(c, it)
        c.commit()
    print(f"ingested {len(items)} items for {q}/{region}")

if __name__ == "__main__":
    run("latte art", "US", 7, 25)
