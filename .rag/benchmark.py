#!/usr/bin/env python3
"""Small, repeatable retrieval benchmark built from real canon questions."""
import argparse
import os
import re
import subprocess
import sys


CASES = [
    ("Tuesday / no Tuesday", "Tuesday love when there is no Tuesday",
     ("pieces/theo_draco_july26_2002_the_reply_that_bounced.md",)),
    ("Eli cover", "Who is Theo's chosen World Cup cover?",
     ("reference/active_threads.md", "reference/scene_kit_current.md")),
    ("Theo's walks", "What is Theo's night-walking habit?",
     ("sessions/primrose_hill_walk_handoff.md", "characters/theodore_nott_character_updated3.md")),
    ("Paris hotel", "Which Paris hotel did Jackie and Draco choose?",
     ("arcs/the_honeymoon_they_owed.md", "reference/scene_kit_current.md")),
    ("Green Park", "What happened with the Green Park stalker and when?",
     ("lore/past_events_bible_updated3.md",)),
    ("Children", "What do Draco and Jackie currently want about children?",
     ("arcs/the_honeymoon_they_owed.md", "reference/active_threads.md")),
    ("Apology letter", "Did Draco write Ruby an apology letter?",
     ("sessions/july6_karaoke_day.md", "reference/active_threads.md")),
    ("Camarilla guns", "What Camarilla safeguards remain for Theo at the World Cup?",
     ("characters/London_Camarilla.md", "reference/active_threads.md")),
]
FORBIDDEN_PREFIXES = ("archive/superseded-planning/", "workflows/")
RESULT = re.compile(r"^\[[^]]+\]\s+(.+)$", re.M)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--rerank", choices=("auto", "on", "off"), default="auto")
    args = ap.parse_args()
    rag_dir = os.path.dirname(os.path.abspath(__file__))
    query_py = os.path.join(rag_dir, "query.py")

    passed = 0
    print("| Question | Expected source in top 5 | Duplicate-file cap | Excluded sources |")
    print("|---|---:|---:|---:|")
    for label, question, expected in CASES:
        proc = subprocess.run(
            [sys.executable, query_py, question, "--limit", str(args.limit),
             "--rerank", args.rerank],
            check=True, text=True, capture_output=True,
        )
        paths = RESULT.findall(proc.stdout)
        source_ok = any(path in expected for path in paths[:5])
        cap_ok = all(paths.count(path) <= 2 for path in set(paths))
        excluded_ok = not any(path.startswith(FORBIDDEN_PREFIXES) for path in paths)
        passed += int(source_ok and cap_ok and excluded_ok)
        print("| %s | %s | %s | %s |" % (
            label, "yes" if source_ok else "**no**",
            "yes" if cap_ok else "**no**", "yes" if excluded_ok else "**no**"))
    print("\n**Result: %d/%d cases passed.**" % (passed, len(CASES)))


if __name__ == "__main__":
    main()
