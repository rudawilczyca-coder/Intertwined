# Haven House publication and repair report — 2026-09-24

## Scope

- Live Doc: `Intertwined — Haven House — Sunday, 11 August 2002`
- Google Doc ID: `1NovuVIspPVWlTsPntVRkFTBYa8Kx6Da4WuI-OP_lRKw`
- Existing verified source: `2026-09-23_haven_house_turns.md`
- New verified source: `2026-09-24_haven_house_turns.md`
- New source session: `agent:main:telegram:direct:169400399`

The new batch contains six accepted Ruby rounds and six accepted Sable rounds.
Sable rounds remain whole even when they contain multiple character
perspectives. OOC notes, model-cost notes, and internal character headings were
excluded.

## Repair

The pre-write raw Doc inspection found roughly 39 missing characters and
paragraph-boundary damage in the previously published batch. Examples included
`higher` rendered as `hiher` and `Filippo` rendered as `ilippo`. The corruption
was consistent with the earlier reverse-ordered blank-paragraph deletion path
removing the character before a spacer.

The damaged Doc body was therefore replaced once from the two verified local
archives rather than appended to. The replacement used plain text with one
newline per paragraph and no empty paragraphs; labels and italics were applied
afterward. No Markdown converter or spacer-deletion pass was used.

## Verification

- Final plain-text SHA-256: `43f7329a3e25057ee6a8d9eb9d26f581fbdbacf54646a680ff3c00ce6a372d3a`
- Text readback matches the rebuilt source exactly.
- Paragraphs: 320; empty paragraphs: 0.
- Heading 3 labels: 22, exactly `Ruby | Sable` repeated 11 times.
- Every non-label paragraph is `NORMAL_TEXT`.
- Rich-text italics match exactly: `Not enough.`, `Nine o'clock,`, `You reached her.`, `I called.`, `She didn’t know what she heard.`, `Neither did you.`, `She always hears Me when it matters.`, and `Monsieur Morel` in Draco's wake-up sentence.
- No temporary marker remains.
- Final text: “He held the glass shower door open for her, steam curling out past his arm.”

The live cursor and scene capsule were advanced only after these checks passed.
