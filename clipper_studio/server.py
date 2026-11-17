"""Local-first video clipping UI and API."""

from __future__ import annotations

import asyncio
import json
import math
import os
import re
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from tools.video.video_trimmer import VideoTrimmer


REPO_ROOT = Path(__file__).resolve().parent.parent
CLIPPER_DIR = Path(
    os.environ.get("OPENMONTAGE_CLIPPER_DIR")
    or REPO_ROOT / ".backlot" / "clipper-studio"
)
SOURCES_DIR = CLIPPER_DIR / "sources"
EXPORTS_DIR = CLIPPER_DIR / "exports"
UI_DIR = Path(__file__).resolve().parent / "ui"
SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
MAX_UPLOAD_BYTES = 8 * 1024**3
SOURCE_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")


class ExportClipRequest(BaseModel):
    source_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(gt=0)
    title: str = Field(default="Clip", min_length=1, max_length=100)
    framing: Literal["source", "portrait"] = "source"


def _probe_video(path: Path) -> dict:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("ffprobe is unavailable; install FFmpeg and restart the clipper.")
    result = subprocess.run(
        [
            ffprobe, "-v", "error", "-show_entries",
            "format=duration:stream=codec_type,width,height", "-of", "json", str(path),
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode:
        raise ValueError("FFprobe could not read this video file.")
    data = json.loads(result.stdout)
    video_stream = next(
        (stream for stream in data.get("streams", []) if stream.get("codec_type") == "video"),
        None,
    )
    duration = float((data.get("format") or {}).get("duration", 0))
    if (
        video_stream is None
        or not math.isfinite(duration)
        or duration <= 0
        or not video_stream.get("width")
        or not video_stream.get("height")
    ):
        raise ValueError("This file does not contain a readable video stream.")
    return {
        "duration_seconds": duration,
        "width": int(video_stream["width"]),
        "height": int(video_stream["height"]),
    }


def _metadata_path(source_id: str) -> Path:
    return SOURCES_DIR / f"{source_id}.json"


def _source_path(source_id: str, suffix: str) -> Path:
    return SOURCES_DIR / f"{source_id}{suffix}"


def _source_record(metadata: dict) -> dict:
    return {
        **metadata,
        "media_url": f"/api/clipper/sources/{metadata['source_id']}/media",
    }


def _load_source(source_id: str) -> tuple[dict, Path]:
    if not SOURCE_ID_PATTERN.fullmatch(source_id):
        raise HTTPException(status_code=404, detail="Source video not found.")
    try:
        metadata = json.loads(_metadata_path(source_id).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise HTTPException(status_code=404, detail="Source video not found.")
    extension = metadata.get("extension")
    if metadata.get("source_id") != source_id or extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=404, detail="Source video not found.")
    path = _source_path(source_id, extension)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Source video not found.")
    return metadata, path


def _resolve_export(export_id: str) -> tuple[dict, Path]:
    if not SOURCE_ID_PATTERN.fullmatch(export_id):
        raise HTTPException(status_code=404, detail="Export not found.")
    try:
        metadata = json.loads((EXPORTS_DIR / f"{export_id}.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise HTTPException(status_code=404, detail="Export not found.")
    if metadata.get("export_id") != export_id:
        raise HTTPException(status_code=404, detail="Export not found.")
    path = EXPORTS_DIR / f"{export_id}.mp4"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Export not found.")
    return metadata, path


def _filename_slug(title: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", title.strip()).strip("-_")
    return slug[:72] or "clip"


def _write_json(path: Path, data: dict) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def create_app() -> FastAPI:
    app = FastAPI(title="OpenMontage Clip Studio", docs_url=None, redoc_url=None)

    @app.get("/api/health")
    async def health() -> dict:
        return {"ok": True, "app": "clip-studio"}

    @app.get("/api/clipper/sources")
    async def list_sources() -> list[dict]:
        SOURCES_DIR.mkdir(parents=True, exist_ok=True)
        records = []
        for path in SOURCES_DIR.glob("*.json"):
            try:
                metadata = json.loads(path.read_text(encoding="utf-8"))
                source_id = metadata["source_id"]
                extension = metadata["extension"]
                if (
                    not SOURCE_ID_PATTERN.fullmatch(source_id)
                    or extension not in SUPPORTED_EXTENSIONS
                ):
                    continue
                source = _source_path(source_id, extension)
                if source.is_file():
                    records.append(_source_record(metadata))
            except (OSError, KeyError, TypeError, json.JSONDecodeError):
                continue
        return sorted(records, key=lambda item: item.get("uploaded_at", ""), reverse=True)

    @app.post("/api/clipper/sources")
    async def upload_source(
        request: Request,
        filename: str = Query(..., min_length=1, max_length=255),
    ) -> dict:
        clean_name = Path(filename.replace("\\", "/")).name
        extension = Path(clean_name).suffix.lower()
        if not clean_name or extension not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail="Choose a video in MP4, MOV, MKV, WebM, or M4V format.",
            )
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="Video exceeds the 8 GiB upload limit.")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid Content-Length.")

        source_id = uuid.uuid4().hex
        SOURCES_DIR.mkdir(parents=True, exist_ok=True)
        temporary_path = SOURCES_DIR / f"{source_id}.upload"
        source_path = _source_path(source_id, extension)
        size = 0
        try:
            with temporary_path.open("wb") as target:
                async for chunk in request.stream():
                    size += len(chunk)
                    if size > MAX_UPLOAD_BYTES:
                        raise HTTPException(
                            status_code=413, detail="Video exceeds the 8 GiB upload limit."
                        )
                    target.write(chunk)
            if size == 0:
                raise HTTPException(status_code=400, detail="The uploaded file is empty.")
            temporary_path.replace(source_path)
            video_info = await asyncio.to_thread(_probe_video, source_path)
        except HTTPException:
            temporary_path.unlink(missing_ok=True)
            source_path.unlink(missing_ok=True)
            raise
        except RuntimeError as exc:
            temporary_path.unlink(missing_ok=True)
            source_path.unlink(missing_ok=True)
            raise HTTPException(status_code=503, detail=str(exc))
        except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
            temporary_path.unlink(missing_ok=True)
            source_path.unlink(missing_ok=True)
            raise HTTPException(status_code=422, detail=str(exc))

        metadata = {
            "source_id": source_id,
            "filename": clean_name,
            "extension": extension,
            "size_bytes": size,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            **video_info,
        }
        _write_json(_metadata_path(source_id), metadata)
        return _source_record(metadata)

    @app.get("/api/clipper/sources/{source_id}/media")
    async def source_media(source_id: str) -> FileResponse:
        metadata, path = _load_source(source_id)
        media_types = {
            ".m4v": "video/mp4",
            ".mkv": "video/x-matroska",
            ".mov": "video/quicktime",
            ".mp4": "video/mp4",
            ".webm": "video/webm",
        }
        return FileResponse(path, media_type=media_types[metadata["extension"]])

    @app.post("/api/clipper/exports")
    async def export_clip(payload: ExportClipRequest) -> dict:
        metadata, source_path = _load_source(payload.source_id)
        if (
            not math.isfinite(payload.start_seconds)
            or not math.isfinite(payload.end_seconds)
            or payload.end_seconds <= payload.start_seconds
        ):
            raise HTTPException(status_code=422, detail="End time must be after start time.")
        if payload.end_seconds > metadata["duration_seconds"]:
            raise HTTPException(
                status_code=422,
                detail="End time is beyond the duration of the source video.",
            )

        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        export_id = uuid.uuid4().hex
        output_path = EXPORTS_DIR / f"{export_id}.mp4"
        framing = "9:16" if payload.framing == "portrait" else "source"
        result = await asyncio.to_thread(
            VideoTrimmer().execute,
            {
                "operation": "cut",
                "input_path": str(source_path),
                "output_path": str(output_path),
                "start_seconds": payload.start_seconds,
                "end_seconds": payload.end_seconds,
                "codec": "libx264",
                "aspect_ratio": framing,
            },
        )
        if not result.success or not output_path.is_file():
            output_path.unlink(missing_ok=True)
            error = result.error if not result.success else "FFmpeg did not create an output file."
            raise HTTPException(status_code=500, detail=error)

        record = {
            "export_id": export_id,
            "source_id": payload.source_id,
            "source_filename": metadata["filename"],
            "title": payload.title.strip() or "Clip",
            "download_filename": f"{_filename_slug(payload.title)}.mp4",
            "start_seconds": payload.start_seconds,
            "end_seconds": payload.end_seconds,
            "framing": payload.framing,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "saved_to": str(output_path),
        }
        _write_json(EXPORTS_DIR / f"{export_id}.json", record)
        return {
            **record,
            "media_url": f"/api/clipper/exports/{export_id}/media",
            "download_url": f"/api/clipper/exports/{export_id}",
        }

    @app.get("/api/clipper/exports")
    async def list_exports() -> list[dict]:
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        records = []
        for path in EXPORTS_DIR.glob("*.json"):
            try:
                metadata = json.loads(path.read_text(encoding="utf-8"))
                export_id = metadata["export_id"]
                if (
                    SOURCE_ID_PATTERN.fullmatch(export_id)
                    and (EXPORTS_DIR / f"{export_id}.mp4").is_file()
                ):
                    records.append({
                        **metadata,
                        "media_url": f"/api/clipper/exports/{export_id}/media",
                        "download_url": f"/api/clipper/exports/{export_id}",
                    })
            except (OSError, KeyError, TypeError, json.JSONDecodeError):
                continue
        return sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)

    @app.get("/api/clipper/exports/{export_id}/media")
    async def export_media(export_id: str) -> FileResponse:
        _metadata, path = _resolve_export(export_id)
        return FileResponse(path, media_type="video/mp4")

    @app.get("/api/clipper/exports/{export_id}")
    async def download_export(export_id: str) -> FileResponse:
        metadata, path = _resolve_export(export_id)
        return FileResponse(
            path,
            media_type="video/mp4",
            filename=Path(metadata["download_filename"]).name,
        )

    @app.get("/")
    async def home() -> HTMLResponse:
        html = (UI_DIR / "index.html").read_text(encoding="utf-8")
        return HTMLResponse(html)

    app.mount("/static", StaticFiles(directory=UI_DIR), name="static")
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["127.0.0.1", "localhost"],
        www_redirect=False,
    )
    return app


app = create_app()
