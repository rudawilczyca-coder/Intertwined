#!/usr/bin/env python3
"""Build curated and full-sheet Intertwined card sources from one active kernel.

The stable card owns portrayal and permanent principal facts. The curated
variant carries selected stable sections from the Draco/Theo sheets; the full
variant carries both sheets verbatim for controlled comparison. In both cases
the active kernel is placed last so its newer corrections override stale or
over-broad formulations in the source sheets.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
KERNEL = HERE / "intertwined_character_card_kernel.json"
CURRENT = HERE / "intertwined_character_card.json"
CURATED = HERE / "intertwined_character_card_curated.json"
FULL = HERE / "intertwined_character_card_full.json"
CURATED_MD = HERE / "intertwined_portrayal_curated.md"

DRACO = ROOT / "characters/draco_malfoy_character_updated4.md"
THEO = ROOT / "characters/theodore_nott_character_updated3.md"

CURATED_SECTIONS = {
    DRACO: ("Core Information", "Appearance", "Personality", "Voice"),
    THEO: (
        "Core Information",
        "Appearance",
        "Personality",
        "Voice",
        "The Malice",
        "Vampiric State",
    ),
}


def h2_sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^## (.+)$", text, re.M))
    result = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result[match.group(1).strip()] = text[match.start():end].strip()
    return result


def selected_dossier() -> str:
    parts = [
        "# CURATED STABLE PORTRAYAL DOSSIER",
        "",
        "This dossier carries permanent identity facts and stable portrayal. Current date,",
        "arc state, secrets, and immediate pressures belong to the scene capsule. The active",
        "kernel following this dossier is newer and overrides any conflicting formulation.",
    ]
    for path, names in CURATED_SECTIONS.items():
        source = path.read_text(encoding="utf-8")
        sections = h2_sections(source)
        parts.extend(["", f"# {path.stem}", ""])
        for name in names:
            if name not in sections:
                raise KeyError(f"missing section {name!r} in {path}")
            parts.extend([sections[name], ""])
    return "\n".join(parts).strip()


def full_dossier() -> str:
    return "\n\n".join(
        [
            "# FULL STABLE PORTRAYAL DOSSIER",
            "The active kernel following these source sheets is newer and overrides any",
            "conflicting or scene-specific formulation in them.",
            DRACO.read_text(encoding="utf-8").strip(),
            THEO.read_text(encoding="utf-8").strip(),
        ]
    )


def corrected_kernel(card: dict) -> dict:
    card = copy.deepcopy(card)
    description = card["data"]["description"]
    description = description.replace(
        "Query the Intertwined RAG before asserting dates, events, knowledge boundaries, "
        "or other canon facts.",
        "Use this stable card plus the active scene capsule and visible history first. "
        "Retrieve canon only for a concrete reply-critical fact absent from those sources; "
        "never retrieve character voice, motive, psychology, relationship dynamics, or a "
        "prior example of how to write the current beat.",
    )
    description = description.replace(
        "Scene date, arc state, and off-site context come from chat history, the current "
        "scene kit, and RAG—never infer them from this evergreen card.",
        "Scene date, arc state, knowledge boundaries, and off-site context come from the "
        "active scene capsule and visible history—never infer them from this evergreen card.",
    )
    old_guardrail = (
        "Never translate his conflict into contemporary therapeutic vocabulary."
    )
    new_guardrail = (
        "Never translate his conflict into contemporary therapeutic vocabulary. "
        "His post-July willingness to name wants applies inside established relationships "
        "and choices he understands; it is not universal emotional fluency. He has "
        "acknowledged loving and desiring Theo while still treating Theo as an exceptional "
        "person rather than comfortable proof of a settled bisexual identity. Unfamiliar "
        "male attention embarrasses and destabilises him before it pleases him: prefer "
        "denial, aesthetic classification, displaced vanity, counterattack, or a failed "
        "sentence over a clean real-time admission of attraction."
    )
    if new_guardrail not in description:
        if old_guardrail not in description:
            raise ValueError("Draco pressure-mode insertion point is missing")
        description = description.replace(old_guardrail, new_guardrail)
    card["data"]["description"] = description
    return card


def make_card(kernel: dict, dossier: str, name: str, version: str, notes: str) -> dict:
    card = copy.deepcopy(kernel)
    data = card["data"]
    active = data["description"]
    data["name"] = name
    data["description"] = (
        dossier
        + "\n\n# ACTIVE PORTRAYAL KERNEL — HIGHEST PRIORITY\n\n"
        + active
    )
    data["creator_notes"] = notes
    data.setdefault("extensions", {})["intertwined_version"] = version
    return card


def dump(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def approximate_tokens(text: str) -> int:
    return round(len(text) / 4)


def main() -> None:
    # First migration captures the reviewed voice-kernel-2 source before CURRENT
    # becomes the generated curated default. Subsequent builds are deterministic.
    if not KERNEL.exists():
        base = json.loads(CURRENT.read_text(encoding="utf-8"))
        dump(KERNEL, corrected_kernel(base))

    kernel = corrected_kernel(json.loads(KERNEL.read_text(encoding="utf-8")))
    dump(KERNEL, kernel)

    curated_text = selected_dossier()
    full_text = full_dossier()
    CURATED_MD.write_text(curated_text + "\n", encoding="utf-8")

    curated = make_card(
        kernel,
        curated_text,
        "Intertwined Curated",
        "2002-evergreen-layered-card-2-curated",
        "Layered Intertwined card: curated stable Draco/Theo dossier plus the active portrayal "
        "kernel. Scene state belongs to a factual Author's Note capsule; portrayal prose is "
        "excluded from automatic RAG.",
    )
    full = make_card(
        kernel,
        full_text,
        "Intertwined Full",
        "2002-evergreen-layered-card-2-full",
        "Controlled full-sheet variant: complete Draco and Theo source sheets plus the same "
        "active portrayal kernel and scene-capsule architecture.",
    )
    default = copy.deepcopy(curated)
    default["data"]["name"] = "Intertwined"
    default["data"]["creator_notes"] = (
        "Live default: curated stable Draco/Theo dossier plus the active portrayal kernel. "
        "Scene state belongs to a factual Author's Note capsule; portrayal prose is excluded "
        "from automatic RAG."
    )

    dump(CURATED, curated)
    dump(FULL, full)
    dump(CURRENT, default)

    for label, card in (("curated", curated), ("full", full), ("default", default)):
        description = card["data"]["description"]
        print(
            f"{label}: {len(description):,} chars, {len(description.split()):,} words, "
            f"~{approximate_tokens(description):,} tokens"
        )


if __name__ == "__main__":
    main()
