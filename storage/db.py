## this will be to store db for shorts

import sqlite3, os, json, time

DB_PATH = os.path.join(os.getcwd(), "youtube_shorts.db")


DDL = """
CREATE TABLE IF NOT EXISTS shorts(
  id TEXT PRIMARY KEY,
  url TEXT NOT NULL,
  title TEXT,
  description TEXT,
  tags TEXT, -- json array
  thumb_url TEXT, -- thumbnail image URL
  published_at TEXT,
  region TEXT,
  creator_id TEXT,
  creator_name TEXT,
  duration_sec INTEGER,
  stats TEXT, -- json 
  embed_html TEXT NOT NULL,
  ingest_mode TEXT NOT NULL,
  risk_nsfw REAL DEFAULT 0,
  risk_violence REAL DEFAULT 0,
  tombstoned_at TEXT,
  created_at INTEGER,
  updated_at INTEGER
);
CREATE INDEX IF NOT EXISTS vids_pub ON shorts(published_at);
"""



def conn():
    c = sqlite3.connect(DB_PATH)
    c.execute("PRAGMA journal_mode = WAL")
    c.row_factory = sqlite3.Row
    return c


def init():
    with conn() as c:
        for stmt in filter(None, DDL.split(";")):
            c.execute(stmt)


def upsert_video(c, rec: dict):
    """Insert or update a video record"""
    now = int(time.time())
    rec = rec.copy()
    
    # Convert Python lists/dicts to JSON strings for storage
    rec["tags"] = json.dumps(rec.get("tags", []))
    rec["stats"] = json.dumps(rec.get("stats", {}))
    
    c.execute("""
    INSERT INTO shorts(id, url, title, description, tags, thumb_url, published_at, 
                      region, creator_id, creator_name, duration_sec, stats, 
                      embed_html, ingest_mode, created_at, updated_at)
    VALUES(:id, :url, :title, :description, :tags, :thumb_url, :published_at,
           :region, :creator_id, :creator_name, :duration_sec, :stats,
           :embed_html, :ingest_mode, :now, :now)
    ON CONFLICT(id) DO UPDATE SET
      title=excluded.title, description=excluded.description, tags=excluded.tags,
      thumb_url=excluded.thumb_url, stats=excluded.stats, updated_at=:now;
    """, {**rec, "now": now})
