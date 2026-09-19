# London Court archive repair — 2026-09-19

Supersedes the incomplete 01:40 append report. Completed by the parent assistant, not Luna.

## Source and scope

- Read-only indexed extraction from `transcript_events` in the agent SQLite store, session `054c651f-9f75-4216-aed3-db6b270bb778` (Telegram DM `169400399`). No runtime database writes.
- Previous verified endpoint: Telegram 15492, Docs UTF-16 index 69816.
- Restored 17 source messages as 16 story turns (the split audio pair forms one turn), through Jackie’s London-connections warning, Telegram 15609.
- Local story: `2026-09-19_london_court_latest_turns.md`.
- Source sequence numbers: 30735, 30737, 30753, 30758, 30764, 30771, 30848, 30852, 30859, 30885, 30949, 30971, 30995, 31084, 31443, 31467, 31469.
- Earlier archived content preserved; OOC, operational chatter, voice demos, image captions and unpublished model drafts excluded.
- Latest disputed assistant continuation (sequence 31482) excluded entirely rather than inventing an accepted replacement; retained in `rejected/2026-09-19_viola_household_consultation.md` as NON-CANON evidence.

## Corrections and fidelity

- All assistant story bodies recovered directly from delivered-message transcript, not from generation drafts or prior flawed append. Corrected the duplicated/mutated sleeve sentence by restoring its exact source.
- Two approved Viola corrections applied: “That is the arrangement, Mr Nott.” and omission of her unsupported claim to have heard Jackie’s downstairs offer.
- Removed the expressly withdrawn sitting action and spoken “scratch that” OOC. Standing remains.
- Split audio joined at repeated lead-in; transport wrappers and escaped quote delimiters removed.
- Certain ASR proper names normalised: “Heaven House” → “Haven House”; “Viola Squirt” → “Viola's court”. Other uncertain spoken wording retained, not silently rewritten.
- Paragraph/heading formatting is presentational; user prose otherwise preserved. No new scene dialogue generated.

## Google Docs repair and verification

- Live Doc: https://docs.google.com/document/d/1g0ByTbXLcN9NLk6YUr-UiGkJ4uymYJSl6zP6NqNBp_U/edit
- Backed up complete raw document before mutation; revision-guarded batch replaced only faulty suffix `[69816,74786)`.
- Inserted 41,030 UTF-16 story characters. Read-back matches expected story exactly.
- All 557 prior structural elements through index 69816 compare identically, including text/style/index data.
- Restored range: 381 Google Docs paragraphs, 29 Heading 3 speaker headings, 46 intended italic spans. All intended text is italic; Docs additionally italicises 29 terminating paragraph newlines, with no unintended body text italicised.
- Final restored endpoint: index 110846.
- One body paragraph initially inherited heading style; corrected and read back before completion.
- No release, residency agreement, spent boon or new service has been canonised.
- Final revision: `ANLCKQntCS8w6eyEeZ9y9grOj6uU_ZAF_ErYVAzkCxBNm5I_5Qa5Mc2XGODPtOR5D2P2y4QtoziAoX28rL2hgUXMmjzXAMreV8bKHKELdsYN`.
- Story Markdown SHA-256: `8b03766163a2a0be60f92674805379ce47d4e188ff5876e28e53bbeb2e5576f6`.

Private raw evidence, requests and verification results remain in workspace `output/archive-repair-2026-09-19/`; not committed with unrelated conversation history.
