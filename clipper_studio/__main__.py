"""Start the local OpenMontage Clip Studio."""

from __future__ import annotations

import argparse
import threading
import webbrowser


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=4760)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if not args.no_browser:
        threading.Timer(0.8, webbrowser.open, (f"http://127.0.0.1:{args.port}/",)).start()

    import uvicorn

    uvicorn.run("clipper_studio.server:app", host="127.0.0.1", port=args.port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
