"""Export the deterministic evidence used by the application."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from src.engine import build_decision_data

OUTPUT_DIR = ROOT / "outputs"


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, pd.Series):
        return _json_value(value.to_dict())
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and pd.isna(value):
        return None
    return value


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    case = build_decision_data(ROOT / "data")
    case["metrics"].to_csv(OUTPUT_DIR / "segmentos.csv", index=False)
    case["robustness"].to_csv(OUTPUT_DIR / "robustez.csv", index=False)
    case["shortlist"].to_csv(OUTPUT_DIR / "shortlist.csv", index=False)

    decision = case["decision"]
    payload = {
        "assumptions": asdict(case["assumptions"]),
        "thesis_verdict": decision["thesis_verdict"],
        "decision_status": decision["decision_status"],
        "evidence_strength": decision["evidence_strength"],
        "robust_same_winner": decision["robust_same_winner"],
        "robust_evidence_complete": decision["robust_evidence_complete"],
        "thesis": decision["thesis"],
        "challenger": decision["challenger"],
        "winner": decision["winner"],
        "reversal": decision["reversal"],
        "audit": case["audit"],
    }
    (OUTPUT_DIR / "decisao.json").write_text(
        json.dumps(_json_value(payload), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Evidence exported to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
