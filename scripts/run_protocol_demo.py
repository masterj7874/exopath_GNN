"""Run the standard-library-only synthetic ExoPath-GNN protocol demo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from exopath_gnn.pipeline import run_protocol_demo  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "artifacts" / "demo"))
    parser.add_argument("--config", default=str(ROOT / "config" / "default.json"))
    parser.add_argument("--schema", default=str(ROOT / "schemas" / "typed_graph_schema.json"))
    args = parser.parse_args()
    summary = run_protocol_demo(args.output, args.config, args.schema)
    print(f"Synthetic contract test complete: {summary['patient_count']} records")


if __name__ == "__main__":
    main()

