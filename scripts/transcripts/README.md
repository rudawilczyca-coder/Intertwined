# Local transcript archive

This tool builds a private, local SQLite/FTS5 search index from the archived
Claude Project export. The database is **derived evidence, not canon**. It stays
outside the repository under `/home/sable/archives/Intertwined/index/`.

Only visible human and assistant prose is indexed. Hidden thinking, tool calls,
and tool results are excluded. By default, searches also exclude superseded
conversation branches.

## Build or refresh

```bash
python3 scripts/transcripts/transcript_archive.py build
```

## Search

```bash
python3 scripts/transcripts/transcript_archive.py search "free pass" --context 1
python3 scripts/transcripts/transcript_archive.py search "New Orleans" --title "France"
python3 scripts/transcripts/transcript_archive.py search 'Jackie NEAR Draco' --fts
```

Useful filters:

- `--title TEXT` limits results to matching conversation titles.
- `--sender human|assistant` limits by speaker.
- `--context N` prints N neighbouring messages on either side.
- `--all-branches` includes abandoned edit/regeneration branches.
- `--fts` accepts raw SQLite FTS5 query syntax.

The script reports the source conversation title and export filename for every
match so a result can be traced back to the original JSON.

Normal searches treat the supplied words as one exact phrase. Use `--fts` for
broader expressions such as `Jackie AND potion` or `Jackie NEAR Draco`.
