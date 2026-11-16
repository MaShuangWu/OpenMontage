"""Stage 2: inbox manifest -> 9:16 promo reel (Remotion) -> QA -> metadata -> publish.

Templates are functions ``(ctx) -> Timeline``. Only ``story_cliffhanger`` exists so far;
the other PRD templates register here as their PromoBots are built.

story_cliffhanger (parent-directed):
  [hook card: cover art + big hook text + parent voiceover]
  [gameplay with the app's own narration, up to the choice screen]
  [end card: app name + store CTA + voiceover "Where will Bun go next?..."]
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from autopilot import metadata as meta_mod, narration, qa, render
from autopilot.db import RunLog
from autopilot.media_utils import run as run_cmd
from autopilot.pipeline import _save, finish_status, publish_all

log = logging.getLogger("autopilot.promo")

COPY_SYSTEM = (
    "You write short promo copy for a children's educational app. The audience is PARENTS, "
    "never children: address the parent ('your child', 'your kid'). Use ONLY the approved "
    "claims given; do not invent statistics, percentages, awards, prices, 'free', 'best', "
    "'#1', or outcomes like 'fluent'. Copy is read aloud by a text-to-speech voice: plain "
    "words, no emojis, no hashtags. Reply with JSON only."
)


@dataclass
class Timeline:
    cuts: list[dict[str, Any]]
    overlays: list[dict[str, Any]]
    voice: list[tuple[Path, float]]          # (wav, start seconds)
    game_audio: Optional[tuple[Path, float]]  # (clip, start seconds)
    captions: list[dict[str, Any]]
    total: float
    copy: dict[str, str] = field(default_factory=dict)


def _fmt(text: str, values: dict[str, str]) -> str:
    return text.format(**values) if "{" in text else text


def story_context(app: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    params = manifest.get("capture_params", {})
    story_id = params.get("story", "")
    data = json.loads((Path(app["path"]) / "data" / "stories" / f"{story_id}.json").read_text(encoding="utf-8"))
    who = next((l.get("who") for s in data["scenes"] for l in s.get("lines", [])
                if l.get("who") and l.get("who") != "narrator"), "")
    choice = next((s["choice"] for s in data["scenes"] if s.get("choice")), None)
    target = params.get("target", "zh")
    title = data["title"]["en"] if isinstance(data["title"], dict) else str(data["title"])
    blurb = data["blurb"]["en"] if isinstance(data.get("blurb"), dict) else str(data.get("blurb", ""))
    cover = Path(app["path"]) / "assets" / "ui" / f"{data['cover']}.jpg"
    return {
        "story_id": story_id, "title": title, "blurb": blurb, "hero": who.title() if who else "our hero",
        "language": app.get("language_names", {}).get(target, target),
        "choice_prompt": (choice or {}).get("prompt", {}).get("en", "") if choice else "",
        "cover": cover if cover.is_file() else None,
    }


def make_copy(app: dict[str, Any], ctx: dict[str, Any], chat_meta: Optional[Callable],
              on_llm_call: Optional[Callable[[dict], None]] = None) -> tuple[dict[str, str], str]:
    values = {"language": ctx["language"], "hero": ctx["hero"]}
    claims = [_fmt(c, values) for c in app.get("approved_claims", [])]
    fallback = {k: _fmt(v, values) for k, v in app.get("fallback_copy", {}).items()}
    if chat_meta is None:
        return fallback, "fallback (no LLM)"
    user = f"""App: {app['display_name']} ({app.get('audience', 'parents')})
Approved claims:
{chr(10).join('- ' + c for c in claims)}
The video shows the story "{ctx['title']}" ({ctx['blurb']}) being read aloud in {ctx['language']},
and stops on a choice: "{ctx['choice_prompt']}".

Return JSON:
{{"hook": "spoken opening line to parents, max 12 words",
  "hook_overlay": "on-screen hook text, max 6 words",
  "outro": "spoken closing line: tease the choice and name {app['display_name']}, max 16 words"}}"""
    try:
        data, meta = chat_meta([{"role": "system", "content": COPY_SYSTEM}, {"role": "user", "content": user}],
                               json_mode=True, max_tokens=400)
        if on_llm_call:
            on_llm_call(meta)
        out = {k: " ".join(str(data.get(k, "")).split()) for k in ("hook", "hook_overlay", "outro")}
        limits = {"hook": 14, "hook_overlay": 7, "outro": 18}
        banned = re.compile(r"\d+\s*%|\bfree\b|\bbest\b|#1|\bfluent", re.I)
        for k, n in limits.items():
            if not out[k] or len(out[k].split()) > n or banned.search(out[k]):
                raise ValueError(f"{k!r} rejected: {out[k]!r}")
        if app["display_name"].lower() not in out["outro"].lower():
            raise ValueError("outro does not name the app")
        return out, f"llm ({meta.get('provider')})"
    except Exception as exc:
        log.warning("LLM copy unusable (%s); using fallback copy", exc)
        return fallback, "fallback"


def _no_llm(*_a, **_k):
    raise RuntimeError("LLM disabled")


def _vo(text: str, out_dir: Path, voice: Optional[str]) -> tuple[Path, list[dict], float]:
    scene = type("VO", (), {"id": out_dir.name, "narration": text})()
    wav, parts = narration.synthesize([scene], out_dir, voice=voice)
    return wav, parts[0].words, parts[0].end


def _shift(words: list[dict], seconds: float) -> list[dict]:
    ms = int(round(seconds * 1000))
    return [dict(w, startMs=w["startMs"] + ms, endMs=w["endMs"] + ms) for w in words]


def story_cliffhanger(app, manifest, ctx, copy, audio_dir: Path, voice: Optional[str]) -> Timeline:
    hook_wav, hook_words, hook_d = _vo(copy["hook"], audio_dir / "vo_hook", voice)
    out_wav, out_words, out_d = _vo(copy["outro"], audio_dir / "vo_outro", voice)
    lead = 0.3
    intro = max(2.8, lead + hook_d + 0.5)
    clip_d = float(manifest["duration_sec"])
    outro_start = intro + clip_d
    total = outro_start + max(3.5, 0.4 + out_d + 1.2)
    choice_t = next((e["t"] for e in manifest["events"] if e["type"] == "choice"), None)
    stores = " & ".join(app.get("stores", [])) or "your app store"
    cta = app.get("cta") or f"On the {stores}"
    cover = str(ctx["cover"]) if ctx["cover"] else None
    end_card = Path(app.get("path", ".")) / app["end_card"] if app.get("end_card") else None
    end_cut: dict[str, Any] = (
        {"id": "endcard", "source": str(end_card), "animation": "zoom-out"}
        if end_card and end_card.is_file() else
        {"id": "endcard", "type": "hero_title", "source": "", "text": app["display_name"], "heroSubtitle": cta,
         **({"backgroundImage": cover, "backgroundOverlay": 0.1} if cover else {})})

    cuts = [
        ({"id": "hook", "source": cover, "in_seconds": 0, "out_seconds": round(intro, 3), "animation": "zoom-in"}
         if cover else {"id": "hook", "type": "text_card", "source": "", "text": copy["hook_overlay"],
                        "in_seconds": 0, "out_seconds": round(intro, 3)}),
        {"id": "gameplay", "source": manifest["clip_path"], "in_seconds": round(intro, 3),
         "out_seconds": round(outro_start, 3), "transition_in": "fade", "transition_out": "cut",
         "transition_duration": 0.25},
        {**end_cut, "in_seconds": round(outro_start, 3), "out_seconds": round(total, 3)},
    ]
    # No overlays: the stock hero/section titles are sized for 16:9 and wash out the art in 9:16.
    # The hook voiceover's captions carry the hook text, and the app's own choice screen
    # already asks the cliffhanger question.
    overlays: list[dict[str, Any]] = []
    captions = _shift(hook_words, lead) + _shift(out_words, outro_start + 0.4)
    return Timeline(cuts, overlays, [(hook_wav, lead), (out_wav, outro_start + 0.4)],
                    (Path(manifest["clip_path"]), intro), captions, total, copy)


TEMPLATES = {"story_cliffhanger": story_cliffhanger}


def mix_audio(tl: Timeline, out_path: Path) -> Path:
    inputs: list[str] = []
    chains: list[str] = []
    sources = [(p, s) for p, s in tl.voice] + ([tl.game_audio] if tl.game_audio else [])
    for i, (path, start) in enumerate(sources):
        inputs += ["-i", str(path)]
        ms = int(round(start * 1000))
        chains.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[a{i}]")
    labels = "".join(f"[a{i}]" for i in range(len(sources)))
    graph = (";".join(chains) + f";{labels}amix=inputs={len(sources)}:normalize=0:duration=longest,"
             f"apad,atrim=0:{tl.total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run_cmd(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph, "-map", "[out]",
             "-ar", "48000", "-c:a", "pcm_s16le", "-t", f"{tl.total:.3f}", str(out_path)])
    return out_path


def assemble(manifest_path: Path, platforms: list[str], dry_run: bool = False, voice: Optional[str] = None,
             use_llm: bool = True) -> dict[str, Any]:
    from autopilot.promo import app_config, load_registry
    from lib.checkpoint import init_project

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    registry = load_registry()
    app = app_config(manifest["app_id"], registry)
    template = TEMPLATES.get(manifest["template"])
    if template is None:
        raise NotImplementedError(f"template {manifest['template']!r} is not built yet")
    chat_meta = None
    if use_llm:
        from lib.llm_client import chat_meta

    ctx = story_context(app, manifest)
    project_id = f"promo-{app['id']}-{ctx['story_id'] or 'demo'}-{time.strftime('%Y%m%d-%H%M%S')}".replace("_", "-")
    pdir = init_project(project_id, title=f"{app['display_name']} promo", pipeline_type="promo", series="kawaii-promos")
    artifacts = pdir / "artifacts"
    db = RunLog()
    run_id = db.start_run(project_id, f"{app['display_name']}: {ctx['title']}", manifest["template"], "9:16",
                          manifest["duration_sec"])
    out: dict[str, Any] = {"run_id": run_id, "project_dir": str(pdir), "status": "failed"}
    try:
        copy, source = make_copy(app, ctx, chat_meta, on_llm_call=lambda m: db.llm_call(run_id, "promo_copy", m))
        log.info("Copy (%s): %s", source, copy)
        tl = template(app, manifest, ctx, copy, pdir / "assets" / "audio", voice)
        mixed = mix_audio(tl, pdir / "assets" / "audio" / "final_mix.wav")
        props = {
            "renderer_family": "explainer-data", "themeConfig": app.get("theme", {}), "tailPaddingSeconds": 0,
            "cuts": tl.cuts, "overlays": tl.overlays, "captions": tl.captions,
            "captionStyle": {"wordsPerPage": 3, "fontSize": 76, "bottomOffset": 520},
            "audio": {"narration": {"src": str(mixed), "volume": 1.0}},
        }
        _save(artifacts / "promo_plan.json", {"manifest": manifest, "copy": copy, "copy_source": source,
                                             "context": {k: str(v) for k, v in ctx.items()}})
        _save(artifacts / "render_props.json", props)
        video = render.render(props, pdir / "renders" / "final.mp4", "9:16")
        report = qa.check(video, tuple(registry.get("size", [1080, 1920])))
        _save(artifacts / "qa_report.json", report)
        db.update_run(run_id, video_path=str(video), video_seconds=report.get("duration"))
        out.update(video=str(video), qa=report)
        if not report["passed"]:
            raise RuntimeError("QA failed: " + "; ".join(report["issues"]))

        script = f"{copy['hook']} {app['display_name']}: {ctx['title']}. {ctx['blurb']} {copy['outro']}"
        md = meta_mod.generate(f"{ctx['title']} | {app['display_name']}", script, "9:16", report["duration"],
                               chat_meta or _no_llm, on_llm_call=lambda m: db.llm_call(run_id, "metadata", m))
        md["youtube"]["made_for_kids"] = bool(app.get("made_for_kids", False))
        _save(artifacts / "publish_metadata.json", md)

        if dry_run or not platforms:
            out["status"] = "rendered"
            db.update_run(run_id, status="rendered")
            return out
        posts = publish_all(db, run_id, platforms, video, md, "9:16", report["duration"], artifacts)
        out["posts"] = [p.__dict__ for p in posts]
        out["status"] = finish_status(db, run_id, posts)
        return out
    except Exception as exc:
        db.update_run(run_id, status="failed", error=str(exc)[:2000])
        raise
    finally:
        db.close()
