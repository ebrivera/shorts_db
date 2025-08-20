# OmniShorts: RAG-Powered Short-Form Content Search Engine

**Semantic search for the world's fastest-growing content format**

## 🎯 Executive Summary

OmniShorts brings semantic search to short-form video content. Inspired by how ChatGPT leverages Reddit for opinions and niche knowledge, I recognized that valuable insights increasingly live in short-form videos - yet remain inaccessible to AI systems. This API enables LLMs and applications to tap into video knowledge through intelligent search.

## 💡 Core Capabilities

1. **Customer-Centric Problem Solving**: Bridging the gap where LLMs can't access video knowledge
2. **Rapid Iteration**: Working pipeline in 3.5 days while traveling
3. **Full-Stack Implementation**: End-to-end ownership from data ingestion to REST API
4. **Data Integration**: Unified YouTube API, embeddings, and metadata into actionable insights
5. **Production-Ready**: SQL injection prevention, performance optimization, proper error handling

## 🏗️ Architecture

```
YouTube API → Ingestion Pipeline → SQLite Database
                     ↓                    ↓
              Text Embeddings  →   FAISS Index
              (MiniLM-L6)               ↓
                                  FastAPI REST API
```

## 🔧 Technical Implementation

### Search Intelligence

- **Semantic Similarity (60%)**: Content relevance via sentence transformers
- **Recency Score (20%)**: Temporal decay function for fresh content
- **Popularity (20%)**: Log-normalized engagement metrics
- **Regional Filtering**: Geographic content targeting
- **Sub-100ms latency** for typical queries

### Key Components

**Data Ingestion** (`sources/youtube_embedded.py`)

- YouTube Data API v3 integration
- Filters true shorts (<60 seconds)
- Extracts metadata: titles, descriptions, tags, statistics

**Vector Search** (`index/faiss_index.py`)

- FAISS for efficient similarity search
- Combines title + tags + description for comprehensive embeddings
- Cosine similarity via normalized inner product

**REST API** (`search_api.py`)

```python
GET /v1/search
  ?q=<query>           # Search query
  &k=10                # Number of results
  &days=7              # Recency filter
  &region=US           # Geographic filter
  &weight_similarity=0.6  # Tunable weights
```

## 📊 Sample Response

```json
{
  "query": "latte art tutorial",
  "results": [
    {
      "id": "yt:abc123",
      "title": "Perfect Rosetta in 30 Seconds",
      "score": 0.8932,
      "similarity": 0.9123,
      "recency": 0.85,
      "popularity": 0.7234,
      "creator_name": "BaristaDaily"
    }
  ],
  "total_found": 42
}
```

## 🚀 Quick Start

```bash
# Install & configure
pip install -r requirements.txt
export YOUTUBE_API_KEY=your_api_key

# Initialize & ingest
python storage/db.py
python ingest.py

# Launch API
uvicorn search_api:app --reload

# Test search
curl "http://localhost:8000/v1/search?q=latte%20art"
```

## 🔮 Roadmap

- **Transcript Integration**: ASR for full content understanding
- **Multi-modal Fusion**: Combining text, visual, and audio signals
- **User Interface**: React-based search frontend
- **Feedback Loop**: Click-through optimization

## 🎯 Impact

This technology enables:

- **Enhanced LLM Context**: Give AI assistants access to video knowledge
- **Content Discovery**: Surface relevant tutorials and insights instantly
- **Market Intelligence**: Track emerging trends in video content
- **Cross-Modal RAG**: Foundation for transcript + visual + audio fusion

---

**Duration**: 3.5 days (while traveling and sightseeing)  
**Performance**: ~50-100ms search latency, scales to 100K+ videos  
**Vision**: Making the world's fastest-growing content format searchable and accessible to AI systems
