"""DashScope (Alibaba Cloud Bailian) video generation via Wan 3.0 (万相 3.0).

``wan3.0-video`` (standard) and ``wan3.0-video-prime`` (faster, pricier) share
one request shape covering text-to-video, first/last-frame image-to-video, and
reference-conditioned video (images, videos, audio). The
API is asynchronous: submit a task with ``X-DashScope-Async: enable``, poll
``/api/v1/tasks/{task_id}``, then download ``video_url`` (valid ~24h).

API reference:
https://help.aliyun.com/zh/model-studio/wan3-video-generation-api-reference
"""

from __future__ import annotations

import base64
import math
import mimetypes
import os
import re
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ResumeSupport,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

REGIONS = {
    "cn-beijing",
    "ap-southeast-1",
    "ap-northeast-1",
    "cn-hongkong",
    "eu-central-1",
    "us-east-1",
}
SUBMIT_PATH = "/api/v1/services/aigc/video-generation/video-synthesis"
TASK_PATH = "/api/v1/tasks/{task_id}"

MODELS = ["wan3.0-video", "wan3.0-video-prime"]
DEFAULT_MODEL = "wan3.0-video"

OPERATIONS = [
    "text_to_video",
    "image_to_video",
    "first_last_frame_to_video",
    "reference_to_video",
]
RESOLUTIONS = ["480P", "720P", "1080P"]
# The API defaults to 1080P (the most expensive tier); default to 720P so a
# caller who omits resolution does not silently pay double.
DEFAULT_RESOLUTION = "720P"
RATIOS = ["adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]
DEFAULT_DURATION = 5
MAX_DURATION = 30

# USD per output second at the Singapore list price, the most expensive region
# for both models, so the estimate is an upper bound everywhere. Singapore
# lists wan3.0-video in CNY (0.37471 / 0.74942 / 1.49884), converted at 7.2;
# Beijing bills 0.30 / 0.60 / 1.20 CNY (standard) and 0.45 / 0.90 / 1.80 CNY
# (prime).
USD_PER_SECOND = {
    "wan3.0-video": {"480P": 0.052, "720P": 0.104, "1080P": 0.208},
    "wan3.0-video-prime": {"480P": 0.068, "720P": 0.14, "1080P": 0.28},
}

MAX_REFERENCE_IMAGES = 10
MAX_REFERENCE_VIDEOS = 5
MAX_REFERENCE_AUDIO = 5

_IN_PROGRESS = {"PENDING", "RUNNING"}
_SUCCESS = "SUCCEEDED"
_FAILURES = {"FAILED", "CANCELED", "UNKNOWN"}


class DashscopeVideo(BaseTool):
    name = "dashscope_video"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "video_generation"
    provider = "dashscope"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API
    resume_support = ResumeSupport.FROM_CHECKPOINT

    dependencies = ["env:DASHSCOPE_API_KEY"]
    install_instructions = (
        "Set DASHSCOPE_API_KEY to your Alibaba Cloud DashScope API key.\n"
        "  Get one at https://dashscope.aliyun.com/\n"
        "  Set DASHSCOPE_WORKSPACE_ID and DASHSCOPE_REGION for Wan 3.0 "
        "(region defaults to cn-beijing), or set DASHSCOPE_BASE_URL to override the endpoint."
    )
    fallback = "minimax_video"
    fallback_tools = ["minimax_video", "seedance_video", "kling_video"]
    agent_skills = ["dashscope"]

    capabilities = OPERATIONS
    supports = {
        "text_to_video": True,
        "image_to_video": True,
        "first_last_frame_to_video": True,
        "reference_to_video": True,
        "reference_image": True,
        "reference_video": True,
        "reference_audio": True,
        "native_audio": True,
        "seed": True,
    }
    best_for = [
        "text, image, first/last-frame, and reference video with Wan 3.0",
        "faster turnaround with wan3.0-video-prime",
        "Chinese-language prompts and Mandarin dialogue with native audio",
        "clips up to 30 seconds at 480P/720P/1080P",
    ]
    not_good_for = ["offline generation", "clips longer than 30 seconds"]

    # Selector note: ``image_url`` is read but intentionally not declared here.
    # The video selector uploads ``reference_image_path`` to fal.ai for any
    # provider that declares ``image_url``; this tool inlines local files as
    # base64 instead, so no separate upload host is needed.
    input_schema = {
        "type": "object",
        "anyOf": [{"required": ["prompt"]}, {"required": ["resume_job"]}],
        "properties": {
            "prompt": {"type": "string", "maxLength": 20000},
            "operation": {
                "type": "string",
                "enum": [*OPERATIONS, "resume"],
                "default": "text_to_video",
            },
            "model": {
                "type": "string",
                "enum": MODELS,
                "default": DEFAULT_MODEL,
                "description": (
                    "wan3.0-video is the standard model; wan3.0-video-prime is "
                    "the faster variant at ~1.3-1.5x the per-second price."
                ),
            },
            "reference_image_url": {
                "type": "string",
                "description": (
                    "First frame for image_to_video, or one reference image for "
                    "reference_to_video. Public URL or data URI."
                ),
            },
            "reference_image_path": {
                "type": "string",
                "description": "Local file alternative to reference_image_url.",
            },
            "first_frame_image": {
                "type": "string",
                "description": "Alias for reference_image_url in frame operations.",
            },
            "last_image_url": {
                "type": "string",
                "description": "Final frame for first_last_frame_to_video.",
            },
            "last_image_path": {
                "type": "string",
                "description": "Local file alternative to last_image_url.",
            },
            "reference_image_urls": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": MAX_REFERENCE_IMAGES,
            },
            "reference_image_paths": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": MAX_REFERENCE_IMAGES,
            },
            "reference_video_url": {"type": "string"},
            "reference_video_path": {"type": "string"},
            "reference_video_urls": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": MAX_REFERENCE_VIDEOS,
            },
            "reference_video_paths": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": MAX_REFERENCE_VIDEOS,
            },
            "reference_audio_urls": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": MAX_REFERENCE_AUDIO,
            },
            "reference_audio_paths": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": MAX_REFERENCE_AUDIO,
            },
            "duration": {
                "type": "integer",
                "minimum": -1,
                "maximum": MAX_DURATION,
                "default": DEFAULT_DURATION,
                "description": (
                    "Output seconds, 2-30. -1 lets the model choose. With "
                    "reference videos, input + output seconds must not exceed 30."
                ),
            },
            "resolution": {
                "type": "string",
                "enum": RESOLUTIONS,
                "default": DEFAULT_RESOLUTION,
                "description": "Billed per second; 1080P costs ~2x 720P and ~4x 480P.",
            },
            "ratio": {
                "type": "string",
                "enum": RATIOS,
                "description": (
                    "Defaults to 16:9 for text_to_video and adaptive otherwise."
                ),
            },
            "aspect_ratio": {
                "type": "string",
                "enum": RATIOS,
                "description": "Selector-compatible alias for ratio.",
            },
            "audio": {
                "type": "boolean",
                "default": True,
                "description": "Generate a native audio track.",
            },
            "seed": {"type": "integer", "minimum": -1, "maximum": 2147483647},
            "prompt_extend": {
                "type": "boolean",
                "default": True,
                "description": "Let DashScope rewrite the prompt before generation.",
            },
            "watermark": {"type": "boolean", "default": False},
            "poll_interval_seconds": {
                "type": "number",
                "minimum": 0.1,
                "maximum": 60,
                "default": 15,
                "description": "Seconds between task-status requests.",
            },
            "timeout_seconds": {
                "type": "number",
                "minimum": 1,
                "maximum": 3600,
                "default": 1800,
                "description": (
                    "Maximum time to wait for remote generation. Timeout errors "
                    "include task_id; the task stays queryable for 24 hours."
                ),
            },
            "output_path": {"type": "string"},
            "resume_job": {
                "type": "object",
                "description": "Job metadata from a prior submission. Poll and download without submitting.",
            },
            "job_path": {
                "type": "string",
                "description": "Optional path to save accepted job metadata before polling.",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=512, vram_mb=0, disk_mb=500, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=0)
    idempotency_key_fields = [
        "prompt",
        "resume_job",
        "model",
        "operation",
        "reference_image_url",
        "reference_image_path",
        "first_frame_image",
        "last_image_url",
        "last_image_path",
        "reference_image_urls",
        "reference_image_paths",
        "reference_video_url",
        "reference_video_path",
        "reference_video_urls",
        "reference_video_paths",
        "reference_audio_urls",
        "reference_audio_paths",
        "duration",
        "resolution",
        "ratio",
        "aspect_ratio",
        "audio",
        "seed",
        "prompt_extend",
        "watermark",
    ]
    side_effects = [
        "writes video file to output_path",
        "calls DashScope (Alibaba Cloud) video generation API",
    ]
    user_visible_verification = [
        "Watch generated clip for motion coherence, prompt adherence, and audio sync"
    ]

    def get_status(self) -> ToolStatus:
        if not os.environ.get("DASHSCOPE_API_KEY"):
            return ToolStatus.UNAVAILABLE
        try:
            self._base_url()
        except ValueError:
            return ToolStatus.UNAVAILABLE
        return ToolStatus.AVAILABLE

    @staticmethod
    def _base_url() -> str:
        override = os.environ.get("DASHSCOPE_BASE_URL", "").strip()
        if override:
            return override.rstrip("/")
        workspace = os.environ.get("DASHSCOPE_WORKSPACE_ID", "").strip()
        if not re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", workspace):
            raise ValueError("Set DASHSCOPE_WORKSPACE_ID to a valid DashScope workspace ID.")
        region = os.environ.get("DASHSCOPE_REGION", "").strip().lower() or "cn-beijing"
        if region in ("intl", "international", "singapore"):
            region = "ap-southeast-1"
        if region not in REGIONS:
            raise ValueError(f"Unsupported DASHSCOPE_REGION. Choose from {', '.join(sorted(REGIONS))}.")
        return f"https://{workspace}.{region}.maas.aliyuncs.com"

    @staticmethod
    def _duration(inputs: dict[str, Any]) -> Any:
        duration = inputs.get("duration", DEFAULT_DURATION)
        if isinstance(duration, str) and duration.lstrip("-").isdigit():
            return int(duration)
        return duration

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        if "resume_job" in inputs or inputs.get("operation") == "resume":
            return 0.0  # No new generation charge.
        model = inputs.get("model", DEFAULT_MODEL)
        rates = USD_PER_SECOND.get(model, USD_PER_SECOND["wan3.0-video-prime"])
        resolution = inputs.get("resolution", DEFAULT_RESOLUTION)
        rate = rates.get(resolution, rates["1080P"])
        duration = self._duration(inputs)
        if isinstance(duration, bool) or not isinstance(duration, int) or duration < 1:
            # -1 lets the model pick a length; budget for the maximum.
            duration = MAX_DURATION
        return round(rate * duration, 2)

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 180.0

    @staticmethod
    def _to_media_url(value: str) -> str:
        """Pass URLs through; inline local files as base64 data URIs."""
        if value.startswith(("http://", "https://", "oss://", "data:")):
            return value
        path = Path(value).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Media file not found: {value}")
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{encoded}"

    @staticmethod
    def _collect(inputs: dict[str, Any], *keys: str) -> list[str]:
        values: list[str] = []
        for key in keys:
            value = inputs.get(key)
            if isinstance(value, (list, tuple)):
                values.extend(str(v) for v in value if v)
            elif value:
                values.append(str(value))
        return values

    def _build_payload(
        self, inputs: dict[str, Any]
    ) -> tuple[dict[str, Any] | None, str | None]:
        model = inputs.get("model", DEFAULT_MODEL)
        if model not in MODELS:
            return None, f"Unsupported DashScope video model '{model}'."

        operation = inputs.get("operation", "text_to_video")
        if operation not in OPERATIONS:
            return None, f"dashscope_video does not support operation '{operation}'."

        prompt = str(inputs.get("prompt") or "")
        if not prompt:
            return None, "dashscope_video requires 'prompt'."
        if len(prompt) > 20000:
            return None, "Wan 3.0 prompt must not exceed 20000 characters."

        first_frame = self._collect(
            inputs,
            "first_frame_image",
            "reference_image_url",
            "image_url",
            "reference_image_path",
        )[:1]
        last_frame = self._collect(inputs, "last_image_url", "last_image_path")[:1]

        media: list[tuple[str, str]] = []
        if operation in ("image_to_video", "first_last_frame_to_video"):
            if not first_frame:
                return None, f"{operation} requires 'reference_image_url' or 'reference_image_path'."
            media.append(("first_frame", first_frame[0]))
            if operation == "first_last_frame_to_video" and not last_frame:
                return None, "first_last_frame_to_video requires 'last_image_url' or 'last_image_path'."
            if last_frame:
                media.append(("last_frame", last_frame[0]))
        elif operation == "reference_to_video":
            images = self._collect(
                inputs,
                "reference_image_url",
                "image_url",
                "reference_image_path",
                "reference_image_urls",
                "reference_image_paths",
            )
            videos = self._collect(
                inputs,
                "reference_video_url",
                "reference_video_path",
                "reference_video_urls",
                "reference_video_paths",
            )
            audio = self._collect(inputs, "reference_audio_urls", "reference_audio_paths")
            if not images and not videos and not audio:
                return None, "reference_to_video requires at least one reference image, video, or audio."
            if len(images) > MAX_REFERENCE_IMAGES:
                return None, f"Wan 3.0 accepts at most {MAX_REFERENCE_IMAGES} reference images."
            if len(videos) > MAX_REFERENCE_VIDEOS:
                return None, f"Wan 3.0 accepts at most {MAX_REFERENCE_VIDEOS} reference videos."
            if len(audio) > MAX_REFERENCE_AUDIO:
                return None, f"Wan 3.0 accepts at most {MAX_REFERENCE_AUDIO} reference audio clips."
            media.extend(("reference_image", v) for v in images)
            media.extend(("reference_video", v) for v in videos)
            media.extend(("reference_audio", v) for v in audio)

        duration = self._duration(inputs)
        if (
            isinstance(duration, bool)
            or not isinstance(duration, int)
            or not (duration == -1 or 2 <= duration <= MAX_DURATION)
        ):
            return None, "Wan 3.0 duration must be -1 or an integer from 2 to 30 seconds."

        resolution = inputs.get("resolution", DEFAULT_RESOLUTION)
        if resolution not in RESOLUTIONS:
            return None, f"Wan 3.0 resolution must be one of {RESOLUTIONS}."

        ratio = inputs.get("ratio") or inputs.get("aspect_ratio")
        if not ratio:
            ratio = "16:9" if operation == "text_to_video" else "adaptive"
        if ratio not in RATIOS:
            return None, f"Unsupported Wan 3.0 ratio '{ratio}'."

        try:
            media_payload = [
                {"type": kind, "url": self._to_media_url(value)} for kind, value in media
            ]
        except (OSError, ValueError) as exc:
            return None, str(exc)

        payload_input: dict[str, Any] = {"prompt": prompt}
        if media_payload:
            payload_input["media"] = media_payload

        parameters: dict[str, Any] = {
            "resolution": resolution,
            "ratio": ratio,
            "duration": duration,
            "audio": bool(inputs.get("audio", True)),
            "prompt_extend": bool(inputs.get("prompt_extend", True)),
            "watermark": bool(inputs.get("watermark", False)),
        }
        if inputs.get("seed") is not None:
            parameters["seed"] = int(inputs["seed"])

        return {"model": model, "input": payload_input, "parameters": parameters}, None

    @staticmethod
    def _api_error(response: Any) -> str | None:
        """Return DashScope's code/message for a non-2xx response."""
        if response.ok:
            return None
        try:
            body = response.json() or {}
        except ValueError:
            body = {}
        code = body.get("code") or f"HTTP {response.status_code}"
        message = body.get("message") or response.text[:200]
        return f"{code}: {message}"

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        api_key = os.environ.get("DASHSCOPE_API_KEY")
        if not api_key:
            return ToolResult(
                success=False,
                error="DASHSCOPE_API_KEY not set. " + self.install_instructions,
            )

        import requests
        from tools.provider_jobs import save_job

        start = time.monotonic()
        job: dict[str, Any] = {}
        cost: float | None = None
        data: dict[str, Any] = {"provider": self.provider}
        submission_pending = False

        def failure(error: str, **extra: Any) -> ToolResult:
            return ToolResult(
                success=False,
                error=error.replace(api_key, "[redacted]"),
                data={**data, **extra},
                cost_usd=cost,
                model=data.get("model"),
            )

        def unknown_submission(error: str) -> ToolResult:
            return failure(
                f"{error} Task acceptance is unknown. Check DashScope for the original "
                "task ID before submitting again.",
                status="submission_unknown",
            )

        try:
            base_url = self._base_url()
            poll_interval = max(float(inputs.get("poll_interval_seconds", 15)), 0.1)
            timeout_seconds = max(float(inputs.get("timeout_seconds", 1800)), 1.0)
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data["endpoint"] = base_url

            if "resume_job" in inputs or inputs.get("operation") == "resume":
                candidate = inputs.get("resume_job")
                if (
                    not isinstance(candidate, dict)
                    or candidate.get("tool") != self.name
                    or candidate.get("endpoint") != base_url
                    or candidate.get("model") not in MODELS
                    or not isinstance(candidate.get("parameters"), dict)
                    or candidate["parameters"].get("resolution") not in RESOLUTIONS
                    or not isinstance(candidate.get("task_id"), str)
                    or not re.fullmatch(r"[A-Za-z0-9_-]+", candidate["task_id"])
                ):
                    return failure("Resume requires a valid resume_job for the configured endpoint.")
                job = candidate
            else:
                payload, validation_error = self._build_payload(inputs)
                if validation_error:
                    return failure(validation_error)
                assert payload is not None
                data.update(model=payload["model"], prompt=payload["input"]["prompt"])
                submission_pending = True
                submit = requests.post(
                    f"{base_url}{SUBMIT_PATH}",
                    headers={**headers, "X-DashScope-Async": "enable"},
                    json=payload,
                    timeout=60,
                    allow_redirects=False,
                )
                if api_error := self._api_error(submit):
                    if 400 <= submit.status_code < 500 and submit.status_code != 408:
                        return failure(f"DashScope video submit failed: {api_error}")
                    return unknown_submission(f"DashScope video submit failed: {api_error}.")
                if not 200 <= submit.status_code < 300:
                    return unknown_submission(f"Unexpected DashScope submit response: HTTP {submit.status_code}.")
                task_id = (submit.json().get("output") or {}).get("task_id")
                if not isinstance(task_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", task_id):
                    return unknown_submission("DashScope did not return a valid task_id.")
                job = {
                    "tool": self.name,
                    "task_id": task_id,
                    "endpoint": base_url,
                    "model": payload["model"],
                    "operation": inputs.get("operation", "text_to_video"),
                    "parameters": payload["parameters"],
                }
                submission_pending = False

            task_id = job["task_id"]
            parameters = job["parameters"]
            data.update(
                task_id=task_id,
                resume_job=job,
                model=job["model"],
                operation=job.get("operation"),
                parameters=parameters,
                resolution=parameters["resolution"],
                ratio=parameters.get("ratio"),
                audio=parameters.get("audio"),
            )
            save_job(inputs.get("job_path"), job)
            task_url = f"{base_url}{TASK_PATH.format(task_id=task_id)}"
            deadline = time.monotonic() + timeout_seconds
            while (remaining := deadline - time.monotonic()) > 0:
                status_resp = requests.get(task_url, headers=headers, timeout=min(30, remaining))
                if api_error := self._api_error(status_resp):
                    return failure(f"DashScope task query failed: {api_error}")
                body = status_resp.json()
                output = body.get("output") or {}
                status = output.get("task_status")
                if status == _SUCCESS:
                    break
                if status in _FAILURES:
                    reason = output.get("message") or output.get("code") or "unknown error"
                    return failure(f"DashScope video generation {status}: {reason}", status=status)
                if status not in _IN_PROGRESS:
                    return failure(f"DashScope returned unknown task status '{status}'.")
                time.sleep(min(poll_interval, max(deadline - time.monotonic(), 0)))
            else:
                return failure(
                    f"DashScope video generation timed out after {timeout_seconds:g}s. "
                    "Resume with the returned resume_job within 24 hours.",
                    status="timed_out",
                )

            usage = body.get("usage") or {}
            data.update(usage=usage, actual_prompt=output.get("actual_prompt") or output.get("orig_prompt"))
            if "prompt" not in data:
                data["prompt"] = output.get("orig_prompt")
            billed_seconds = usage.get("duration", usage.get("output_video_duration"))
            if (
                type(billed_seconds) in (int, float)
                and math.isfinite(billed_seconds)
                and billed_seconds > 0
            ):
                rate = USD_PER_SECOND[job["model"]][parameters["resolution"]]
                cost = round(rate * billed_seconds, 2)

            video_url = output.get("video_url")
            if not video_url:
                return failure("DashScope task succeeded without a video_url.")
            video = requests.get(video_url, timeout=300)
            video.raise_for_status()
            output_path = Path(inputs.get("output_path", "dashscope_video.mp4"))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(video.content)
        except Exception as exc:  # noqa: BLE001 - surface a redacted error to the caller
            if submission_pending:
                return unknown_submission(f"DashScope video submit failed: {exc}.")
            return failure(f"DashScope video generation failed: {exc}")

        return ToolResult(
            success=True,
            data={**data, "output": str(output_path)},
            artifacts=[str(output_path)],
            cost_usd=cost,
            duration_seconds=round(time.monotonic() - start, 2),
            model=job["model"],
        )
