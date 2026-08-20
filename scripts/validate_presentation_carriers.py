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
from moxing.core import (  # noqa: E402
    ChartArtwork,
    ChartPage,
    PRESENTATION_LINE_TRACES,
    PRESENTATION_LOCK_MODES,
    PRESENTATION_TARGETS,
    html_page,
)


def main() -> None:
    rendered = {chart_id: render_chart(chart_id) for chart_id in CHARTS}
    active = {
        chart_id: re.search(r'<main[^>]+data-presentation-carrier="([a-z]+)"', source).group(1)
        for chart_id, source in rendered.items()
    }
    targets = {
        chart_id: re.search(r'<main[^>]+data-presentation-target="([a-z]+)"', source).group(1)
        for chart_id, source in rendered.items()
    }
    lock_modes = {
        chart_id: re.search(r'<main[^>]+data-lock-mode="([a-z]+)"', source).group(1)
        for chart_id, source in rendered.items()
    }
    line_traces = {
        chart_id: re.search(r'<main[^>]+data-line-trace="(true|false)"', source).group(1) == "true"
        for chart_id, source in rendered.items()
    }
    interface_ids = {"C3", "C6", "C8", "C15", "C22"}
    direct_a_ids = {"C1", "C2", "C4", "C5", "C7", "C9", "C10", "C11", "C12", "C20"}
    embedded_b_ids = {"C13", "C14", "C16", "C17", "C18", "C19", "C21", "C23", "C24"}

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
        presentation=EmbeddedEvidence("E14", "<g></g>", "<g></g>", plot_svg="<g></g>", compiled_motion=True),
        presentation_target="embedded",
    )
    embedded_html = html_page(embedded_page)

    checks = {
        "all charts declare an active carrier": set(active) == set(CHARTS) and set(active.values()) <= {"direct", "embedded", "interface"},
        "all charts declare approved targets": targets == PRESENTATION_TARGETS,
        "all charts declare approved lock intensity": lock_modes == PRESENTATION_LOCK_MODES,
        "all charts declare approved line traces": line_traces == PRESENTATION_LINE_TRACES,
        "current rollout leaves only approved C charts on interface": {chart_id for chart_id, mode in active.items() if mode == "interface"} == interface_ids,
        "A group activates direct carrier": {chart_id for chart_id, mode in active.items() if mode == "direct"} == direct_a_ids,
        "B group activates embedded carrier": {chart_id for chart_id, mode in active.items() if mode == "embedded"} == embedded_b_ids,
        "interface markup remains compatible": all('data-interface="precision-v2.1"' in rendered[chart_id] and 'class="chart-body pi-split-body"' in rendered[chart_id] for chart_id in interface_ids),
        "C interface charts use four compiled macro layers": all('class="pi-data-field"' in rendered[chart_id] and 'class="pi-evidence-bay"' in rendered[chart_id] and 'class="pi-bay-terminal"' in rendered[chart_id] and ('class="pi-lock-ring"' in rendered[chart_id] or 'class="pi-focus-corner"' in rendered[chart_id]) for chart_id in interface_ids),
        "C interface charts keep one evidence identity": all(interface_identity_matches(chart_id, rendered[chart_id]) for chart_id in interface_ids),
        "C interface charts contain no embedded evidence capsule": all('class="pm-local-evidence"' not in rendered[chart_id] for chart_id in interface_ids),
        "direct markup has no split bay": all('<section class="chart-body pi-split-body">' not in rendered[chart_id] and 'class="chart-body pm-direct-body"' in rendered[chart_id] for chart_id in direct_a_ids),
        "A direct charts use two or three compiled macro layers": all('data-motion-system="presentation-v2.1"' in rendered[chart_id] and 'class="pm-data-field-layer"' in rendered[chart_id] and 'class="pm-plot-layer"' in rendered[chart_id] and (('class="pm-target-lock"' not in rendered[chart_id]) if lock_modes[chart_id] == "implicit" else ('class="pm-target-lock"' in rendered[chart_id])) for chart_id in direct_a_ids),
        "A direct charts contain no evidence container": all('evidence bay' not in rendered[chart_id] and 'class="evidence-plate"' not in rendered[chart_id] and 'class="pm-local-evidence"' not in rendered[chart_id] for chart_id in direct_a_ids),
        "embedded carrier renders full-width local evidence": 'class="chart-body pm-embedded-body"' in embedded_html and 'class="pm-local-evidence"' in embedded_html and '<section class="chart-body pi-split-body">' not in embedded_html,
        "embedded positional lock delay remains compatible": EmbeddedEvidence("E14", "", "", 740).lock_delay == 740,
        "B embedded charts use three or four compiled macro layers": all('data-motion-system="presentation-v2.1"' in rendered[chart_id] and 'class="pm-data-field-layer"' in rendered[chart_id] and 'class="pm-plot-layer"' in rendered[chart_id] and 'class="pm-local-evidence"' in rendered[chart_id] and (('class="pm-target-lock"' not in rendered[chart_id]) if lock_modes[chart_id] == "implicit" else ('class="pm-target-lock"' in rendered[chart_id])) for chart_id in embedded_b_ids),
        "B embedded charts contain no detached evidence plate": all('class="pi-evidence-bay"' not in rendered[chart_id] and 'class="evidence-plate"' not in rendered[chart_id] for chart_id in embedded_b_ids),
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


def interface_identity_matches(chart_id: str, source: str) -> bool:
    evidence_id = f"E{int(chart_id[1:]):02d}"
    return (
        f'aria-label="{evidence_id} evidence bay"' in source
        and f'<span>{evidence_id}</span>' in source
        and source.count(f'>{evidence_id}<') >= 2
        and f'>{evidence_id} / ' in source
    )


if __name__ == "__main__":
    main()
