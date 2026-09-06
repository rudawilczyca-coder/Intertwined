#!/usr/bin/env python3
"""Build and search a local SQLite/FTS5 index of Claude project exports.

The database is a derived evidence index. It is not canon and must not be
committed. Only visible human/assistant text blocks are indexed; hidden
thinking and tool traffic are deliberately excluded.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sqlite3
from pathlib import Path


DEFAULT_SOURCE = Path(
    "/home/sable/archives/Intertwined/claude-project-export-2026-08-16/"
    "Claude_project_export_Intertwined _ A Draco & Theo romance_"
    "019c8524-43e4-72ad-b0ad-23454d3b5072"
)
DEFAULT_DB = Path(
    "/home/sable/archives/Intertwined/index/intertwined-transcripts.sqlite3"
)
ROOT_PARENT = "00000000-0000-4000-8000-000000000000"


SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    uuid TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    summary TEXT,
    model TEXT,
    created_at TEXT,
    updated_at TEXT,
    current_leaf_uuid TEXT,
    source_path TEXT NOT NULL,
    source_filename TEXT NOT NULL
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    uuid TEXT NOT NULL,
    parent_uuid TEXT,
    sequence_index INTEGER,
    sender TEXT NOT NULL,
    created_at TEXT,
    text TEXT NOT NULL,
    on_active_branch INTEGER NOT NULL CHECK (on_active_branch IN (0, 1)),
    UNIQUE(conversation_id, uuid)
);

CREATE INDEX messages_conversation_sequence
    ON messages(conversation_id, sequence_index);
CREATE INDEX messages_active_sender
    ON messages(on_active_branch, sender);

CREATE VIRTUAL TABLE message_fts USING fts5(
    text,
    content='messages',
    content_rowid='id',
    tokenize='unicode61 remove_diacritics 2'
);

CREATE TRIGGER messages_ai AFTER INSERT ON messages BEGIN
  INSERT INTO message_fts(rowid, text) VALUES (new.id, new.text);
END;
CREATE TRIGGER messages_ad AFTER DELETE ON messages BEGIN
  INSERT INTO message_fts(message_fts, rowid, text)
  VALUES('delete', old.id, old.text);
END;
CREATE TRIGGER messages_au AFTER UPDATE ON messages BEGIN
  INSERT INTO message_fts(message_fts, rowid, text)
  VALUES('delete', old.id, old.text);
  INSERT INTO message_fts(rowid, text) VALUES (new.id, new.text);
END;
"""


def visible_text(message: dict) -> str:
    """Return only user-visible prose, excluding thinking and tool payloads."""
    blocks = message.get("content") or []
    parts: list[str] = []
    for block in blocks:
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


def build(source: Path, database: Path) -> None:
    files = sorted(Path(p) for p in glob.glob(str(source / "*.json")))
    if not files:
        raise SystemExit(f"No JSON exports found under {source}")

    database.parent.mkdir(parents=True, exist_ok=True)
    temporary = database.with_suffix(database.suffix + ".new")
    if temporary.exists():
        temporary.unlink()

    conversations = messages_written = active_written = 0
    connection = sqlite3.connect(temporary)
    try:
        connection.executescript(SCHEMA)
        for path in files:
            with path.open(encoding="utf-8") as handle:
                data = json.load(handle)
            uuid = str(data.get("uuid") or path.stem)
            leaf = data.get("current_leaf_message_uuid")
            messages = data.get("chat_messages") or []
            active = active_branch(messages, leaf)
            cursor = connection.execute(
                """INSERT INTO conversations
                   (uuid, title, summary, model, created_at, updated_at,
                    current_leaf_uuid, source_path, source_filename)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    uuid,
                    data.get("name") or path.stem,
                    data.get("summary"),
                    data.get("model"),
                    data.get("created_at"),
                    data.get("updated_at"),
                    leaf,
                    str(path),
                    path.name,
                ),
            )
            conversation_id = cursor.lastrowid
            conversations += 1
            for fallback_index, message in enumerate(messages):
                text = visible_text(message)
                if not text:
                    continue
                message_uuid = str(
                    message.get("uuid") or f"{uuid}:message:{fallback_index}"
                )
                is_active = int(not leaf or message_uuid in active)
                connection.execute(
                    """INSERT INTO messages
                       (conversation_id, uuid, parent_uuid, sequence_index,
                        sender, created_at, text, on_active_branch)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        conversation_id,
                        message_uuid,
                        message.get("parent_message_uuid"),
                        message.get("index", fallback_index),
                        message.get("sender") or "unknown",
                        message.get("created_at"),
                        text,
                        is_active,
                    ),
                )
                messages_written += 1
                active_written += is_active
        connection.execute("PRAGMA user_version=1")
        connection.commit()
        check = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if check != "ok":
            raise RuntimeError(f"SQLite integrity check failed: {check}")
    finally:
        connection.close()

    os.replace(temporary, database)
    print(
        f"Built {database}\n"
        f"Conversations: {conversations}\n"
        f"Visible messages: {messages_written}\n"
        f"Messages on active branches: {active_written}"
    )


def literal_fts_query(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value).strip()
    if not re.search(r"[^\W_]", normalized, flags=re.UNICODE):
        raise SystemExit("Search query contains no searchable words")
    return '"' + normalized.replace('"', '""') + '"'


def search(args: argparse.Namespace) -> None:
    if not args.database.exists():
        raise SystemExit(
            f"Database not found: {args.database}\n"
            "Run the build command first."
        )
    fts_query = args.query if args.fts else literal_fts_query(args.query)
    clauses = ["message_fts MATCH ?"]
    parameters: list[object] = [fts_query]
    if not args.all_branches:
        clauses.append("m.on_active_branch = 1")
    if args.title:
        clauses.append("c.title LIKE ?")
        parameters.append(f"%{args.title}%")
    if args.sender:
        clauses.append("m.sender = ?")
        parameters.append(args.sender)
    parameters.append(args.limit)

    sql = f"""
        SELECT m.id, m.conversation_id, c.title, c.source_filename,
               m.sequence_index, m.sender, m.created_at,
               snippet(message_fts, 0, '[', ']', ' … ', 28) AS excerpt,
               m.text
          FROM message_fts
          JOIN messages m ON m.id = message_fts.rowid
          JOIN conversations c ON c.id = m.conversation_id
         WHERE {' AND '.join(clauses)}
         ORDER BY bm25(message_fts), c.created_at, m.sequence_index
         LIMIT ?
    """
    connection = sqlite3.connect(args.database)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(sql, parameters).fetchall()
        if not rows:
            print("No matches.")
            return
        for number, row in enumerate(rows, 1):
            print(f"\n[{number}] {row['title']}")
            print(
                f"    {row['sender']} · message {row['sequence_index']}"
                + (f" · {row['created_at']}" if row["created_at"] else "")
            )
            print(f"    Source: {row['source_filename']}")
            if args.context:
                surrounding = connection.execute(
                    """SELECT sequence_index, sender, text
                         FROM messages
                        WHERE conversation_id = ?
                          AND sequence_index BETWEEN ? AND ?
                          AND (? OR on_active_branch = 1)
                        ORDER BY sequence_index""",
                    (
                        row["conversation_id"],
                        row["sequence_index"] - args.context,
                        row["sequence_index"] + args.context,
                        int(args.all_branches),
                    ),
                ).fetchall()
                for item in surrounding:
                    marker = ">" if item["sequence_index"] == row["sequence_index"] else " "
                    compact = re.sub(r"\s+", " ", item["text"]).strip()
                    print(
                        f"  {marker} {item['sequence_index']:>4} "
                        f"{item['sender']}: {compact[:500]}"
                    )
            else:
                print("    " + re.sub(r"\s+", " ", row["excerpt"]).strip())
    finally:
        connection.close()


def stats(database: Path) -> None:
    connection = sqlite3.connect(database)
    try:
        conversations = connection.execute(
            "SELECT count(*) FROM conversations"
        ).fetchone()[0]
        messages = connection.execute("SELECT count(*) FROM messages").fetchone()[0]
        active = connection.execute(
            "SELECT count(*) FROM messages WHERE on_active_branch=1"
        ).fetchone()[0]
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        print(
            f"Database: {database}\nConversations: {conversations}\n"
            f"Visible messages: {messages}\nActive-branch messages: {active}\n"
            f"Integrity: {integrity}"
        )
    finally:
        connection.close()


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    build_parser = commands.add_parser("build", help="rebuild the derived index")
    build_parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    build_parser.add_argument("--database", type=Path, default=DEFAULT_DB)

    search_parser = commands.add_parser("search", help="search visible transcript text")
    search_parser.add_argument("query")
    search_parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    search_parser.add_argument("--title", help="case-insensitive title substring")
    search_parser.add_argument("--sender", choices=["human", "assistant"])
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--context", type=int, default=0)
    search_parser.add_argument(
        "--all-branches", action="store_true", help="include superseded branches"
    )
    search_parser.add_argument(
        "--fts", action="store_true", help="interpret query as raw FTS5 syntax"
    )

    stats_parser = commands.add_parser("stats", help="show database counts and integrity")
    stats_parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    return root


def main() -> None:
    args = parser().parse_args()
    if args.command == "build":
        build(args.source, args.database)
    elif args.command == "search":
        search(args)
    elif args.command == "stats":
        stats(args.database)


if __name__ == "__main__":
    main()
