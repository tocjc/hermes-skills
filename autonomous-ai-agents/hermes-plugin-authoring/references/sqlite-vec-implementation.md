# sqlite-vec Memory Provider — Implementation Notes

Created during session 2026-07-14. Local vector memory plugin using sqlite-vec + sentence-transformers.

## Architecture

```
Hermes session
  → MemoryManager.prefetch(query)   # before each turn
  → SqliteVecMemoryProvider.prefetch(query)
    → _embed(query) → vec0 MATCH → cosine similarity → top-K results
  → MemoryManager.sync_turn(user, assistant)
  → SqliteVecMemoryProvider.sync_turn()
    → extract significant content → _embed() → INSERT INTO vec_memories
```

## Schema

```sql
-- Memories table (rowid = vec0 primary key)
CREATE TABLE memories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    content     TEXT    NOT NULL,
    category    TEXT    DEFAULT 'general',
    tags        TEXT    DEFAULT '',
    created_at  REAL    NOT NULL DEFAULT (julianday('now')),
    updated_at  REAL    NOT NULL DEFAULT (julianday('now'))
);

-- vec0 virtual table: 384D float32, cosine distance
CREATE VIRTUAL TABLE vec_memories USING vec0(
    id INTEGER PRIMARY KEY,
    embedding float[384] distance_metric=cosine
);
```

## Key Decisions

### Embedding: sentence-transformers all-MiniLM-L6-v2
- 384D vectors, normalized embeddings for cosine similarity
- ~80MB model, cached on first use (`~/.cache/huggingface/`)
- Device forced to CPU (guaranteed availability)
- Set `SQLITE_VEC_EMBED_MODEL` env var to override

### Similarity: 1 - cosine_distance
sqlite-vec's `vec0` returns distance (0 = identical, 1 = orthogonal, 2 = opposite). Convert to similarity score: `score = 1.0 - distance`.

### Prefetch Filtering
- Results below `min_score` threshold are filtered out
- Extra results fetched (limit × 3) to account for filtering
- Default: top_k=5, min_score=0.3

### Auto-Sync Logic
- Only stores assistant responses (not user queries)
- Skips code blocks, tool output, and short messages (< 30 chars)
- Category: `insight`, tags: `session:<session_id>`
- Truncates to 200 chars max

## Dependencies

```bash
pip install sqlite-vec sentence-transformers
```

## Tool Schema

The `memory_vec` tool exposes 6 actions:

| Action | Params | Returns |
|--------|--------|---------|
| add | content, category?, tags? | `{memory_id: int}` |
| search | query, limit?, min_score? | `{results: [{id, content, score, ...}]}` |
| recent | limit? | `{results: [...]}` |
| update | memory_id, content | `{success: bool}` |
| remove | memory_id | `{success: bool}` |
| stats | — | `{total_memories, by_category, embedding_dim, model}` |

## Verified Constraints

- sqlite-vec version: v0.1.9
- Available vec0 modules: `vec0`, `vec_each`
- Loading: `sqlite_vec.load(conn)` after `conn.enable_load_extension(True)`
- WAL mode + synchronous=NORMAL for performance
- Tested with Chinese text embeddings — semantic search works correctly across languages