from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "tokens" / "presentation-modes.json"
REFERENCE = ROOT / "references" / "presentation-modes.md"


def main() -> None:
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    charts = data["charts"]
    ids = [item["id"] for item in charts]
    expected = [f"C{index}" for index in range(1, 25)]
    modes = set(data["modes"])
    motions = set(data["motionGrammars"])
    documented_rows = []
    for line in REFERENCE.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\| (C\d+) \| [^|]+ \| ([ABC]) \| ([a-z]+) \| [^|]+ \| (low|medium|high) \| ([ABC]) \|", line)
        if match:
            documented_rows.append(match.groups())
    contract_rows = [(item["id"], item["mode"], item["motion"], item["risk"], item["batch"]) for item in charts]

    checks = {
        "exact C1-C24 coverage": ids == expected,
        "unique chart IDs": len(ids) == len(set(ids)),
        "valid modes": all(item["mode"] in modes for item in charts),
        "valid motion grammars": all(item["motion"] in motions for item in charts),
        "approved mode totals": Counter(item["mode"] for item in charts) == Counter({"A": 10, "B": 9, "C": 5}),
        "approved prototypes": data["approvedPrototypes"] == {"A": "C1", "B": "C14", "C": "C6"},
        "A evidence remains local": all("side-bay" not in item["evidence"] and "embedded" not in item["evidence"] for item in charts if item["mode"] == "A"),
        "B evidence is embedded": all(item["evidence"].startswith("embedded-") for item in charts if item["mode"] == "B"),
        "C evidence uses side bay": all(item["evidence"].startswith("side-bay-") for item in charts if item["mode"] == "C"),
        "full-interface set is frozen": {item["id"] for item in charts if item["mode"] == "C"} == {"C3", "C6", "C8", "C15", "C22"},
        "group-aligned migration batches": all(item["batch"] == item["mode"] for item in charts),
        "bounded risk values": all(item["risk"] in {"low", "medium", "high"} for item in charts),
        "reference table matches contract": documented_rows == contract_rows,
    }

    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    passed = sum(checks.values())
    print(f"{passed}/{len(checks)} checks passed")
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
