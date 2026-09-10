#!/usr/bin/env python3
"""Validate the generated Japanese applied-subject CSV samples."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


SAMPLE_DIR = Path(__file__).resolve().parent
EXPECTED = {code: 10 for code in ("NUR", "CIV", "ECO", "STA", "ETH", "ICT")}


def validate_file(path: Path) -> str:
    """Validate one WebApp CSV file and return its question ID."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows or any(not row for row in rows):
        raise ValueError(f"{path.name}: empty file or row")

    configs = {row[1]: row[2] for row in rows if row[0] == "config" and len(row) == 3}
    question_id = configs.get("question_id", "")
    if question_id != path.stem:
        raise ValueError(f"{path.name}: question_id is {question_id!r}")
    if configs.get("mode") != "rb" or configs.get("require_pairs") != "true":
        raise ValueError(f"{path.name}: not an rb paired question")
    if configs.get("base_language") != "ja":
        raise ValueError(f"{path.name}: base language is not Japanese")

    qtexts = [row for row in rows if row[0] == "qtextL"]
    if len(qtexts) != 1 or len(qtexts[0]) != 3 or qtexts[0][1] != "ja":
        raise ValueError(f"{path.name}: expected one Japanese qtextL")
    if "__SELPROMPT__" not in qtexts[0][2] or "__SELTYPE__" in qtexts[0][2]:
        raise ValueError(f"{path.name}: invalid selection prompt")

    options: dict[str, Counter[str]] = defaultdict(Counter)
    feedback: Counter[str] = Counter()
    for row in rows:
        if row[0] == "option":
            if len(row) != 4 or row[2] not in {"C", "W"} or not row[3].strip():
                raise ValueError(f"{path.name}: invalid option row {row!r}")
            options[row[1]][row[2]] += 1
        elif row[0] == "feedback":
            if len(row) != 3 or not row[2].strip():
                raise ValueError(f"{path.name}: invalid feedback row {row!r}")
            feedback[row[1]] += 1

    expected_patterns = int(configs.get("num_options", "0"))
    if len(options) != expected_patterns:
        raise ValueError(f"{path.name}: pattern count does not match num_options")
    for pattern, truths in options.items():
        if truths != Counter({"C": 1, "W": 1}) or feedback[pattern] != 1:
            raise ValueError(f"{path.name}: pattern {pattern} is not one complete pair")
    if set(feedback) != set(options):
        raise ValueError(f"{path.name}: option and feedback patterns differ")
    return question_id


def main() -> None:
    """Validate the complete collection."""
    files = sorted(SAMPLE_DIR.glob("[A-Z][A-Z][A-Z][0-9][0-9].csv"))
    counts = Counter(path.stem[:3] for path in files)
    if counts != Counter(EXPECTED):
        raise ValueError(f"unexpected category counts: {dict(counts)}")

    question_ids = [validate_file(path) for path in files]
    duplicates = [item for item, count in Counter(question_ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"duplicate question IDs: {duplicates}")
    print(f"Validated {len(files)} Japanese paired MCQ samples: {dict(counts)}")


if __name__ == "__main__":
    main()
