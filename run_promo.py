#!/usr/bin/env python3
"""Kawaii app promos (docs/kawaii_ai_video_pipeline_prd.md).

  python run_promo.py capture  --app stories [--story ch01_morning_walk] [--target zh]
  python run_promo.py assemble --manifest projects/promo_inbox/<clip>.json [--platforms youtube,meta,tiktok] [--dry-run]
  python run_promo.py run      --app stories [--story ...] [--platforms ...] [--dry-run]   # capture + assemble
  python run_promo.py apps                                                                   # registry status

Apps, templates, approved claims and made-for-kids flags: autopilot/promo/apps.yaml.
Assembly uses the LLM router for copy when reachable, else the app's fallback copy.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import tools.base_tool  # noqa: E402,F401  (loads .env)

INBOX = ROOT / "projects" / "promo_inbox"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("capture", "run"):
        p = sub.add_parser(name)
        p.add_argument("--app", required=True)
        p.add_argument("--story")
        p.add_argument("--target", help="learning language (zh|en|ja)")
        p.add_argument("--ui", help="interface language (en|vi|zh_CN|ja)")
        p.add_argument("--hold", type=float, help="seconds to hold on the cliffhanger screen")
    asm = sub.add_parser("assemble")
    asm.add_argument("--manifest", required=True, type=Path)
    for p in (sub.choices["run"], asm):
        p.add_argument("--platforms", default="")
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--voice", help="Piper voice for the parent voiceover")
        p.add_argument("--no-llm", action="store_true", help="use the app's fallback copy")
    sub.add_parser("apps")
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    from autopilot.promo import app_config, load_registry

    if args.cmd == "apps":
        for app_id, a in load_registry()["apps"].items():
            print(f"{app_id:<8} {a.get('status', '?'):<6} {a['template']:<18} {a['display_name']}")
        return 0

    manifest = getattr(args, "manifest", None)
    try:
        if args.cmd in ("capture", "run"):
            from autopilot.promo.capture import capture
            registry = load_registry()
            app = app_config(args.app, registry)
            manifest = capture(app, registry, INBOX, {"story": args.story, "target": args.target,
                                                      "ui": args.ui, "hold": args.hold})
            print(f"Manifest: {manifest}")
            if args.cmd == "capture":
                return 0
        from autopilot.promo.assemble import assemble
        from autopilot.publishers import parse_platforms
        result = assemble(Path(manifest), parse_platforms(args.platforms), dry_run=args.dry_run,
                          voice=args.voice, use_llm=not args.no_llm)
    except Exception as exc:
        logging.error("Promo failed: %s", exc)
        return 1
    print(json.dumps({k: v for k, v in result.items() if k != "qa"}, indent=2, default=str))
    return 0 if result["status"] in {"published", "rendered"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
