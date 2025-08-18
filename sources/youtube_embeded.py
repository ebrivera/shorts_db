
# this is going to get our youtube data

import os, re, requests, datetime as dt
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")



YOUTUBE_BASE_URL = "https://www.googleapis.com/youtube/v3"
ISO8601 = re.compile(r"PT(?:(\d+)M)?(?:(\d+)S)?")

def parse_duration(duration: str) -> int:
    """Convert PT1M30S to 90 seconds"""
    m = ISO8601.fullmatch(duration)
    if not m: return 0
    mins = int(m.group(1) or 0)
    secs = int(m.group(2) or 0)
    return mins*60 + secs



def get_video_data(query: str, max_results: int = 50, since: str = None, region: str = "US") -> list[dict]:
    """
    Search for YouTube videos matching the query, return list of dicts for true shorts (<60s).
    """
    # Search for videos
    search_response = requests.get(YOUTUBE_BASE_URL + "/search", params={
        "key": API_KEY,
        "part": "snippet",
        "q": query,
        "type": "video",
        "regionCode": region,
        "publishedAfter": since,
        "videoDuration": "short",
        "maxResults": max_results,
        "relevanceLanguage": "en"
    })
    search_data = search_response.json()
    video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]
    if not video_ids:
        return []

    # Get video details
    video_response = requests.get(YOUTUBE_BASE_URL + "/videos", params={
        "key": API_KEY,
        "part": "snippet,contentDetails,statistics",
        "id": ",".join(video_ids)
    })
    v = video_response.json()

    out = []
    for it in v.get("items", []):
        dur = parse_duration(it["contentDetails"]["duration"])
        if dur > 60 or dur == 0:  # keep true shorts
            continue
        snip = it["snippet"]
        thumb = snip["thumbnails"].get("high", snip["thumbnails"]["default"])["url"]
        out.append({
            "id": f"yt:{it['id']}", # youtube id
            "url": f"https://www.youtube.com/watch?v={it['id']}", # url for video
            "title": snip.get("title", ""), # title of video
            "description": snip.get("description", ""), # desc
            "tags": snip.get("tags", []), # tags
            "thumb_url": thumb, #thumbnail from thumb
            "published_at": snip.get("publishedAt"), # time published
            "region": region, #where from
            "creator_id": snip.get("channelId"), # who created  (id)
            "creator_name": snip.get("channelTitle"), #who created (name)
            "duration_sec": dur, #duration of video
            "stats": it.get("statistics", {}), #stats
            "embed_html": f"https://www.youtube.com/embed/{it['id']}", #embed html
            "ingest_mode": "EMBED_ONLY", #ingest mode
        })
    return out


if __name__ == "__main__":
    since = (dt.datetime.utcnow() - dt.timedelta(days=7)).isoformat("T") + "Z"
    video_data = get_video_data("python")

    print(video_data[0])