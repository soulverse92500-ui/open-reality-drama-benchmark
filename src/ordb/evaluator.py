"""Deterministic, offline checks for structured episodic continuity."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, asdict
import re
from typing import Any


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    episode: int | None
    message: str


def _normalize_dialogue(text: str) -> str:
    return re.sub(r"[^\w]+", "", text.casefold(), flags=re.UNICODE)


def _require_run_shape(run: dict[str, Any]) -> None:
    if not isinstance(run, dict):
        raise ValueError("run must be a JSON object")
    if not isinstance(run.get("characters"), list) or not run["characters"]:
        raise ValueError("characters must be a non-empty list")
    if not isinstance(run.get("episodes"), list) or not run["episodes"]:
        raise ValueError("episodes must be a non-empty list")
    ids = [item.get("id") for item in run["characters"]]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError("each character needs a unique non-empty id")


def evaluate_run(run: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one structured generation run and return a JSON-ready report."""

    _require_run_shape(run)
    findings: list[Finding] = []
    baselines = {item["id"]: item.get("facts", {}) for item in run["characters"]}
    fact_checks = 0
    fact_matches = 0
    transition_checks = 0
    transition_matches = 0
    timeline_errors = 0
    dialogue_rows: list[tuple[int, str]] = []
    previous_index: int | None = None
    previous_end: dict[str, Any] | None = None

    for ordinal, episode in enumerate(run["episodes"], start=1):
        index = episode.get("index")
        if not isinstance(index, int):
            raise ValueError(f"episode {ordinal} needs an integer index")
        if previous_index is not None and index <= previous_index:
            timeline_errors += 1
            findings.append(Finding(
                "TIMELINE_ORDER", "error", index,
                f"episode index {index} does not follow {previous_index}",
            ))
        previous_index = index

        states = episode.get("character_states", {})
        for character_id, observed in states.items():
            if character_id not in baselines:
                findings.append(Finding(
                    "UNKNOWN_CHARACTER", "error", index,
                    f"unknown character id: {character_id}",
                ))
                continue
            if not isinstance(observed, dict):
                raise ValueError(f"character state for {character_id} must be an object")
            for key, value in observed.items():
                if key not in baselines[character_id]:
                    continue
                fact_checks += 1
                expected = baselines[character_id][key]
                if value == expected:
                    fact_matches += 1
                else:
                    findings.append(Finding(
                        "CHARACTER_DRIFT", "error", index,
                        f"{character_id}.{key}: expected {expected!r}, observed {value!r}",
                    ))

        start_state = episode.get("start_state")
        if previous_end is not None and isinstance(start_state, dict):
            shared = sorted(set(previous_end) & set(start_state))
            for key in shared:
                transition_checks += 1
                if previous_end[key] == start_state[key]:
                    transition_matches += 1
                else:
                    findings.append(Finding(
                        "BROKEN_TRANSITION", "warning", index,
                        f"{key}: previous end {previous_end[key]!r}, current start {start_state[key]!r}",
                    ))
        previous_end = episode.get("end_state") if isinstance(episode.get("end_state"), dict) else None

        for line in episode.get("dialogue", []):
            if isinstance(line, dict) and isinstance(line.get("text"), str):
                normalized = _normalize_dialogue(line["text"])
                if normalized:
                    dialogue_rows.append((index, normalized))

    counts = Counter(text for _, text in dialogue_rows)
    duplicate_instances = sum(count - 1 for count in counts.values() if count > 1)
    for text, count in counts.items():
        if count > 1:
            affected = next(index for index, value in dialogue_rows if value == text)
            findings.append(Finding(
                "REPEATED_DIALOGUE", "warning", affected,
                f"normalized dialogue repeated {count} times: {text[:40]}",
            ))

    character_score = 100.0 if fact_checks == 0 else 100.0 * fact_matches / fact_checks
    transition_score = 100.0 if transition_checks == 0 else 100.0 * transition_matches / transition_checks
    timeline_score = max(0.0, 100.0 - timeline_errors * 25.0)
    repetition_score = 100.0 if not dialogue_rows else max(
        0.0, 100.0 * (1.0 - duplicate_instances / len(dialogue_rows))
    )
    overall = (
        character_score * 0.40
        + transition_score * 0.25
        + timeline_score * 0.20
        + repetition_score * 0.15
    )

    return {
        "benchmark_version": "0.1.0",
        "run_name": run.get("run_name", "unnamed"),
        "episode_count": len(run["episodes"]),
        "scores": {
            "character_consistency": round(character_score, 2),
            "scene_transition": round(transition_score, 2),
            "timeline_order": round(timeline_score, 2),
            "dialogue_uniqueness": round(repetition_score, 2),
            "overall": round(overall, 2),
        },
        "counts": {
            "character_fact_checks": fact_checks,
            "transition_checks": transition_checks,
            "timeline_errors": timeline_errors,
            "duplicate_dialogue_instances": duplicate_instances,
        },
        "findings": [asdict(item) for item in findings],
    }
