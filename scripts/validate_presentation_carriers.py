from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from moxing import (  # noqa: E402
    CHARTS,
    DirectCanvas,
    EmbeddedEvidence,
    EvidenceInterface,
    PrecisionInterface,
    render_chart,
)
from moxing.core import ChartArtwork, ChartPage, PRESENTATION_TARGETS, html_page  # noqa: E402


def main() -> None:
    rendered = {chart_id: render_chart(chart_id) for chart_id in CHARTS}
    active = {
        chart_id: re.search(r'data-presentation-carrier="([a-z]+)"', source).group(1)
        for chart_id, source in rendered.items()
    }
    targets = {
        chart_id: re.search(r'data-presentation-target="([a-z]+)"', source).group(1)
        for chart_id, source in rendered.items()
    }
    interface_ids = {"C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C15", "C22"}

    legacy_spec = PrecisionInterface("E00", "0 0 10 10", 0, 100, "", "")
    legacy_artwork = ChartArtwork("<g></g>", precision=legacy_spec)
    embedded_page = ChartPage(
        chart_id="C14",
        slug="probe",
        public_name="Probe",
        title="Probe",
        subtitle="Probe",
        footer="Probe",
        svg="<g></g>",
        data={},
        presentation=EmbeddedEvidence("E14", "<g></g>", "<g></g>"),
        presentation_target="embedded",
    )
    embedded_html = html_page(embedded_page)

    checks = {
        "all charts declare an active carrier": set(active) == set(CHARTS) and set(active.values()) <= {"direct", "embedded", "interface"},
        "all charts declare approved targets": targets == PRESENTATION_TARGETS,
        "I0 preserves the existing interface set": {chart_id for chart_id, mode in active.items() if mode == "interface"} == interface_ids,
        "I0 preserves the existing direct set": {chart_id for chart_id, mode in active.items() if mode == "direct"} == set(CHARTS) - interface_ids,
        "I0 activates no embedded production chart": "embedded" not in active.values(),
        "interface markup remains compatible": all('data-interface="precision-v2.1"' in rendered[chart_id] and 'class="chart-body pi-split-body"' in rendered[chart_id] for chart_id in interface_ids),
        "direct markup has no split bay": all('<section class="chart-body pi-split-body">' not in rendered[chart_id] and 'class="chart-body pm-direct-body"' in rendered[chart_id] for chart_id in set(CHARTS) - interface_ids),
        "embedded carrier renders full-width local evidence": 'class="chart-body pm-embedded-body"' in embedded_html and 'class="pm-local-evidence"' in embedded_html and '<section class="chart-body pi-split-body">' not in embedded_html,
        "legacy PrecisionInterface name aliases EvidenceInterface": PrecisionInterface is EvidenceInterface,
        "legacy ChartArtwork precision argument resolves to interface carrier": legacy_artwork.presentation is legacy_spec and legacy_artwork.presentation.mode == "interface",
        "conflicting carrier arguments fail closed": conflict_fails(),
    }

    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    passed = sum(checks.values())
    print(f"{passed}/{len(checks)} checks passed")
    if passed != len(checks):
        raise SystemExit(1)


def conflict_fails() -> bool:
    try:
        ChartArtwork("<g></g>", presentation=DirectCanvas(), precision=EvidenceInterface("E00", "0 0 10 10", 0, 100, "", ""))
    except ValueError:
        return True
    return False


if __name__ == "__main__":
    main()
