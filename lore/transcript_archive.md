# Intertwined Transcript Archive

## Purpose and authority

The transcript archive is a **targeted evidence layer**, not a second canon.

1. `lore/canon_index.md`, stable character cards, and the active scene capsule
   remain the authority for what is settled and currently portrayable.
2. Google Docs hold the readable primary scene text for live and curated scenes.
3. The local SQLite archive supports exact recovery from the older Claude
   Project export: wording, chronology, physical continuity, and source tracing.
4. Alternate branches, rejected drafts, OOC discussion, and superseded material
   do not become canon merely because a search finds them.

For portrayal, follow `CLAUDE.md`: use raw prose only to recover concrete facts.
Reduce findings to a terse factual ledger before writing; do not imitate an old
reply's voice, motives, or scene solution.

## Google Drive structure

Root: [Intertwined](https://drive.google.com/drive/folders/1wiHG-10m93aYdQgDr6p_1fWNOsgpqI2V)

- `00 — Live Threads` — current collaborative scene Docs.
- `10 — Canon Scene Archive` — completed, accepted scene documents.
- `20 — Retrospections & Missing Scenes` — deliberately reconstructed scenes.
- `30 — Planning, Prompts & Character Work` — plans, cards, references, images,
  summaries, and writing support.
- `90 — Alternate & Rejected Model Drafts` — non-canon alternatives and scene
  fragments whose status is not accepted canon.
- `99 — Raw Imports & Legacy Books` — exports, original books, and legacy source
  bundles retained as evidence.

Moving a file into these folders does not alter its canon status. Folder names
describe document purpose, not authority.

## Local SQLite archive

Source snapshot:

`/home/sable/archives/Intertwined/claude-project-export-2026-08-16/Claude_project_export_Intertwined _ A Draco & Theo romance_019c8524-43e4-72ad-b0ad-23454d3b5072/`

Derived database (private; not committed):

`/home/sable/archives/Intertwined/index/intertwined-transcripts.sqlite3`

Current build:

- 135 conversations
- 7,993 visible human/assistant messages
- 7,154 visible messages on final active branches
- hidden thinking, tool calls, and tool results excluded
- abandoned branches stored but excluded from ordinary searches

Build, search, and verification instructions live in
`scripts/transcripts/README.md`. Typical targeted search:

```bash
python3 scripts/transcripts/transcript_archive.py search \
  "exact remembered phrase" --title "conversation title" --context 2
```

Search results always include the original conversation title and JSON export
filename. Use `--all-branches` only when investigating edits or regenerations;
never treat those results as accepted scene history without corroboration.

## Maintenance

- Rebuild the database after adding or replacing a Claude export snapshot.
- Keep the source JSON archive immutable; rebuild the derived database instead
  of editing it by hand.
- Keep the SQLite file off GitHub because it contains the full private text.
- Add new live Google Docs to Drive first. A later exporter may add them to the
  local index, but Drive remains their primary readable home.
