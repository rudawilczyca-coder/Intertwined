#!/usr/bin/env python3
"""
query.py — retrieve top-N chunks from a repo's RAG index.

Usage:
    python3 query.py "your question" [--repo /path/to/repo]
                      [--character NAME] [--since YYYY-MM-DD] [--until YYYY-MM-DD]
                      [--event "text in heading/title"] [--limit N] [--mode auto|semantic|keyword]

Defaults --repo to the parent of this script's directory. Metadata filters
(--character, --since, --until, --event) always apply. Ranking mode:
  semantic  — cosine similarity vs the query's OpenAI embedding (needs a key
              AND an embedded index).
  keyword   — SQLite FTS5 BM25 over chunk text (no key needed).
  auto      — semantic if embeddings + key are available, else keyword.

Unless --rerank off is supplied, the top first-pass candidates are reranked by
Voyage when its credential is available. API failures preserve first-pass order.

Examples:
    python3 query.py "the proposal in the music room" --character Theodore --limit 5
    python3 query.py "model comparison arena" --since 2026-06-01
"""
import os
import sys
import json
import math
import argparse
import re
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rag_lib as R

VOYAGE_RERANK_MODEL = "rerank-2.5-lite"
VOYAGE_RERANK_URL = "https://api.voyageai.com/v1/rerank"


def resolve_voyage_key():
    key = os.environ.get("VOYAGE_API_KEY")
    if key:
        return key, "env:VOYAGE_API_KEY"
    path = os.path.expanduser("~/.openclaw/credentials/voyage-api-key")
    try:
        with open(path) as f:
            key = f.read().strip()
        if key:
            return key, "file:voyage-api-key"
    except Exception:
        pass
    return None, "no VOYAGE_API_KEY or voyage-api-key credential file"


def voyage_rerank(query, ranked, key):
    """Rerank [(row, first_pass_score)] with Voyage; preserve row objects."""
    payload = json.dumps({
        "model": VOYAGE_RERANK_MODEL,
        "query": query,
        "documents": [row["text"] for row, _ in ranked],
        "top_k": len(ranked),
    }).encode()
    req = urllib.request.Request(
        VOYAGE_RERANK_URL, data=payload,
        headers={"Authorization": "Bearer %s" % key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        data = json.loads(response.read())
    return [(ranked[item["index"]][0], item["relevance_score"]) for item in data["data"]]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def canon_character(name):
    """Map a user-supplied name/alias to a canonical character name."""
    nl = name.strip().lower()
    for canon, aliases in R.CANON_CHARACTERS.items():
        if nl == canon.lower() or any(nl == a.lower() for a in aliases):
            return canon
    # substring fallback
    for canon in R.CANON_CHARACTERS:
        if nl in canon.lower():
            return canon
    return name


def apply_filters(rows, args):
    ch = canon_character(args.character) if args.character else None
    out = []
    for r in rows:
        chars = json.loads(r["characters"] or "[]")
        if ch and ch not in chars:
            continue
        if args.since and (not r["date_max"] or r["date_max"] < args.since):
            continue
        if args.until and (not r["date_min"] or r["date_min"] > args.until):
            continue
        if args.event:
            hay = ((r["heading"] or "") + " " + (r["title"] or "")).lower()
            if args.event.lower() not in hay:
                continue
        out.append(r)
    return out, ch


def best_snippet(text, query, width=280):
    """Return a query-relevant window instead of always showing chunk start."""
    flat = " ".join(text.split())
    if len(flat) <= width:
        return flat

    stop = {
        "after", "before", "did", "does", "for", "from", "had", "has",
        "her", "his", "how", "into", "set", "that", "the", "their",
        "they", "this", "was", "what", "when", "where", "which", "who",
        "why", "with",
    }
    terms = {
        w.lower() for w in re.findall(r"[A-Za-z0-9]+", query)
        if len(w) >= 3 and w.lower() not in stop
    }
    if not terms:
        return flat[:width].rstrip() + "…"

    lower = flat.lower()
    positions = [m.start() for term in terms for m in re.finditer(re.escape(term), lower)]
    if not positions:
        return flat[:width].rstrip() + "…"

    best_start, best_score = 0, -1
    for pos in positions:
        start = max(0, min(pos - width // 3, len(flat) - width))
        window = lower[start:start + width]
        score = sum(1 + min(len(term), 10) / 10 for term in terms if term in window)
        if score > best_score:
            best_start, best_score = start, score

    end = min(len(flat), best_start + width)
    if best_start:
        next_space = flat.find(" ", best_start)
        if 0 <= next_space < end:
            best_start = next_space + 1
    if end < len(flat):
        last_space = flat.rfind(" ", best_start, end)
        if last_space > best_start:
            end = last_space
    return ("…" if best_start else "") + flat[best_start:end].rstrip() + ("…" if end < len(flat) else "")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_repo = os.path.dirname(here)
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--repo", default=default_repo)
    ap.add_argument("--character")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--event")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--mode", choices=["auto", "semantic", "keyword"], default="auto")
    ap.add_argument("--rerank", choices=["auto", "on", "off"], default="auto")
    ap.add_argument("--candidate-limit", type=int, default=30)
    args = ap.parse_args()

    db_path = os.path.join(os.path.abspath(args.repo), ".rag", "index.db")
    if not os.path.exists(db_path):
        sys.exit("No index at %s — run build_index.py first." % db_path)
    conn = R.connect(db_path)
    conn.row_factory = __import__("sqlite3").Row

    have_embeddings = conn.execute(
        "SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL").fetchone()[0] > 0
    key, key_source = R.resolve_openai_key()

    mode = args.mode
    if mode == "auto":
        mode = "semantic" if (have_embeddings and key) else "keyword"
    if mode == "semantic" and not (have_embeddings and key):
        why = "no embeddings in index" if not have_embeddings else "no OpenAI key (%s)" % key_source
        print("[semantic unavailable: %s -> falling back to keyword]" % why)
        mode = "keyword"

    # ---- candidate set ----------------------------------------------------
    if mode == "keyword":
        # FTS5 match; fall back to all rows if the query has no usable tokens.
        q = " OR ".join(w for w in __import__("re").findall(r"[A-Za-z0-9]+", args.query))
        rows = []
        if q:
            try:
                rows = conn.execute(
                    "SELECT c.*, bm25(chunks_fts) AS score FROM chunks_fts "
                    "JOIN chunks c ON c.id=chunks_fts.rowid "
                    "WHERE chunks_fts MATCH ? ORDER BY score", (q,)).fetchall()
            except Exception:
                rows = []
        if not rows:
            rows = conn.execute("SELECT *, 0.0 AS score FROM chunks").fetchall()
        filtered, ch = apply_filters(rows, args)
        ranked = [(r, -r["score"]) for r in filtered]  # lower bm25 = better
        ranked.sort(key=lambda x: x[1], reverse=True)
        results = ranked[:args.limit]
        score_label = "bm25(rel)"
    else:
        qvec = R.embed_texts([args.query], key)[0]
        rows = conn.execute("SELECT * FROM chunks WHERE embedding IS NOT NULL").fetchall()
        filtered, ch = apply_filters(rows, args)
        scored = [(r, cosine(qvec, R.unpack_vec(r["embedding"]))) for r in filtered]
        scored.sort(key=lambda x: x[1], reverse=True)
        ranked = scored
        results = ranked[:args.limit]
        score_label = "cosine"

    # Voyage is a second-stage relevance judge over a bounded candidate pool.
    # It never changes the stored vectors; failures fall back to first-pass order.
    voyage_key, voyage_source = resolve_voyage_key()
    use_rerank = args.rerank == "on" or (args.rerank == "auto" and voyage_key)
    if use_rerank and ranked:
        try:
            candidates = ranked[:max(args.limit, args.candidate_limit)]
            results = voyage_rerank(args.query, candidates, voyage_key)[:args.limit]
            score_label = "voyage-rerank"
            mode += "+rerank"
        except Exception as exc:
            print("[Voyage rerank unavailable: %s -> using first-pass order]" % exc, file=sys.stderr)
            results = ranked[:args.limit]
    elif args.rerank == "on" and not voyage_key:
        print("[Voyage rerank unavailable: %s -> using first-pass order]" % voyage_source, file=sys.stderr)

    # ---- output -----------------------------------------------------------
    print("query:   %r" % args.query)
    print("repo:    %s" % os.path.abspath(args.repo))
    print("mode:    %s   score: %s" % (mode, score_label))
    if args.character:
        print("filter:  character=%s" % (ch or args.character))
    if args.since or args.until:
        print("filter:  date %s .. %s" % (args.since or "-inf", args.until or "+inf"))
    if args.event:
        print("filter:  event~%r" % args.event)
    print("matches: %d (showing %d)" % (len(filtered), len(results)))
    print("=" * 72)
    if not results:
        print("(no chunks matched the filters)")
    for r, score in results:
        chars = json.loads(r["characters"] or "[]")
        dates = json.loads(r["dates"] or "[]")
        print("\n[%.4f] %s" % (score, r["rel_path"]))
        print("  heading:    %s" % (r["heading"] or "(none)"))
        if r["title"] and r["title"] != r["heading"]:
            print("  file title: %s" % r["title"])
        if dates:
            print("  dates:      %s" % ", ".join(dates[:6]) + (" …" if len(dates) > 6 else ""))
        if chars:
            print("  characters: %s" % ", ".join(chars))
        snippet = best_snippet(r["text"], args.query)
        print("  text:       %s" % snippet)
    conn.close()


if __name__ == "__main__":
    main()
