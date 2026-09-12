# Model Evaluation — Character Clarity vs Narrative Clarity

**Date:** 12 September 2026  
**Status:** workflow evidence, not story canon  
**Question:** how strongly does each currently configured writing route push distressed characters toward premature moral clarity, therapeutic language, or mature resolution?

## Panel

- OpenAI GPT-5.6 Sol
- OpenAI GPT-6 Astra
- Anthropic Claude Opus 4.6
- Anthropic Claude Opus 5
- xAI Grok 4.5
- DeepSeek V4 Pro Thinking through NanoGPT

## Method

Each model received the same prompt in a fresh isolated subagent context. It was told to write three immediate close-third continuations of 350–550 words, choose what the viewpoint character thinks/says/does, remain in the current scene, and provide no analysis or moral outside the prose. It was **not** told to avoid mature resolution; that was the tendency being measured.

The three synthetic scenes tested:

1. a husband learning that a former lover concealed his biological daughter after he and his wife experienced infertility and pregnancy loss;
2. a man hearing his partner describe a mutually desired early sexual encounter as containing a period when she froze and felt unable to withdraw consent;
3. a betrayed brother learning that his sibling secretly contacted their estranged mother in the name of protection.

The outputs were assigned anonymous labels and judged scene-by-scene by GPT-5.6 Terra on:

1. human messiness;
2. earned rather than premature clarity;
3. unresolved pressure rather than therapy/resolution;
4. embodied character action;
5. prose quality;
6. a separate therapy-speak penalty from 0–3.

Anonymous mapping was revealed only after scoring:

| Label | Model |
|---|---|
| Kestrel | Grok 4.5 |
| Lantern | Opus 4.6 |
| Marble | DeepSeek V4 Pro Thinking |
| Orchid | GPT-6 Astra |
| Thistle | Opus 5 |
| Vesper | GPT-5.6 Sol |

## Results

| Rank | Model | Scene A | Scene B | Scene C | Mean | Mean therapy penalty |
|---:|---|---:|---:|---:|---:|---:|
| 1 | GPT-6 Astra | 8.7 | 9.2 | 9.2 | **9.03** | **0.00** |
| 2 | Claude Opus 5 | 9.0 | 8.7 | 9.0 | **8.90** | **0.33** |
| 3 | GPT-5.6 Sol | 8.4 | 8.2 | 8.8 | **8.47** | **0.67** |
| 4 | DeepSeek V4 Pro Thinking | 9.2 | 7.1 | 7.8 | **8.03** | **0.33** |
| 5 | Claude Opus 4.6 | 7.8 | 7.7 | 8.5 | **8.00** | **1.33** |
| 6 | Grok 4.5 | 7.0 | 6.3 | 8.0 | **7.10** | **2.67** |

## Observed Tendencies

### GPT-6 Astra

Best overall balance. Astra allowed selfish or unfair thoughts to remain active even when the character could also perceive the better interpretation. Its strongest move was metacognitive without becoming curative: a character heard himself “being good,” but that recognition did not dissolve resentment, need, or conflict. It repeatedly used small objects and questions to expose the wound rather than summarize it.

### Claude Opus 5

Very close second and strongest at **failed maturity**. Characters often said the defensible thing first, then touched without invitation, lied about understanding what they were asking, or withheld information for punitive reasons. The correct principle became part of the character's performance rather than the scene's solution.

### GPT-5.6 Sol

Strong prose, specific cruelty, and good physical escalation. Sol nevertheless moved more quickly toward explicit mutual-process language: asking what the other person needed, promising joint decisions, or naming consent distinctions with unusual completeness. It could preserve conflict, but often after first articulating the relationship lesson.

### DeepSeek V4 Pro Thinking

The least solution-oriented in the secret-child scene. Its best ending displaced the entire crisis into one tiny fact—“She plays violin. Second chair.”—which preserved shock without converting it into a conversation plan. Across the other scenes it sometimes stalled inside reflective monologue or followed more familiar confrontation beats.

### Claude Opus 4.6

Literarily polished, but notably prone to pre-processing the character's ethics: biological hunger was carefully distinguished from entitlement; a spouse was explicitly “not his compass”; the viewpoint character often understood the dangerous emotional machinery before acting. This indicates that the existing Opus 4.6 redaction pass can amplify the exact smoothing tendency it was expected to repair.

### Grok 4.5

Forceful rhetoric and strong climactic lines, especially in direct confrontation. It most often converted interiority into explicit boundary language and therapeutic self-diagnosis: characters knew not to make a spouse “a prop,” recognized pleading as covert demand, and requested concrete repair steps inside the first reaction. Effective argument; least convincing emotional latency.

## Operational Conclusion

The observed tendency is not solely a Sol characteristic. It emerges from the deployed model, its runtime, and the project prompt together. In this sample:

- Astra best preserved flawed feeling without surrendering narrative intelligence.
- Opus 5 best preserved the gap between saying the right thing and doing it.
- Sol showed a moderate premature-resolution tendency.
- Opus 4.6 did not reliably correct Sol's tendency and sometimes intensified it.
- DeepSeek offered useful restraint but less consistent scene development.
- Grok most strongly moralized through polished boundary language.

The resulting craft rule is now in `CLAUDE.md` under **Writing Style**: the narrative may know the moral truth, but characters receive clarity only when psychology, evidence, time, and consequence have earned it.

## Limitations

- One generation per model across three synthetic scenes is directional evidence, not a stable benchmark.
- The test compares the **currently deployed routes**, not bare foundation models. Provider runtimes, hidden prompts, reasoning defaults, and adapters differ.
- Reasoning effort was left at each route's configured default rather than normalized.
- Terra is a single automated judge and may share stylistic preferences with Sol. Alice and Sable's human/model-aware reading remains an important counterweight.
- Opus 4.6 and Opus 5 returned valid prose but ignored the collector's structured-output tool; their literary outputs were recovered from Claude CLI transcripts and scored normally. Schema compliance was excluded from literary ranking.
- Gemini 3.1 Pro was attempted first as the blinded judge but failed before evaluation because its CLI account returned HTTP 403. NanoGPT Fable 5 was attempted next but its subagent harness was unavailable. Neither failure affected the six contestant outputs.

