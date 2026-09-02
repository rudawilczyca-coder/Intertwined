"""
rag_lib.py — shared helpers for the Intertwined / sable-antiquary RAG index.

Provider-agnostic pipeline: walk markdown -> chunk by heading -> extract
metadata -> store text+metadata+embedding in SQLite.

Embeddings use Qwen3-Embedding-8B through OpenRouter's compatible endpoint.
The key is resolved ONLY from a real credential path (see resolve_embedding_key).
We never fabricate a placeholder.

No third-party deps required (stdlib sqlite3 + urllib). If numpy is present
it is used to speed up cosine similarity, otherwise a pure-python path runs.
"""
import os
import re
import json
import sqlite3
import hashlib
import urllib.request
import urllib.error

EMBED_MODEL = "qwen/qwen3-embedding-8b"
EMBED_DIM = 4096  # qwen3-embedding-8b native dimension, verified live

# Directories we never index. ``archives`` holds superseded versions of files
# that exist current elsewhere; indexing them surfaces outdated canon.
SKIP_DIRS = {".git", ".obsidian", ".claude", ".rag", ".trash", "node_modules", "archives"}

# Repo-relative trees which are useful to humans but are not canon evidence.
# Keep this narrower than SKIP_DIRS: ``archive`` may still contain unique
# played material, while its superseded-planning shelf must never compete with
# current canon. Workflow documents describe process rather than story truth.
SKIP_REL_DIRS = {
    "archive/superseded-planning",
    "workflows",
}

# Portrayal bibles are stable prompt authority, not retrieval evidence. Returning
# their interpretive prose during scene generation turns RAG into a second,
# stochastic character card. Permanent principal facts now live in the card too;
# event chronology and changing scene state remain searchable elsewhere.
SKIP_REL_FILES = {
    "characters/draco_malfoy_character_updated4.md",
    "characters/theodore_nott_character_updated3.md",
    "nest/intertwined_portrayal_curated.md",
}
EXTS = (".md", ".txt")

# --- roughly token-sized bounds (approx 4 chars/token) -----------------------
MIN_TOKENS = 200
MAX_TOKENS = 800
CHARS_PER_TOKEN = 4


# ---------------------------------------------------------------------------
# Character names (for cross-referencing chunks against Intertwined canon).
# Curated principals + roster, with alias sets. Whole-word matched in text.
# ---------------------------------------------------------------------------
CANON_CHARACTERS = {
    "Theodore Nott": ["Theodore Nott", "Theo Nott", "Theo"],
    "Draco Malfoy": ["Draco Malfoy", "Draco"],
    "Jackie Nott-Malfoy": ["Jackie Nott-Malfoy", "Jackie Nott", "Jackie"],
    # Ruby Williams arc (2002 London/Wales). NOTE: "Ruby" is also Alice's OOC
    # nickname; in canon-file prose it near-always means the character.
    "Ruby Williams": ["Ruby Williams", "Ruby"],
    "Robbie": ["Robbie"],
    "Gemma Williams": ["Gemma Williams", "Gemma"],
    "Gareth Williams": ["Gareth Williams", "Gareth"],
    "Mike Williams": ["Mike Williams", 'Michael "Mike" Williams'],
    "Callum Williams": ["Callum Williams", "Callum"],
    "Alex Williams": ["Alex Williams", 'Alexander "Alex" Williams'],
    "Meg Harlow": ["Meg Harlow", "Meg"],
    "Jess Kowalski": ["Jess Kowalski"],
    "Crissy Kowalski": ["Crissy Kowalski", "Crissy"],
    "Danny Tsang": ["Danny Tsang"],
    "Priya Anand": ["Priya Anand", "Priya"],
    "Vex": ["Vex"],
    "Cassius Nott": ["Cassius Nott", "Cassius"],
    "Pansy Parkinson": ["Pansy Parkinson", "Pansy"],
    "Blaise Zabini": ["Blaise Zabini", "Blaise"],
    "Filippo de' Medici": ["Filippo de' Medici", "Filippo Medici", "Filippo"],
    "Caterina Volkonskaya": ["Caterina Volkonskaya", "Caterina"],
    "Silas Thorne": ["Silas Thorne", "Silas"],
    "Samuel Carrow": ["Samuel Carrow", "Samuel"],
    "Lyra Carrow": ["Lyra Carrow"],
    "Dante": ["Dante"],
    "Astoria Greengrass": ["Astoria Greengrass", "Astoria"],
    "Daphne Scamander": ["Daphne Scamander", "Daphne Greengrass", "Daphne"],
    "Harry Potter": ["Harry Potter", "Harry"],
    "Amalthea Taylor": ["Amalthea Taylor", "Amalthea"],
    "Cole Lavigne": ["Cole Lavigne"],
    "Eli Lavigne": ["Eli Lavigne"],
    "Cyrus Taylor": ["Cyrus Taylor"],
    "Anne Hawthorne": ["Anne Hawthorne"],
    "Caroline Parr": ["Caroline Parr"],
    "Cassian Price": ["Cassian Price"],
    "Catherine Morrow": ["Catherine Morrow"],
    "Charlie Mercer": ["Charlie Mercer"],
    "Donovan Rowle": ["Donovan Rowle"],
    "Drake Lightwood": ["Drake Lightwood"],
    "Jackson Bellamy": ["Jackson Bellamy", 'Jackson "Jax" Bellamy', "Jax"],
    "Julie Knox": ["Julie Knox"],
    "Mira Vance": ["Mira Vance"],
    "Moira Bell": ["Moira Bell"],
    "Imogen Parkinson": ["Imogen Parkinson", "Imogen"],
}

# Precompile alias -> canonical, longest alias first so "Theo Nott" beats "Theo".
_ALIAS_PAIRS = sorted(
    ((alias, canon) for canon, aliases in CANON_CHARACTERS.items() for alias in aliases),
    key=lambda p: len(p[0]),
    reverse=True,
)
_ALIAS_REGEX = [
    (re.compile(r"\b" + re.escape(alias) + r"\b"), canon) for alias, canon in _ALIAS_PAIRS
]


def extract_characters(text):
    """Return sorted list of canonical character names mentioned in text."""
    found = set()
    for rx, canon in _ALIAS_REGEX:
        if rx.search(text):
            found.add(canon)
    return sorted(found)


# ---------------------------------------------------------------------------
# Date extraction. Handles: "June 30, 2026", "February 3, 2002",
# "2026-06-30", "February 3:" (year inferred from nearest full date in file).
# Returns an ISO date string (YYYY-MM-DD) when a full date is resolvable.
# ---------------------------------------------------------------------------
_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}
_MONTH_DAY_YEAR = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b",
    re.I,
)
_MONTH_RANGE_YEAR = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+"
    r"\d{1,2}(?:st|nd|rd|th)?\s*[–—-]\s*\d{1,2}(?:st|nd|rd|th)?,?\s+(\d{4})\b",
    re.I,
)
_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_MONTH_DAY = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?\b",
    re.I,
)


def _iso(y, m, d):
    try:
        return "%04d-%02d-%02d" % (int(y), int(m), int(d))
    except Exception:
        return None


def extract_dates(text, fallback_year=None):
    """Return sorted unique ISO dates found in text.
    fallback_year supplies a year for bare 'Month Day' mentions."""
    dates = set()
    for m in _ISO.finditer(text):
        d = _iso(m.group(1), m.group(2), m.group(3))
        if d:
            dates.add(d)
    for m in _MONTH_DAY_YEAR.finditer(text):
        d = _iso(m.group(3), _MONTHS[m.group(1).lower()], m.group(2))
        if d:
            dates.add(d)
    if fallback_year:
        # bare "Month Day" without an explicit year -> attach fallback year,
        # but skip spans already covered by a full date match.
        covered = {(mm.start(), mm.end()) for mm in _MONTH_DAY_YEAR.finditer(text)}
        for m in _MONTH_DAY.finditer(text):
            if any(m.start() >= s and m.end() <= e for s, e in covered):
                continue
            d = _iso(fallback_year, _MONTHS[m.group(1).lower()], m.group(2))
            if d:
                dates.add(d)
    return sorted(dates)


def file_year_hint(path, text):
    """Best-effort year for a file, used to resolve bare Month-Day dates.
    Prefers a 4-digit year in the filename, else the first full date in text."""
    m = re.search(r"(19|20)\d{2}", os.path.basename(path))
    if m:
        return m.group(0)
    for m in _MONTH_DAY_YEAR.finditer(text):
        return m.group(3)
    m = _ISO.search(text)
    if m:
        return m.group(1)
    return None


def chunk_year_hint(text, fallback_year=None):
    """Prefer a year stated inside the chunk over a file-wide fallback.

    Omnibus timeline files span multiple years, so their first dated event is
    unsafe as the fallback for later bare ``Month Day`` headings.  Section
    headings such as ``March 10–30, 2002`` provide the correct local year.
    """
    m = _MONTH_DAY_YEAR.search(text)
    if m:
        return m.group(3)
    m = _MONTH_RANGE_YEAR.search(text)
    if m:
        return m.group(2)
    m = _ISO.search(text)
    if m:
        return m.group(1)
    return fallback_year


# ---------------------------------------------------------------------------
# Chunking: split a file into sections by markdown headings (#..######),
# then merge tiny sections forward and split oversized ones on blank lines.
# Each chunk carries the file's title (first H1 or filename) as context.
# ---------------------------------------------------------------------------
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def _approx_tokens(s):
    return max(1, len(s) // CHARS_PER_TOKEN)


def _split_large(heading, body):
    """Split an oversized section into <=MAX_TOKENS pieces on paragraph breaks."""
    paras = re.split(r"\n\s*\n", body)
    pieces, cur = [], ""
    for p in paras:
        cand = (cur + "\n\n" + p).strip() if cur else p
        if _approx_tokens(cand) > MAX_TOKENS and cur:
            pieces.append(cur)
            cur = p
        else:
            cur = cand
    if cur.strip():
        pieces.append(cur)
    return pieces or [body]


def split_sections(text):
    """Yield (heading_text, section_body_including_heading) tuples."""
    lines = text.splitlines()
    sections = []
    cur_head = None
    cur_lines = []
    for ln in lines:
        m = _HEADING.match(ln)
        if m:
            if cur_lines or cur_head is not None:
                sections.append((cur_head, "\n".join(cur_lines)))
            cur_head = m.group(2).strip()
            cur_lines = [ln]
        else:
            cur_lines.append(ln)
    if cur_lines or cur_head is not None:
        sections.append((cur_head, "\n".join(cur_lines)))
    return sections


def _section_level(body):
    """Return the Markdown heading depth that opens a split section."""
    for line in body.splitlines():
        match = _HEADING.match(line)
        if match:
            return len(match.group(1))
        if line.strip():
            break
    return 0


def chunk_file(path, text):
    """Return a list of chunk dicts for one file."""
    # File title = first H1, else first heading, else filename stem.
    title = None
    for h, _ in split_sections(text):
        if h:
            title = h
            break
    if not title:
        title = os.path.splitext(os.path.basename(path))[0]

    year_hint = file_year_hint(path, text)
    raw = split_sections(text)

    # Merge a tiny section forward only into one of its descendants. Crossing
    # a peer or parent heading boundary mislabels the later material (for
    # example, a short Sunday section swallowing the following Monday entry).
    merged = []
    buf_head, buf_body, buf_level = None, "", 0
    for head, body in raw:
        if not body.strip():
            continue
        next_level = _section_level(body)
        can_merge_forward = buf_level == 0 or next_level > buf_level
        if (buf_body and _approx_tokens(buf_body) < MIN_TOKENS
                and can_merge_forward):
            buf_body = (buf_body + "\n\n" + body).strip()
            buf_head = buf_head or head
            buf_level = next_level
        else:
            if buf_body:
                merged.append((buf_head, buf_body))
            buf_head, buf_body, buf_level = head, body, next_level
    if buf_body:
        merged.append((buf_head, buf_body))

    chunks = []
    seq = 0
    for head, body in merged:
        pieces = [body] if _approx_tokens(body) <= MAX_TOKENS else _split_large(head, body)
        for i, piece in enumerate(pieces):
            heading = head or title
            # Prepend title context so an isolated chunk still names its source.
            if title and title != heading:
                embed_text = "%s\n\n%s" % (title, piece.strip())
            else:
                embed_text = piece.strip()
            chars = extract_characters(embed_text)
            dates = extract_dates(
                embed_text,
                fallback_year=chunk_year_hint(embed_text, year_hint),
            )
            chunks.append({
                "path": path,
                "title": title,
                "heading": heading,
                "part": i,
                "seq": seq,
                "text": piece.strip(),
                "embed_text": embed_text,
                "characters": chars,
                "dates": dates,
                "date_min": dates[0] if dates else None,
                "date_max": dates[-1] if dates else None,
                "tokens_approx": _approx_tokens(piece),
            })
            seq += 1
    return chunks


def walk_repo(repo_root):
    """Yield absolute paths of indexable files under repo_root."""
    for dirpath, dirnames, filenames in os.walk(repo_root):
        kept = []
        for dirname in dirnames:
            if dirname in SKIP_DIRS:
                continue
            candidate = os.path.join(dirpath, dirname)
            rel = os.path.relpath(candidate, repo_root).replace(os.sep, "/")
            if rel in SKIP_REL_DIRS:
                continue
            kept.append(dirname)
        dirnames[:] = kept
        for fn in filenames:
            # A template is an authoring aid, not canon evidence. Match the
            # explicit filename convention without excluding ordinary prose
            # that happens to discuss a template.
            stem = os.path.splitext(fn)[0].lower()
            candidate = os.path.join(dirpath, fn)
            rel = os.path.relpath(candidate, repo_root).replace(os.sep, "/")
            if rel in SKIP_REL_FILES:
                continue
            if fn.endswith(EXTS) and not (stem.endswith("_template") or stem == "template"):
                yield candidate


# ---------------------------------------------------------------------------
# Embedding credential resolution + call. No fabricated keys.
# ---------------------------------------------------------------------------
def resolve_embedding_key():
    """Return the OpenRouter embedding credential without exposing it."""
    for name in ("EMBEDDING_API_KEY", "OPENROUTER_API_KEY"):
        k = os.environ.get(name)
        if k:
            return k, "env:%s" % name
    cred = os.path.expanduser("~/.openclaw/credentials/openrouter-api-key")
    try:
        with open(cred) as f:
            k = f.read().strip()
        if k:
            return k, "file:openrouter-api-key"
    except Exception:
        pass
    return None, ("No embedding credential found: EMBEDDING_API_KEY and "
                  "OPENROUTER_API_KEY unset, and no openrouter-api-key file")


def embed_texts(texts, key, base_url=None):
    """Call the OpenAI-compatible embeddings API for a batch."""
    base = (base_url or os.environ.get("EMBEDDING_BASE_URL") or
            "https://openrouter.ai/api/v1").rstrip("/")
    url = base + "/embeddings"
    payload = json.dumps({"model": EMBED_MODEL, "input": texts}).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={"Authorization": "Bearer %s" % key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    return [item["embedding"] for item in sorted(data["data"], key=lambda x: x["index"])]


# ---------------------------------------------------------------------------
# SQLite storage.
# ---------------------------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id          INTEGER PRIMARY KEY,
    chunk_key   TEXT UNIQUE,
    path        TEXT,
    rel_path    TEXT,
    title       TEXT,
    heading     TEXT,
    part        INTEGER,
    text        TEXT,
    embed_text  TEXT,
    characters  TEXT,   -- JSON array
    dates       TEXT,   -- JSON array
    date_min    TEXT,
    date_max    TEXT,
    tokens_approx INTEGER,
    embedding   BLOB,   -- packed float32, or NULL if not yet embedded
    embed_model TEXT
);
CREATE INDEX IF NOT EXISTS idx_date_min ON chunks(date_min);
CREATE INDEX IF NOT EXISTS idx_date_max ON chunks(date_max);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    text, heading, title, characters, content=''
);
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
"""


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    return conn


def chunk_key(c, repo_root):
    rel = os.path.relpath(c["path"], repo_root)
    h = hashlib.sha1(("%s|%s|%d|%d" % (rel, c["heading"], c["part"], c.get("seq", 0))).encode()).hexdigest()[:16]
    return h


def pack_vec(vec):
    import struct
    return struct.pack("<%df" % len(vec), *vec)


def unpack_vec(blob):
    import struct
    n = len(blob) // 4
    return list(struct.unpack("<%df" % n, blob))
