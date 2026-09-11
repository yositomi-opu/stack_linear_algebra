#!/usr/bin/env python3
"""Validate the generated Japanese applied-subject CSV samples."""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


SAMPLE_DIR = Path(__file__).resolve().parent
EXPECTED = {code: 10 for code in ("NUR", "CIV", "ECO", "STA", "ETH", "ICT")}
SELECTION_PROMPTS = (
    "正しいものを1つ選べ。",
    "正しいものを1つ選べ（複数ある場合も1つでよい）。",
    "正しいものをすべて選べ。",
)


def validate_file(path: Path) -> str:
    """Validate one WebApp CSV file and return its question ID."""
    if not path.read_bytes().startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"{path.name}: UTF-8 BOM is missing")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows or any(not row for row in rows):
        raise ValueError(f"{path.name}: empty file or row")

    configs = {row[1]: row[2] for row in rows if row[0] == "config" and len(row) >= 3}
    if configs.get("csv_schema") != "2":
        raise ValueError(f"{path.name}: CSV schema is not 2")
    question_id = configs.get("question_id", "")
    if question_id != path.stem:
        raise ValueError(f"{path.name}: question_id is {question_id!r}")
    if configs.get("mode") != "rb" or configs.get("require_pairs") != "true":
        raise ValueError(f"{path.name}: not an rb paired question")
    if configs.get("base_language") != "ja":
        raise ValueError(f"{path.name}: base language is not Japanese")

    qtexts = [row for row in rows if row[0] == "qtextL"]
    if len(qtexts) != 1 or len(qtexts[0]) != 4 or qtexts[0][1:3] != ["string", "ja"]:
        raise ValueError(f"{path.name}: expected one Japanese qtextL")
    question_text = qtexts[0][3]
    if question_text.count("__SELPROMPT__") != 1 or "__SELTYPE__" in question_text:
        raise ValueError(f"{path.name}: invalid selection prompt")
    prefix, suffix = question_text.split("__SELPROMPT__")
    if suffix.strip() or not prefix.rstrip().endswith(("。", ".", "！", "!", "？", "?")):
        raise ValueError(f"{path.name}: __SELPROMPT__ must be an independent final sentence")
    for prompt in SELECTION_PROMPTS:
        rendered = question_text.replace("__SELPROMPT__", prompt)
        if "__SELPROMPT__" in rendered or not rendered.endswith(prompt):
            raise ValueError(f"{path.name}: selection prompt substitution failed")

    options: dict[str, Counter[str]] = defaultdict(Counter)
    feedback: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        option_match = re.fullmatch(r"option(\d+)([CW])", row[0])
        feedback_match = re.fullmatch(r"feedback(\d+)([CW])?", row[0])
        if option_match:
            if len(row) != 4 or row[1] not in {"string", "cas", "cas_list"} or not row[3].strip():
                raise ValueError(f"{path.name}: invalid option row {row!r}")
            options[option_match.group(1)][option_match.group(2)] += 1
        elif feedback_match:
            if len(row) != 4 or row[1] not in {"string", "cas"} or not row[3].strip():
                raise ValueError(f"{path.name}: invalid feedback row {row!r}")
            feedback[feedback_match.group(1)][feedback_match.group(2) or "shared"] += 1

    required_choices = int(configs.get("num_options", "0"))
    if len(options) < required_choices:
        raise ValueError(f"{path.name}: fewer patterns than num_options")
    for pattern, truths in options.items():
        feedback_shape = feedback[pattern]
        valid_feedback = not feedback_shape or feedback_shape == Counter({"shared": 1}) or feedback_shape == Counter({"C": 1, "W": 1})
        if truths != Counter({"C": 1, "W": 1}) or not valid_feedback:
            raise ValueError(f"{path.name}: pattern {pattern} is not one complete pair")
    if not set(feedback).issubset(options):
        raise ValueError(f"{path.name}: feedback exists without a matching option")
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
