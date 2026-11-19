import json
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_video_scene_honors_hard_cut_tokens_and_backing_color() -> None:
    source = (REPO_ROOT / "remotion-composer/src/Explainer.tsx").read_text(
        encoding="utf-8"
    )

    assert '["cut", "none"].includes((transitionIn || "").toLowerCase())' in source
    assert '["cut", "none"].includes((transitionOut || "").toLowerCase())' in source
    assert "transitionIn={cut.transition_in}" in source
    assert "transitionOut={cut.transition_out}" in source
    assert "sceneDurationSeconds={cut.out_seconds - cut.in_seconds}" in source
    assert "Math.round(sceneDurationSeconds * fps)" in source
    assert "durationInFrames - transitionFrames" in source
    assert "backgroundColor={cut.backgroundColor}" in source


def test_cinematic_fades_are_bounded_by_each_scene_duration() -> None:
    source = (REPO_ROOT / "remotion-composer/src/CinematicRenderer.tsx").read_text(
        encoding="utf-8"
    )

    assert "const durationInFrames = resolveSceneDurationFrames(scene, fps);" in source
    assert "durationInFrames - fadeOutFrames" in source


def test_cinematic_trim_after_scales_source_interval_by_playback_rate() -> None:
    """Playback at either rate stops at the selected source-out boundary."""
    source = (REPO_ROOT / "remotion-composer/src/CinematicRenderer.tsx").read_text(
        encoding="utf-8"
    )
    assert "const trimAfter = resolveTrimAfterFrames(scene, fps);" in source
    assert "const durationInFrames = resolveSceneDurationFrames(scene, fps);" in source
    assert "trimAfter={trimAfter}" in source
    assert 'from "./cinematic/trim-after.js"' in source
    assert "resolveSceneDurationFrames(scene, FPS)" in source

    helper_path = REPO_ROOT / "remotion-composer/src/cinematic/trim-after.js"
    script = f"""
      const {{ resolveSceneDurationFrames, resolveTrimAfterFrames }} = require({json.dumps(str(helper_path))});
      const regions = [
        {{ name: "first", start: 0, end: 30 }},
        {{ name: "selected", start: 30, end: 60 }},
        {{ name: "after-trim", start: 60, end: 90 }},
      ];
      const results = [0.5, 2].map((playbackRate) => {{
        const scene = {{ durationSeconds: 6, trimBeforeSeconds: 0, trimAfterSeconds: 2, playbackRate }};
        const trimAfter = resolveTrimAfterFrames(scene, 30);
        const durationInFrames = resolveSceneDurationFrames(scene, 30);
        const visibleRegions = new Set();
        for (let timelineFrame = 0; timelineFrame < durationInFrames; timelineFrame++) {{
          const sourceFrame = Math.floor(timelineFrame * playbackRate);
          const region = regions.find(
            (candidate) => sourceFrame >= candidate.start && sourceFrame < candidate.end,
          );
          if (region) visibleRegions.add(region.name);
        }}
        return {{ playbackRate, trimAfter, durationInFrames, visibleRegions: [...visibleRegions] }};
      }});
      console.log(JSON.stringify(results));
    """
    result = subprocess.run(
        ["node", "-e", script],
        check=True,
        capture_output=True,
        cwd=REPO_ROOT,
        text=True,
    )

    assert json.loads(result.stdout) == [
        {
            "playbackRate": 0.5,
            "trimAfter": 120,
            "durationInFrames": 120,
            "visibleRegions": ["first", "selected"],
        },
        {
            "playbackRate": 2,
            "trimAfter": 30,
            "durationInFrames": 30,
            "visibleRegions": ["first", "selected"],
        },
    ]


def _jsx_block(source: str, component: str) -> str:
    """Return the JSX element text for <Component ... /> in the source."""
    start = source.index(f"<{component}")
    end = source.index("/>", start)
    return source[start:end]


def test_chart_scenes_receive_the_theme_text_color() -> None:
    """Charts default textColor to near-black (#1F2937).

    If Explainer does not forward the theme's textColor, every chart title,
    axis label, category label and value renders dark-on-dark and is invisible
    on any dark theme.
    """
    source = (REPO_ROOT / "remotion-composer/src/Explainer.tsx").read_text(
        encoding="utf-8"
    )

    for component in ("BarChart", "LineChart", "PieChart", "KPIGrid"):
        assert "textColor={textColor}" in _jsx_block(source, component), (
            f"{component} must receive the theme textColor, "
            f"or its labels are invisible on dark themes"
        )


def test_comparison_card_surface_follows_the_theme() -> None:
    """ComparisonCard hardcodes cardBackgroundColor to a light grey (#F3F4F6).

    On a dark theme it receives the theme's light textColor, so without a
    themed card surface the labels are light-on-light.
    """
    source = (REPO_ROOT / "remotion-composer/src/Explainer.tsx").read_text(
        encoding="utf-8"
    )
    block = _jsx_block(source, "ComparisonCard")

    assert "textColor={textColor}" in block
    assert "cardBackgroundColor={cut.cardBackgroundColor || theme.surfaceColor}" in block
