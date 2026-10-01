#!/usr/bin/env python3
"""Build and test the Intertwined Book Four transcript-retrieval pilot.

The raw Claude export remains the lossless source. This script creates a
normalized JSONL archive, a readable selected-path transcript, child retrieval
chunks, and a rebuildable SQLite FTS/vector index. Default retrieval excludes
hidden branches, alternate attempts, OOC/setup traffic, and inline rewrites.
"""

from __future__ import annotations

import argparse
import array
import hashlib
import json
import math
import os
import re
import sqlite3
import struct
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PILOT = REPO / "rag-pilot" / "book4"
MANIFEST_PATH = PILOT / "manifest.json"
BENCHMARK_PATH = PILOT / "benchmark.json"
ARCHIVE_DIR = PILOT / "archive"
DERIVED_DIR = PILOT / "derived"
DEFAULT_DB = Path(
    "/home/sable/archives/Intertwined/index/book4-rag-pilot.sqlite3"
)
ROOT_PARENT = "00000000-0000-4000-8000-000000000000"
EMBED_MODEL = "qwen/qwen3-embedding-8b"
EMBED_URL = "https://openrouter.ai/api/v1/embeddings"
MAX_CHARS = 2200
MIN_CHARS = 650


SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    chunk_id TEXT NOT NULL UNIQUE,
    chunk_sha256 TEXT NOT NULL,
    book_id TEXT NOT NULL,
    scene_id TEXT NOT NULL,
    story_date TEXT,
    authority TEXT NOT NULL,
    default_search INTEGER NOT NULL,
    conversation_uuid TEXT,
    conversation_title TEXT,
    message_uuid TEXT,
    sequence_index INTEGER,
    sender TEXT,
    author TEXT,
    part INTEGER NOT NULL,
    text TEXT NOT NULL,
    embed_text TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    previous_chunk_id TEXT,
    next_chunk_id TEXT,
    embedding BLOB,
    embed_model TEXT
);
CREATE INDEX IF NOT EXISTS chunks_default ON chunks(default_search, authority);
CREATE INDEX IF NOT EXISTS chunks_scene ON chunks(scene_id, sequence_index, part);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    text, conversation_title, scene_id, author,
    content='chunks', content_rowid='id',
    tokenize='unicode61 remove_diacritics 2'
);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def read_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".new")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temporary, path)


def visible_text(message: dict) -> str:
    parts = []
    for block in message.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            value = block.get("text")
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())
    if parts:
        return "\n\n".join(parts)
    value = message.get("text")
    return value.strip() if isinstance(value, str) else ""


def active_branch(messages: list[dict], leaf_uuid: str | None) -> set[str]:
    by_uuid = {m.get("uuid"): m for m in messages if m.get("uuid")}
    active: set[str] = set()
    cursor = leaf_uuid
    while cursor and cursor != ROOT_PARENT and cursor not in active:
        message = by_uuid.get(cursor)
        if not message:
            break
        active.add(cursor)
        cursor = message.get("parent_message_uuid")
    return active


def in_ranges(index: int, ranges: list[list[int]]) -> bool:
    return any(start <= index <= end for start, end in ranges)


def classify_content(text: str, sender: str) -> str:
    stripped = text.lstrip()
    low = stripped.lower()
    if re.match(r"^\[\[?\s*ooc\s*:", stripped, flags=re.I):
        return "ooc"
    if sender == "human" and (
        low.startswith("roleplay setup")
        or low.startswith("read the attached instructions")
        or low.startswith("## current scene")
        or low.startswith("france arc roleplay session")
    ):
        return "setup"
    if sender == "assistant" and re.match(
        r"^(i (?:need to|will|have now)|now let me|files read|done[!,.:]|here(?:'s| is) (?:a )?summary)",
        low,
    ):
        return "meta_or_summary"
    if sender == "human" and re.match(
        r"^(create|summarize|boil it down|could you|can you|help me|okay\.?$)",
        low,
    ):
        return "instruction"
    return "story"


def extract_story_text(text: str, sender: str) -> str:
    """Remove visible setup chatter while leaving the archived text untouched."""
    value = text.strip()
    if not value:
        return ""
    # A number of accepted assistant turns begin with an OOC/file-read note and
    # then a Markdown divider. The prose after the divider is the story turn.
    if sender == "assistant" and classify_content(value, sender) in {
        "ooc",
        "meta_or_summary",
    }:
        pieces = re.split(r"(?m)^---\s*$", value, maxsplit=1)
        if len(pieces) == 2 and len(pieces[1].strip()) >= 120:
            value = pieces[1].strip()
        else:
            return ""
    # Preserve a user's authored prose but remove a trailing archive command.
    if sender == "human" and not re.match(r"^\[\[?\s*ooc\s*:", value, re.I):
        value = re.split(r"\n\s*\[\[?\s*OOC\s*:", value, maxsplit=1, flags=re.I)[0].strip()
    if classify_content(value, sender) in {"ooc", "setup", "instruction"}:
        return ""
    return value


def correction_supersessions(messages: list[dict], selected: set[str], ranges) -> set[int]:
    """Find explicit inline rewrite requests on the selected path.

    This is conservative. It only retires the immediately previous assistant
    turn when a standalone OOC message explicitly asks for a rewrite or names a
    factual inconsistency. Manifest entries handle narratively chosen alternate
    endings which are not phrased as corrections.
    """
    ordered = [
        m for m in sorted(messages, key=lambda x: x.get("index", 0))
        if m.get("uuid") in selected
    ]
    retired: set[int] = set()
    for pos, message in enumerate(ordered):
        idx = int(message.get("index", pos))
        text = visible_text(message)
        if message.get("sender") != "human" or not in_ranges(idx, ranges):
            continue
        if not re.match(r"^\[\[?\s*ooc\s*:", text.lstrip(), re.I):
            continue
        low = text.lower()
        if not re.search(
            r"\brewrite\b|\binconsisten(?:cy|t)\b|\bwrong\b|\bmy correction\b|"
            r"\bdoing it again\b|\bthat was my error\b",
            low,
        ):
            continue
        for prior in reversed(ordered[:pos]):
            pidx = int(prior.get("index", 0))
            if prior.get("sender") == "assistant" and in_ranges(pidx, ranges):
                retired.add(pidx)
                break
    return retired


def clean_attachment(value):
    """Keep attachment metadata without copying binary payloads into JSONL."""
    if not isinstance(value, dict):
        return value
    keep = {}
    for key in (
        "id",
        "uuid",
        "file_name",
        "filename",
        "mime_type",
        "file_type",
        "size",
        "url",
    ):
        if key in value:
            keep[key] = value[key]
    return keep or {"present": True, "keys": sorted(value)}


def split_large_paragraph(paragraph: str) -> list[str]:
    if len(paragraph) <= MAX_CHARS:
        return [paragraph]
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z\"“‘*])", paragraph)
    pieces, current = [], ""
    for sentence in sentences:
        candidate = (current + " " + sentence).strip() if current else sentence
        if len(candidate) > MAX_CHARS and current:
            pieces.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        pieces.append(current)
    # Last-resort hard split for very long unpunctuated blocks.
    output = []
    for piece in pieces:
        if len(piece) <= MAX_CHARS:
            output.append(piece)
        else:
            output.extend(piece[i : i + MAX_CHARS] for i in range(0, len(piece), MAX_CHARS))
    return output


def chunk_text(text: str) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    atoms = []
    for paragraph in paragraphs:
        atoms.extend(split_large_paragraph(paragraph))
    pieces, current = [], ""
    for atom in atoms:
        candidate = (current + "\n\n" + atom).strip() if current else atom
        if len(candidate) > MAX_CHARS and current:
            pieces.append(current)
            current = atom
        else:
            current = candidate
    if current:
        if pieces and len(current) < MIN_CHARS:
            pieces[-1] = pieces[-1] + "\n\n" + current
        else:
            pieces.append(current)
    return pieces or ([text.strip()] if text.strip() else [])


def stable_id(prefix: str, *parts) -> str:
    payload = "|".join(str(part) for part in parts)
    return prefix + "-" + hashlib.sha1(payload.encode()).hexdigest()[:18]


def summary_chunks(manifest: dict) -> list[dict]:
    path = REPO / manifest["book"]["canon_summary"]
    text = path.read_text(encoding="utf-8")
    sections = []
    current_heading = manifest["book"]["title"]
    current_lines: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^#{2,4}\s+(.*)$", line)
        if match and current_lines:
            sections.append((current_heading, "\n".join(current_lines).strip()))
            current_lines = []
        if match:
            current_heading = match.group(1).strip()
        current_lines.append(line)
    if current_lines:
        sections.append((current_heading, "\n".join(current_lines).strip()))

    chunks = []
    for section_number, (heading, body) in enumerate(sections):
        for part, piece in enumerate(chunk_text(body)):
            locator = f"{path.relative_to(REPO)}#section-{section_number}-part-{part}"
            chunk_id = stable_id("b04c", "canon-summary", section_number, part, piece)
            embed_text = (
                f"Intertwined Book Four canon summary\nSection: {heading}\n"
                f"Authority: current event bible\n\n{piece}"
            )
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "chunk_sha256": hashlib.sha256(piece.encode()).hexdigest(),
                    "book_id": manifest["book"]["id"],
                    "scene_id": "b04-canon-summary",
                    "story_date": manifest["book"]["story_date_start"]
                    + "/"
                    + manifest["book"]["story_date_end"],
                    "authority": "canon_summary",
                    "default_search": True,
                    "conversation_uuid": None,
                    "conversation_title": heading,
                    "message_uuid": None,
                    "sequence_index": None,
                    "sender": "reference",
                    "author": "Alice + Sable canon record",
                    "part": part,
                    "text": piece,
                    "embed_text": embed_text,
                    "source_locator": locator,
                }
            )
    return chunks


def build_archive(manifest: dict, source: Path) -> tuple[list[dict], list[dict], dict]:
    files = {}
    for path in source.glob("*.json"):
        try:
            data = read_json(path)
        except Exception:
            continue
        if data.get("uuid"):
            files[data["uuid"]] = (path, data)

    records: list[dict] = []
    chunks: list[dict] = []
    readable: list[str] = [
        "# Intertwined — Book Four: Post-Florence & the Summer",
        "",
        "> Readable projection of the selected story path. The JSONL archive preserves",
        "> hidden branches, alternates, OOC/setup messages, and source relationships.",
        "",
    ]
    report = {
        "conversations": 0,
        "messages": 0,
        "selected_story_messages": 0,
        "hidden_variants": 0,
        "inline_superseded": 0,
        "alternate_messages": 0,
        "attachments": 0,
        "automatic_supersessions": [],
    }

    for spec in manifest["conversations"]:
        if spec["uuid"] not in files:
            raise SystemExit(f"Missing source conversation {spec['uuid']}")
        source_path, data = files[spec["uuid"]]
        messages = data.get("chat_messages") or []
        selected = active_branch(messages, data.get("current_leaf_message_uuid"))
        automatic = correction_supersessions(messages, selected, spec["story_ranges"])
        explicit = set(spec.get("superseded_sequence_indices", []))
        superseded = automatic | explicit
        report["automatic_supersessions"].append(
            {
                "conversation_uuid": spec["uuid"],
                "title": data.get("name"),
                "sequence_indices": sorted(automatic),
            }
        )
        report["conversations"] += 1

        readable.append(f"## {spec['scene_id']} — {data.get('name')}")
        readable.append("")
        readable.append(
            f"Story date: `{spec['story_date']}` · Source: `{spec['uuid']}` · "
            f"Authority: `{spec['authority']}`"
        )
        readable.append("")

        by_index = sorted(messages, key=lambda m: m.get("index", 0))
        message_chunks: list[dict] = []
        for fallback_index, message in enumerate(by_index):
            text = visible_text(message)
            if not text:
                continue
            index = int(message.get("index", fallback_index))
            uuid = str(message.get("uuid") or f"{spec['uuid']}:{index}")
            on_selected = uuid in selected
            within_story = in_ranges(index, spec["story_ranges"])
            kind = classify_content(text, message.get("sender") or "unknown")
            is_alternate = spec["authority"] == "alternate_attempt"
            if not on_selected:
                status = "hidden_variant"
            elif index in superseded:
                status = "superseded_inline"
            elif is_alternate:
                status = "alternate_attempt"
            elif within_story:
                status = "selected_story_context"
            else:
                status = "outside_book_story_range"

            story_text = ""
            if within_story:
                story_text = extract_story_text(text, message.get("sender") or "unknown")
            default_search = bool(
                on_selected
                and within_story
                and not is_alternate
                and index not in superseded
                and story_text
            )
            if default_search:
                status = "selected_story"

            attachments = [clean_attachment(v) for v in message.get("attachments") or []]
            files_meta = [clean_attachment(v) for v in message.get("files") or []]
            record = {
                "schema_version": 1,
                "record_id": stable_id("b04m", spec["uuid"], uuid),
                "book_id": manifest["book"]["id"],
                "scene_id": spec["scene_id"],
                "story_date": spec["story_date"],
                "conversation_uuid": spec["uuid"],
                "conversation_title": data.get("name") or source_path.stem,
                "conversation_model": data.get("model"),
                "conversation_current_leaf_uuid": data.get("current_leaf_message_uuid"),
                "source_export_id": manifest["source_archive"]["export_id"],
                "source_filename": source_path.name,
                "message_uuid": uuid,
                "parent_message_uuid": message.get("parent_message_uuid"),
                "sequence_index": index,
                "sender": message.get("sender") or "unknown",
                "author": "Alice" if message.get("sender") == "human" else "Sable",
                "created_at": message.get("created_at"),
                "updated_at": message.get("updated_at"),
                "on_selected_path": on_selected,
                "in_book_story_range": within_story,
                "authority": spec["authority"],
                "canonical_status": status,
                "content_kind": kind,
                "default_search": default_search,
                "text": text,
                "story_text": story_text,
                "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                "truncated": bool(message.get("truncated")),
                "attachments": attachments,
                "files": files_meta,
            }
            records.append(record)
            report["messages"] += 1
            report["attachments"] += len(attachments) + len(files_meta)
            if status == "selected_story":
                report["selected_story_messages"] += 1
            elif status == "hidden_variant":
                report["hidden_variants"] += 1
            elif status == "superseded_inline":
                report["inline_superseded"] += 1
            elif status == "alternate_attempt":
                report["alternate_messages"] += 1

            should_chunk = bool(story_text) and within_story and status in {
                "selected_story",
                "hidden_variant",
                "superseded_inline",
                "alternate_attempt",
            }
            if should_chunk:
                for part, piece in enumerate(chunk_text(story_text)):
                    locator = (
                        f"claude:{spec['uuid']}/message:{uuid}"
                        f"?index={index}&part={part}"
                    )
                    chunk_id = stable_id("b04t", spec["uuid"], uuid, part, piece)
                    authority = status if status != "selected_story" else spec["authority"]
                    embed_text = (
                        f"Intertwined Book Four\nScene: {spec['scene_id']}\n"
                        f"Story date: {spec['story_date']}\nConversation: {data.get('name')}\n"
                        f"Author: {record['author']}\nAuthority: {authority}\n\n{piece}"
                    )
                    message_chunks.append(
                        {
                            "chunk_id": chunk_id,
                            "chunk_sha256": hashlib.sha256(piece.encode()).hexdigest(),
                            "book_id": manifest["book"]["id"],
                            "scene_id": spec["scene_id"],
                            "story_date": spec["story_date"],
                            "authority": authority,
                            "default_search": default_search,
                            "conversation_uuid": spec["uuid"],
                            "conversation_title": data.get("name") or source_path.stem,
                            "message_uuid": uuid,
                            "sequence_index": index,
                            "sender": record["sender"],
                            "author": record["author"],
                            "part": part,
                            "text": piece,
                            "embed_text": embed_text,
                            "source_locator": locator,
                        }
                    )

            if default_search:
                readable.append(
                    f"### {record['author']} · message {index} · `{uuid}`"
                )
                readable.append("")
                readable.append(story_text)
                readable.append("")

        for position, chunk in enumerate(message_chunks):
            chunk["previous_chunk_id"] = (
                message_chunks[position - 1]["chunk_id"] if position else None
            )
            chunk["next_chunk_id"] = (
                message_chunks[position + 1]["chunk_id"]
                if position + 1 < len(message_chunks)
                else None
            )
        chunks.extend(message_chunks)

    chunks.extend(summary_chunks(manifest))
    write_jsonl(ARCHIVE_DIR / "messages.jsonl", records)
    write_jsonl(DERIVED_DIR / "chunks.jsonl", chunks)
    (ARCHIVE_DIR / "selected-path.md").write_text(
        "\n".join(readable).rstrip() + "\n", encoding="utf-8"
    )
    (ARCHIVE_DIR / "build-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return records, chunks, report


def resolve_embedding_key():
    for name in ("EMBEDDING_API_KEY", "OPENROUTER_API_KEY"):
        value = os.environ.get(name)
        if value:
            return value, f"env:{name}"
    path = Path.home() / ".openclaw" / "credentials" / "openrouter-api-key"
    try:
        value = path.read_text(encoding="utf-8").strip()
        if value:
            return value, "credential-file:openrouter-api-key"
    except OSError:
        pass
    return None, "no OpenRouter embedding credential"


def embed_texts(texts: list[str], key: str) -> list[list[float]]:
    payload = json.dumps({"model": EMBED_MODEL, "input": texts}).encode()
    request = urllib.request.Request(
        EMBED_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.loads(response.read())
    return [item["embedding"] for item in sorted(data["data"], key=lambda x: x["index"])]


def pack_vector(vector: list[float]) -> bytes:
    return struct.pack(f"<{len(vector)}f", *vector)


def unpack_vector(blob: bytes) -> array.array:
    values = array.array("f")
    values.frombytes(blob)
    if sys.byteorder != "little":
        values.byteswap()
    return values


def build_index(chunks: list[dict], database: Path, embed: bool, batch_size: int) -> dict:
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    existing = {
        row["chunk_id"]: (row["chunk_sha256"], row["embedding"], row["embed_model"])
        for row in connection.execute(
            "SELECT chunk_id,chunk_sha256,embedding,embed_model FROM chunks"
        )
    }
    connection.execute("DELETE FROM chunks")
    connection.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('delete-all')")
    reused = 0
    for chunk in chunks:
        old_sha, old_embedding, old_model = existing.get(chunk["chunk_id"], (None, None, None))
        reuse = old_sha == chunk["chunk_sha256"] and old_model == EMBED_MODEL
        cursor = connection.execute(
            """INSERT INTO chunks
            (chunk_id,chunk_sha256,book_id,scene_id,story_date,authority,
             default_search,conversation_uuid,conversation_title,message_uuid,
             sequence_index,sender,author,part,text,embed_text,source_locator,
             previous_chunk_id,next_chunk_id,embedding,embed_model)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                chunk["chunk_id"],
                chunk["chunk_sha256"],
                chunk["book_id"],
                chunk["scene_id"],
                chunk.get("story_date"),
                chunk["authority"],
                int(chunk["default_search"]),
                chunk.get("conversation_uuid"),
                chunk.get("conversation_title"),
                chunk.get("message_uuid"),
                chunk.get("sequence_index"),
                chunk.get("sender"),
                chunk.get("author"),
                chunk["part"],
                chunk["text"],
                chunk["embed_text"],
                chunk["source_locator"],
                chunk.get("previous_chunk_id"),
                chunk.get("next_chunk_id"),
                old_embedding if reuse else None,
                old_model if reuse else None,
            ),
        )
        connection.execute(
            "INSERT INTO chunks_fts(rowid,text,conversation_title,scene_id,author) VALUES (?,?,?,?,?)",
            (
                cursor.lastrowid,
                chunk["text"],
                chunk.get("conversation_title") or "",
                chunk["scene_id"],
                chunk.get("author") or "",
            ),
        )
        reused += int(reuse and old_embedding is not None)
    connection.commit()

    embedded = 0
    status = "skipped"
    if embed:
        key, key_source = resolve_embedding_key()
        if not key:
            status = f"blocked: {key_source}"
        else:
            rows = connection.execute(
                "SELECT id,embed_text FROM chunks WHERE embedding IS NULL ORDER BY id"
            ).fetchall()
            try:
                for start in range(0, len(rows), batch_size):
                    batch = rows[start : start + batch_size]
                    vectors = embed_texts([row["embed_text"] for row in batch], key)
                    for row, vector in zip(batch, vectors):
                        connection.execute(
                            "UPDATE chunks SET embedding=?,embed_model=? WHERE id=?",
                            (pack_vector(vector), EMBED_MODEL, row["id"]),
                        )
                    connection.commit()
                    embedded += len(batch)
                    print(f"Embedded {embedded}/{len(rows)} chunks")
                status = f"ok: {reused} reused, {embedded} embedded via {EMBED_MODEL}"
            except Exception as error:
                connection.commit()
                status = f"error after {embedded}: {error}"
    connection.execute(
        "INSERT OR REPLACE INTO meta(key,value) VALUES('embedding_status',?)", (status,)
    )
    connection.execute(
        "INSERT OR REPLACE INTO meta(key,value) VALUES('chunk_count',?)",
        (str(len(chunks)),),
    )
    connection.commit()
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    vectors = connection.execute(
        "SELECT count(*) FROM chunks WHERE embedding IS NOT NULL"
    ).fetchone()[0]
    connection.close()
    return {
        "database": str(database),
        "chunks": len(chunks),
        "vectors": vectors,
        "embedding_status": status,
        "integrity": integrity,
    }


def keyword_query(query: str) -> str | None:
    words = [
        word.lower()
        for word in re.findall(r"[^\W_][\w'-]*", query, flags=re.UNICODE)
        if len(word) >= 3
    ]
    stop = {
        "the", "and", "was", "were", "what", "when", "where", "which", "who",
        "why", "how", "did", "does", "with", "from", "that", "this", "then",
        "into", "about", "after", "before", "rather", "than", "first",
    }
    words = [word for word in words if word not in stop]
    if not words:
        return None
    return " OR ".join('"' + word.replace('"', '""') + '"' for word in dict.fromkeys(words))


def cosine(left: list[float], right: array.array) -> float:
    dot = lnorm = rnorm = 0.0
    for a, b in zip(left, right):
        dot += a * b
        lnorm += a * a
        rnorm += b * b
    if not lnorm or not rnorm:
        return 0.0
    return dot / math.sqrt(lnorm * rnorm)


def retrieve(
    database: Path,
    query: str,
    mode: str = "hybrid",
    limit: int = 5,
    all_variants: bool = False,
) -> tuple[list[dict], dict]:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    allowed = "1=1" if all_variants else "c.default_search=1"
    candidate_limit = max(50, limit * 12)
    keyword_rows = []
    fts = keyword_query(query)
    if fts:
        keyword_rows = connection.execute(
            f"""SELECT c.*, bm25(chunks_fts) AS keyword_score
                  FROM chunks_fts JOIN chunks c ON c.id=chunks_fts.rowid
                 WHERE chunks_fts MATCH ? AND {allowed}
                 ORDER BY keyword_score LIMIT ?""",
            (fts, candidate_limit),
        ).fetchall()

    semantic_rows: list[tuple[sqlite3.Row, float]] = []
    semantic_status = "not requested"
    if mode in {"semantic", "hybrid"}:
        key, key_source = resolve_embedding_key()
        vector_count = connection.execute(
            f"SELECT count(*) FROM chunks c WHERE c.embedding IS NOT NULL AND {allowed}"
        ).fetchone()[0]
        if key and vector_count:
            query_vector = embed_texts([query], key)[0]
            rows = connection.execute(
                f"SELECT c.* FROM chunks c WHERE c.embedding IS NOT NULL AND {allowed}"
            ).fetchall()
            semantic_rows = sorted(
                ((row, cosine(query_vector, unpack_vector(row["embedding"]))) for row in rows),
                key=lambda item: item[1],
                reverse=True,
            )[:candidate_limit]
            semantic_status = f"ok via {key_source}"
        else:
            semantic_status = "unavailable: missing credential or vectors"
            if mode == "semantic":
                connection.close()
                return [], {"semantic_status": semantic_status, "keyword_hits": len(keyword_rows)}

    scores: dict[str, float] = defaultdict(float)
    rows_by_id: dict[str, sqlite3.Row] = {}
    keyword_ids = set()
    semantic_scores = {}
    if mode in {"keyword", "hybrid"}:
        for rank, row in enumerate(keyword_rows, 1):
            scores[row["chunk_id"]] += 1.0 / (60 + rank)
            rows_by_id[row["chunk_id"]] = row
            keyword_ids.add(row["chunk_id"])
    if mode in {"semantic", "hybrid"}:
        for rank, (row, similarity) in enumerate(semantic_rows, 1):
            scores[row["chunk_id"]] += 1.0 / (60 + rank)
            rows_by_id[row["chunk_id"]] = row
            semantic_scores[row["chunk_id"]] = similarity

    # Current canon summaries win close factual ties; transcript evidence still
    # wins exact-dialogue and emotional-context matches through its text score.
    for chunk_id, row in rows_by_id.items():
        if row["authority"] == "canon_summary":
            scores[chunk_id] += 0.0015

    ranked = []
    for chunk_id in sorted(scores, key=scores.get, reverse=True)[:limit]:
        row = rows_by_id[chunk_id]
        item = {key: row[key] for key in row.keys() if key != "embedding"}
        item["retrieval_score"] = scores[chunk_id]
        item["keyword_hit"] = chunk_id in keyword_ids
        item["semantic_similarity"] = semantic_scores.get(chunk_id)
        ranked.append(item)
    connection.close()
    max_similarity = max(semantic_scores.values(), default=None)
    diagnostics = {
        "mode": mode,
        "keyword_hits": len(keyword_rows),
        "semantic_status": semantic_status,
        "max_semantic_similarity": max_similarity,
    }
    return ranked, diagnostics


def display_results(database: Path, rows: list[dict], diagnostics: dict, neighbors: bool) -> None:
    print(json.dumps(diagnostics, ensure_ascii=False, indent=2))
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    for number, row in enumerate(rows, 1):
        print(f"\n[{number}] {row['conversation_title'] or row['scene_id']}")
        print(
            f"    {row['authority']} · {row['story_date']} · "
            f"score {row['retrieval_score']:.5f}"
        )
        if row.get("semantic_similarity") is not None:
            print(f"    cosine {row['semantic_similarity']:.4f}")
        print(f"    Source: {row['source_locator']} · chunk {row['chunk_id']}")
        compact = re.sub(r"\s+", " ", row["text"]).strip()
        print("    " + compact[:900])
        if neighbors and row.get("message_uuid"):
            surrounding = connection.execute(
                """SELECT conversation_title,sequence_index,author,text,source_locator
                     FROM chunks
                    WHERE scene_id=? AND default_search=1
                      AND sequence_index BETWEEN ? AND ?
                    ORDER BY sequence_index,part""",
                # Two messages on either side is enough to recover the answer
                # to the benchmark's Draco-promise question from the correctly
                # retrieved setup turn, while staying on the selected path.
                (row["scene_id"], row["sequence_index"] - 2, row["sequence_index"] + 2),
            ).fetchall()
            for neighbor in surrounding:
                marker = ">" if neighbor["sequence_index"] == row["sequence_index"] else " "
                excerpt = re.sub(r"\s+", " ", neighbor["text"]).strip()[:350]
                print(
                    f"  {marker} msg {neighbor['sequence_index']} {neighbor['author']}: {excerpt}"
                )
    connection.close()


def run_benchmark(database: Path, mode: str, output: Path | None = None) -> dict:
    suite = read_json(BENCHMARK_PATH)
    results = []
    for case in suite["questions"]:
        rows, diagnostics = retrieve(database, case["question"], mode=mode, limit=5)
        locators = [row["source_locator"] for row in rows]
        if not case.get("answerable", True):
            # A negative control passes only when the retrieved evidence does
            # not contain the identity terms required to support the premise.
            # Related Luminary passages may still be returned; they do not make
            # an invented person or password answerable.
            required = [term.casefold() for term in case.get("required_terms", [])]
            passed = not any(
                all(term in row["text"].casefold() for term in required) for row in rows
            )
        else:
            expected = case.get("expected", [])
            passed = any(
                locator_matches(locator, target) for locator in locators for target in expected
            )
            for forbidden in case.get("forbidden", []):
                if any(locator_matches(locator, forbidden) for locator in locators):
                    passed = False
        results.append(
            {
                "id": case["id"],
                "question": case["question"],
                "passed": passed,
                "top_sources": locators,
                "diagnostics": diagnostics,
            }
        )
        print(("PASS" if passed else "FAIL") + f" {case['id']}: {case['question']}")
    report = {
        "mode": mode,
        "passed": sum(item["passed"] for item in results),
        "total": len(results),
        "results": results,
    }
    if output:
        output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return report


def locator_matches(locator: str, target: dict) -> bool:
    if target.get("contains") and target["contains"] not in locator:
        return False
    if target.get("conversation_uuid") and target["conversation_uuid"] not in locator:
        return False
    if target.get("message_uuid") and target["message_uuid"] not in locator:
        return False
    if "sequence_index" in target and f"index={target['sequence_index']}" not in locator:
        return False
    return True


def command_build(args) -> None:
    manifest = read_json(MANIFEST_PATH)
    source = Path(args.source or manifest["source_archive"]["default_path"])
    records, chunks, report = build_archive(manifest, source)
    index_report = build_index(chunks, args.database, not args.no_embed, args.batch)
    print(json.dumps({"archive": report, "index": index_report}, ensure_ascii=False, indent=2))


def command_query(args) -> None:
    rows, diagnostics = retrieve(
        args.database,
        args.query,
        mode=args.mode,
        limit=args.limit,
        all_variants=args.all_variants,
    )
    display_results(args.database, rows, diagnostics, args.show_neighbors)


def command_benchmark(args) -> None:
    output = PILOT / f"benchmark-{args.mode}.json"
    report = run_benchmark(args.database, args.mode, output)
    print(f"\n{report['passed']}/{report['total']} passed; details: {output}")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--source")
    build.add_argument("--database", type=Path, default=DEFAULT_DB)
    build.add_argument("--no-embed", action="store_true")
    build.add_argument("--batch", type=int, default=32)
    build.set_defaults(func=command_build)

    query = commands.add_parser("query")
    query.add_argument("query")
    query.add_argument("--database", type=Path, default=DEFAULT_DB)
    # The checked Book Four suite currently shows that naive reciprocal-rank
    # fusion can displace exact canon/event matches. Keep the proven lexical
    # path as the safe default until a reranker is evaluated; semantic and
    # hybrid remain explicit experimental modes.
    query.add_argument("--mode", choices=["keyword", "semantic", "hybrid"], default="keyword")
    query.add_argument("--limit", type=int, default=5)
    query.add_argument("--all-variants", action="store_true")
    query.add_argument("--show-neighbors", action="store_true")
    query.set_defaults(func=command_query)

    benchmark = commands.add_parser("benchmark")
    benchmark.add_argument("--database", type=Path, default=DEFAULT_DB)
    benchmark.add_argument("--mode", choices=["keyword", "semantic", "hybrid"], default="hybrid")
    benchmark.set_defaults(func=command_benchmark)
    return root


def main() -> None:
    args = parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
