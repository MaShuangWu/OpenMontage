from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from clipper_studio import server as clipper_server


@pytest.fixture
def client(tmp_path, monkeypatch):
    sources = tmp_path / "sources"
    exports = tmp_path / "exports"
    sources.mkdir()
    exports.mkdir()
    monkeypatch.setattr(clipper_server, "SOURCES_DIR", sources)
    monkeypatch.setattr(clipper_server, "EXPORTS_DIR", exports)
    with TestClient(clipper_server.create_app(), base_url="http://127.0.0.1:4760") as test_client:
        yield test_client


def _save_source(source_id: str, sources_dir: Path, duration: float = 20) -> Path:
    source = sources_dir / f"{source_id}.mp4"
    source.write_bytes(b"source video")
    (sources_dir / f"{source_id}.json").write_text(
        json.dumps({
            "source_id": source_id,
            "filename": "lecture.mp4",
            "extension": ".mp4",
            "duration_seconds": duration,
            "width": 1920,
            "height": 1080,
        }),
        encoding="utf-8",
    )
    return source


def test_upload_streams_source_and_lists_it(client, monkeypatch):
    monkeypatch.setattr(
        clipper_server,
        "_probe_video",
        lambda _path: {"duration_seconds": 82.4, "width": 1920, "height": 1080},
    )
    response = client.post(
        "/api/clipper/sources?filename=lecture.mp4",
        content=b"video bytes",
        headers={"Content-Type": "video/mp4"},
    )

    assert response.status_code == 200
    source = response.json()
    assert source["duration_seconds"] == 82.4
    assert source["media_url"].endswith("/media")
    listing = client.get("/api/clipper/sources").json()
    assert [item["source_id"] for item in listing] == [source["source_id"]]


def test_upload_rejects_unsupported_extensions(client):
    response = client.post(
        "/api/clipper/sources?filename=notes.txt",
        content=b"not a video",
    )

    assert response.status_code == 415


def test_export_validates_bounds_and_passes_portrait_request(client, monkeypatch, tmp_path):
    source_id = "a" * 32
    _save_source(source_id, tmp_path / "sources")
    calls = []

    class FakeTrimmer:
        def execute(self, inputs):
            calls.append(inputs)
            Path(inputs["output_path"]).write_bytes(b"exported mp4")
            return SimpleNamespace(success=True, error=None)

    monkeypatch.setattr(clipper_server, "VideoTrimmer", FakeTrimmer)
    invalid = client.post(
        "/api/clipper/exports",
        json={
            "source_id": source_id,
            "start_seconds": 1,
            "end_seconds": 21,
            "title": "Moment",
            "framing": "portrait",
        },
    )
    assert invalid.status_code == 422
    assert not calls

    response = client.post(
        "/api/clipper/exports",
        json={
            "source_id": source_id,
            "start_seconds": 1.5,
            "end_seconds": 8.5,
            "title": "Moment clé",
            "framing": "portrait",
        },
    )

    assert response.status_code == 200
    exported = response.json()
    assert calls[0]["aspect_ratio"] == "9:16"
    assert calls[0]["codec"] == "libx264"
    assert client.get(exported["media_url"]).content == b"exported mp4"
    assert client.get(exported["download_url"]).headers["content-disposition"].endswith(
        'filename="Moment-cl.mp4"'
    )


def test_export_rejects_malformed_source_id(client):
    response = client.post(
        "/api/clipper/exports",
        json={
            "source_id": "..",
            "start_seconds": 0,
            "end_seconds": 1,
            "title": "Clip",
        },
    )

    assert response.status_code == 422
