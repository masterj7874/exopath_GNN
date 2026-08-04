"""Command-line entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_protocol_demo


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Run the ExoPath-GNN synthetic protocol dry run")
    parser.add_argument("--output", default=str(root / "artifacts" / "demo"))
    parser.add_argument("--config", default=str(root / "config" / "default.json"))
    parser.add_argument("--schema", default=str(root / "schemas" / "typed_graph_schema.json"))
    args = parser.parse_args()
    summary = run_protocol_demo(args.output, args.config, args.schema)
    print(f"Synthetic contract test complete: {summary['patient_count']} records; output={args.output}")


if __name__ == "__main__":
    main()

