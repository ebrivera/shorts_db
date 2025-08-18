import os, datetime as dt
from sources.youtube_embed import get_video_data
from storage.db import init, conn, upsert_video

def run(q: str, region: str, days: int = 7, max_results: int = 25):
    init()
    since = (dt.datetime.utcnow() - dt.timedelta(days=days)).isoformat("T") + "Z"
    items = get_video_data(q, region, since, max_results)
    with conn() as c:
        for it in items:
            upsert_video(c, it)
        c.commit()
    print(f"ingested {len(items)} items for {q}/{region}")

if __name__ == "__main__":
    run("latte art", "US", 7, 25)