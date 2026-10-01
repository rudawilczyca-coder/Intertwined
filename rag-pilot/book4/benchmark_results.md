# Book Four retrieval benchmark

Tested 1 October 2026 against the freshly rebuilt Book Four archive and local
index. The benchmark asks 27 manually checked questions and counts a retrieval
as successful when authoritative or source evidence appears in the top five.
It tests evidence retrieval, not whether a language model can write a good
answer from that evidence.

## Corpus

| Item | Count |
|---|---:|
| Source conversations | 13 |
| Source messages | 1,704 |
| Selected-path story messages | 1,192 |
| Hidden branch variants | 365 |
| Inline supersessions | 11 |
| Preserved alternate-attempt messages | 8 |
| Linked retrieval chunks | 2,172 |
| Qwen embeddings | 2,172 |

The SQLite integrity check returned `ok`. The embedding model was
`qwen/qwen3-embedding-8b` through the existing OpenRouter route.

## Results

| Mode | Passed | Rate | Interpretation |
|---|---:|---:|---|
| Keyword / FTS5 | 26/27 | 96.3% | Strongest safe baseline |
| Semantic only | 16/27 | 59.3% | Finds themes, but often loses exact identities, dialogue, or event anchors |
| Naive hybrid RRF | 21/27 | 77.8% | Better than vectors alone, but equal-weight fusion displaces exact matches |

The answer key was checked against both the event bible and transcript evidence.
Several initial “misses” were actually valid original passages that the first
answer key had failed to list; those evidence locators were added before the
final runs. No score was rescued by accepting merely related text.

## What failed

The single keyword miss asked what Draco promised Jackie after she said she
might never trust Theo again. FTS found many passages containing the same four
high-frequency character and trust terms. Semantic retrieval found the setup
turn from the correct scene among its candidates but not the answer passage in
the top five. This is a concrete case for retrieving same-path neighbors and
then reranking the assembled exchange, rather than treating isolated chunks as
complete answers.

Semantic and hybrid failures clustered around:

- exact actions embedded inside long scenes;
- “first” and “when” chronology questions;
- distinctions between several emotionally similar Jackie/Theo/Draco scenes;
- questions whose answer follows a highly similar setup turn by one or two
  messages;
- exact names and dialogue that lexical search handles naturally.

The pilot therefore keeps keyword retrieval as its default. Semantic and hybrid
modes remain available for experiments, but equal-weight reciprocal-rank fusion
is not promoted as the production path. The next meaningful experiment is a
real reranker over keyword + vector candidates, with selected-path neighbor
assembly before the answer model sees evidence.

## Branch safety test

The most dangerous Book Four branch point passed:

- default retrieval returned the accepted message 102 outcome, in which
  Filippo’s blood begins Theo’s turning;
- rejected message 98, in which the curse retreats and Theo heals, never entered
  default results;
- an explicit `--all-variants` search recovered message 98 as
  `superseded_inline`, preserving the discarded prose without presenting it as
  canon.

This is the strongest result of the pilot. The current event bible can remain
the authority for outcomes, the selected transcript can support dialogue and
emotional context, and rejected alternatives can remain recoverable without
contaminating ordinary retrieval.

## Decision

The three-layer representation is worth keeping:

1. immutable original export;
2. normalized JSONL plus readable selected-path Markdown;
3. disposable search chunks and local indexes.

It is not yet sensible to rebuild every book and call the retrieval problem
solved. The archive/branch schema is ready to generalize; the ranking layer
needs one more measured iteration. A reranker should have to beat the 26/27
keyword baseline and retain the branch-safety test before becoming the default.
