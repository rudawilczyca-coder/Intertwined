# Book Four retrieval pilot

This pilot tests transcript retrieval against **Book Four: Post-Florence & the
Summer (23 April–11 August 2001)**. It keeps three layers separate:

1. the archived Claude export is the lossless source;
2. `archive/messages.jsonl` and `archive/selected-path.md` are normalized and
   readable projections of that source;
3. `derived/chunks.jsonl` and the local SQLite/vector index are rebuildable.

The current event bible remains the authority for objective chronology and
outcomes. Selected transcript prose is source evidence for dialogue, emotional
context, and scene sequence. Alternate attempts, hidden branches, and inline
rewrites remain preserved but are excluded from default retrieval.

## Build

```bash
python3 scripts/book4_rag_pilot.py build
```

The command regenerates the normalized archive and child chunks. By default it
also creates a local index at
`/home/sable/archives/Intertwined/index/book4-rag-pilot.sqlite3` and embeds the
chunks when the existing OpenRouter credential is available. Use `--no-embed`
for a keyword-only build.

## Query

```bash
python3 scripts/book4_rag_pilot.py query \
  "Why did Jackie choose the Malice rather than forgive Theo?"
python3 scripts/book4_rag_pilot.py query \
  "Did Filippo's blood heal Theo?" --show-neighbors
python3 scripts/book4_rag_pilot.py query \
  "What happened in the discarded healing version?" --all-variants
```

Default mode is the strongest checked mode, currently keyword retrieval.
`--mode semantic` and `--mode hybrid` remain available for experiments, but the
first 27-question run showed that naive equal-weight fusion can displace exact
canon and event matches. Results cite stable chunk, conversation, message,
branch, and source IDs. `--all-variants` is deliberately required before
superseded or alternate material can compete with the selected story path.

## Benchmark

```bash
python3 scripts/book4_rag_pilot.py benchmark --mode keyword
python3 scripts/book4_rag_pilot.py benchmark --mode hybrid
```

`benchmark.json` contains checked questions and expected evidence locators.
`benchmark_results.md` records the latest comparison. The benchmark measures
retrieval, not prose-answer quality: whether the correct evidence appears in the
top five, whether a superseded branch leaks into default results, and whether an
unanswerable question is treated as such.
