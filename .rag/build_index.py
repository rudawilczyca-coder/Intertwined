#!/usr/bin/env python3
"""
build_index.py — build (or refresh) the RAG index for one repo.

Usage:
    python3 build_index.py [--repo /path/to/repo] [--no-embed]

Defaults --repo to the parent of this script's directory (so a copy living in
<repo>/.rag/ indexes <repo>). Writes the DB to <repo>/.rag/index.db.

Stages:
  1. walk + chunk + extract metadata  -> always runs, stored to SQLite
  2. embed each chunk via Qwen3-Embedding-8B on OpenRouter -> only if a real
     OpenRouter credential resolves.
     With --no-embed, or when no key is found, chunks are stored WITHOUT
     embeddings and the script reports exactly why. No fake vectors are ever
     written; semantic search simply stays disabled until embeddings exist.
"""
import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rag_lib as R


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_repo = os.path.dirname(here)
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=default_repo)
    ap.add_argument("--no-embed", action="store_true", help="skip the embedding stage")
    ap.add_argument("--batch", type=int, default=64)
    args = ap.parse_args()

    repo = os.path.abspath(args.repo)
    rag_dir = os.path.join(repo, ".rag")
    os.makedirs(rag_dir, exist_ok=True)
    db_path = os.path.join(rag_dir, "index.db")

    print("Repo:        %s" % repo)
    print("Index DB:    %s" % db_path)

    # ---- Stage 1: walk + chunk + metadata --------------------------------
    files = sorted(R.walk_repo(repo))
    all_chunks = []
    for path in files:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception as e:
            print("  skip (read error) %s: %s" % (path, e))
            continue
        if not text.strip():
            continue
        all_chunks.extend(R.chunk_file(path, text))

    conn = R.connect(db_path)
    # Preserve vectors for byte-identical chunks. The index is rebuilt from
    # current files each run, but unchanged evidence should not incur another
    # embedding call merely because exclusions or unrelated files changed.
    existing = {
        row[0]: (row[1], row[2], row[3])
        for row in conn.execute(
            "SELECT chunk_key,embed_text,embedding,embed_model FROM chunks"
        ).fetchall()
    }
    conn.execute("DELETE FROM chunks")
    conn.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('delete-all')")
    for c in all_chunks:
        key = R.chunk_key(c, repo)
        rel = os.path.relpath(c["path"], repo)
        prior_text, prior_embedding, prior_model = existing.get(key, (None, None, None))
        reuse = prior_text == c["embed_text"] and prior_model == R.EMBED_MODEL
        cur = conn.execute(
            """INSERT INTO chunks
               (chunk_key,path,rel_path,title,heading,part,text,embed_text,
                characters,dates,date_min,date_max,tokens_approx,embedding,embed_model)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (key, c["path"], rel, c["title"], c["heading"], c["part"], c["text"],
             c["embed_text"], json.dumps(c["characters"]), json.dumps(c["dates"]),
             c["date_min"], c["date_max"], c["tokens_approx"],
             prior_embedding if reuse else None, prior_model if reuse else None),
        )
        conn.execute(
            "INSERT INTO chunks_fts(rowid,text,heading,title,characters) VALUES (?,?,?,?,?)",
            (cur.lastrowid, c["text"], c["heading"] or "", c["title"] or "",
             " ".join(c["characters"])),
        )
    conn.commit()

    n_files = len(files)
    n_chunks = len(all_chunks)
    n_dated = sum(1 for c in all_chunks if c["date_min"])
    n_charred = sum(1 for c in all_chunks if c["characters"])
    print("\nStage 1 complete:")
    print("  files indexed:            %d" % n_files)
    print("  chunks created:           %d" % n_chunks)
    print("  chunks with >=1 date:     %d" % n_dated)
    print("  chunks with >=1 character:%d" % n_charred)

    # ---- Stage 2: embeddings ---------------------------------------------
    embedded = 0
    if args.no_embed:
        embed_status = "skipped (--no-embed)"
        print("\nStage 2 skipped (--no-embed). Chunks stored without embeddings.")
    else:
        key, source = R.resolve_embedding_key()
        if not key:
            embed_status = "BLOCKED: %s" % source
            print("\nStage 2 BLOCKED — no OpenRouter credential.")
            print("  %s" % source)
            print("  Chunks are stored with text + metadata only. Provide a key")
            print("  (export OPENROUTER_API_KEY=... or install the permission-restricted")
            print("  openrouter-api-key credential file) and re-run to enable semantic search.")
        else:
            print("\nStage 2: embedding via %s (key source: %s)" % (R.EMBED_MODEL, source))
            rows = conn.execute(
                "SELECT id, embed_text FROM chunks WHERE embedding IS NULL ORDER BY id"
            ).fetchall()
            reused = conn.execute(
                "SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL"
            ).fetchone()[0]
            print("  reused %d unchanged embeddings" % reused)
            try:
                for i in range(0, len(rows), args.batch):
                    batch = rows[i:i + args.batch]
                    vecs = R.embed_texts([r[1] for r in batch], key)
                    for (cid, _), v in zip(batch, vecs):
                        conn.execute(
                            "UPDATE chunks SET embedding=?, embed_model=? WHERE id=?",
                            (R.pack_vec(v), R.EMBED_MODEL, cid),
                        )
                    embedded += len(batch)
                    conn.commit()
                    print("  embedded %d/%d" % (embedded, len(rows)))
                embed_status = "ok (%d reused, %d embedded, %s)" % (
                    reused, embedded, R.EMBED_MODEL)
            except Exception as e:
                embed_status = "ERROR after %d chunks: %s" % (embedded, e)
                print("\nStage 2 ERROR: %s" % e)
                print("  Partial embeddings kept; re-run to continue.")

    conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('repo',?)", (repo,))
    conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('n_files',?)", (str(n_files),))
    conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('n_chunks',?)", (str(n_chunks),))
    conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('embed_status',?)", (embed_status,))
    conn.commit()
    conn.close()
    print("\nDone. embed_status = %s" % embed_status)


if __name__ == "__main__":
    main()
