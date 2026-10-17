"""Command-line interface for ORDB."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .evaluator import evaluate_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ordb")
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate = subparsers.add_parser("evaluate", help="evaluate a structured run")
    evaluate.add_argument("input", type=Path)
    evaluate.add_argument("--output", type=Path)
    evaluate.add_argument("--pretty", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        with args.input.open("r", encoding="utf-8") as handle:
            run = json.load(handle)
        report = evaluate_run(run)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
