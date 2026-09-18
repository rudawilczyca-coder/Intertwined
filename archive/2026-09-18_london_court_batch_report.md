# London Court archive batch — 2026-09-18

## Scope and source

- Story scene: Sunday, 11 August 2002 — London Court.
- Live Google Doc: `1g0ByTbXLcN9NLk6YUr-UiGkJ4uymYJSl6zP6NqNBp_U`, titled
  `Intertwined — London Court — Sunday, 11 August 2002`.
- Google account/approved route: `sable.the.raven@gmail.com` through `gog` Docs
  commands. No sharing or messaging changes were made.
- Exact source session: key
  `agent:main:telegram:direct:169400399`; session ID
  `054c651f-9f75-4216-aed3-db6b270bb778`.
- Retrieval: OpenClaw session discovery followed by the gateway
  `chat.history` route for that exact session, limit 200. The accepted window
  is 2026-09-18 17:44:03–19:48:39 UTC (19:44–21:48:39 Europe/Warsaw).

## Archived material

The verbatim story-body batch is [2026-09-18_london_court_batch_turns.md](2026-09-18_london_court_batch_turns.md), 13 source turns represented as 262 non-empty paragraphs / 4,650 words / 26,919 bytes. Its SHA-256 is:

`c24c34b3f33a55098576743107b21d9543405efc506ee28acec4f67927db398b`

Accepted Telegram source IDs, in order:

`15471, 15472, 15473, 15474, 15476, 15477, 15478, 15479, 15480, 15481, 15482, 15485, 15492`

Excluded Telegram records in the same window were 15483, 15484, 15486,
15487, 15489, and 15490 (correction/OOC, discarded prose, or repair/status
exchange); adjacent tool records were also excluded.

This includes the continuation from Theo's response to Jackie's embrace through
the Filippo/Nell exchange and Jackie's dragon confession. OOC prefixes and
suffixes, tool chatter, errors, and superseded prose were omitted. Original
story spelling and typos were retained.

- Telegram 15482 is archived with the explicitly corrected line
  `*The dragon would not have cared.*`; the OOC correction itself is not story
  text.
- The entire superseded assistant reply (Telegram 15486), beginning “The
  thought did not reach Theo,” was excluded, including its red-wolf witness
  error.
- The replacement assistant response is the story body from
  `pieces/2002-08-11_dragon_confession_rewrite.md` (SHA-256
  `935aa1286100c5a081dc4229cd8c50a8de89d33a68bcf3e79b41900dc5d6077e`), sent
  as Telegram 15492.
- Draco's “I checked” is retained. The Fontainebleau capsule independently
  records that he verified Jackie alive and unburned after the dragon run; no
  extra witness, animal-form, or red-wolf detail was invented.

## Google Docs write and read-back

Before the write, `gog docs cat` returned 43,817 bytes and the Docs structure
returned 294 paragraphs, 20 Heading 3 paragraphs, 71 empty paragraphs, final
index 43,772, revision
`ANLCKQmwZEu73bENPE8HGJHBjP9gM4kDymJH0d0N-tTpfCwYxZINSK9X0ATIJUuhql1RHcBdt2jhmVMN4PnHx7w7XJMD_HGl4SjiRFmCnko4`.

The archive was inserted at the document end with Markdown conversion. The
insert endpoint reported 26,741 converted characters and 55 requests. A
follow-up atomic batch (`01a0b621-77da-7a19-9280-86b338bf434a`) restored the 70
pre-existing empty paragraph breaks that were not part of the new story. A
final prefix comparison found all 294 original paragraphs, text, paragraph
types, and indices unchanged.

Final live read-back:

- `gog docs cat`: 70,364 bytes.
- Docs structure: 557 paragraphs, 38 Heading 3 paragraphs, 72 empty
  paragraphs (the original 71 plus the document terminal paragraph).
- Final revision:
  `ANLCKQnr0kS8yqtXWKk6uoL2B6qVOYdPjfv6RwaW9pWFGGnCbVKzmio4_pcq5Xhb1ARYR4Y27GywaXJ1UovFT-5sdohHUD1EZ0_UyoPfGfrn`.
- The appended range begins at index 43,772 with `Theodore` and ends at index
  69,816 with the exact final question: “Was getting that close what you
  wanted,” he asked, “or did you decide to go through because he thought you
  wouldn't?”
- Raw Docs read-back matched all 262 appended non-empty paragraphs and all
  italic spans: 36 italic runs / 609 italic characters in the appended range.

The factual cursor in `reference/scene_capsules/2002-08-11_london_court.md`
now points to Telegram 15492. Release, residency, presentation, and Viola's
final terms remain unresolved.
