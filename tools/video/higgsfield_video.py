"""Higgsfield video generation via Higgsfield Cloud API.

Calls https://api.higgsfield.ai with one endpoint per model. Only models with a
verified endpoint in _MODEL_ROUTES are executed; any other model fails before
a request is sent, so no spend can land on an unknown route.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

# Single source of truth for the default model. Referenced by both the input
# schema and every code path that reads `model`, so estimate_cost / estimate_runtime
# / execute can never silently diverge from the advertised default again.
_DEFAULT_MODEL = "seedance_2.0"

_API_BASE = "https://api.higgsfield.ai"

# Endpoint, limits and self-serve USD per output second, verified against
# POST /estimate/<path>/<operation> on 2026-11-16.
_MODEL_ROUTES: dict[str, dict[str, Any]] = {
    "seedance_2.0": {
        "path": "bytedance/seedance-2.0",
        "duration_range": (4, 15),
        "aspect_ratios": ("16:9", "4:3", "1:1", "3:4", "9:16", "21:9"),
        "usd_per_second": {"480p": 0.0804, "720p": 0.1735, "1080p": 0.4293, "4k": 0.8907},
        "default_resolution": "720p",
        "audio_param": "generate_audio",
    },
    "kling_3.0": {
        "path": "kling-video/v3.0/pro",
        "duration_range": (3, 15),
        "aspect_ratios": ("16:9", "9:16", "1:1"),
        "usd_per_second": {"1080p": 0.0962},
        "default_resolution": "1080p",
        "audio_param": "sound",
    },
}

_TERMINAL_FAILURES = {"failed", "nsfw", "canceled", "cancelled"}


class HiggsFieldVideo(BaseTool):
    name = "higgsfield_video"
    version = "0.2.0"
    tier = ToolTier.GENERATE
    capability = "video_generation"
    provider = "higgsfield"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = []
    install_instructions = (
        "Set HIGGSFIELD_API_KEY and HIGGSFIELD_API_SECRET for your Higgsfield Cloud credentials.\n"
        "  Get them at https://cloud.higgsfield.ai/api-keys\n"
        "  Alternatively, set HIGGSFIELD_KEY as a combined key:secret value."
    )
    agent_skills = ["seedance-2-0", "ai-video-gen"]

    capabilities = ["text_to_video", "image_to_video"]
    supports = {
        "text_to_video": True,
        "image_to_video": True,
        "character_consistency": True,
        "multi_model_routing": True,
        "native_audio": True,
        "cinematic_quality": True,
        "camera_direction": True,
        "lip_sync": True,
        "multi_shot": True,
    }
    best_for = [
        "preferred premium video gen on Higgsfield (Seedance 2.0 is the default model)",
        "cinematic trailers, teasers, and high-fidelity clips with native synchronized audio",
        "character-consistent video generation (Soul ID + Seedance 2.0 identity consistency)",
        "director-level camera control and multi-shot editing in a single generation",
        "lip-sync from quoted dialogue in prompts",
        "Seedance 2.0 and Kling 3.0 Pro through a single Higgsfield key",
    ]
    not_good_for = ["offline generation", "fine-grained model control", "budget projects without subscription"]
    fallback_tools = ["seedance_video", "seedance_replicate", "kling_video", "veo_video", "minimax_video"]
    quality_score = 0.9

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {"type": "string"},
            "operation": {
                "type": "string",
                "enum": ["text_to_video", "image_to_video"],
                "default": "text_to_video",
            },
            "model": {
                "type": "string",
                "enum": [
                    "seedance_2.0",
                    "seedance_2.0_fast",
                    "kling_3.0",
                    "veo_3.1",
                    "sora_2",
                    "wan_2.5",
                    "soul_cinema",
                ],
                "default": _DEFAULT_MODEL,
                "description": (
                    "Underlying model. Defaults to Seedance 2.0 (preferred premium) — see "
                    ".agents/skills/seedance-2-0/. Only seedance_2.0 and kling_3.0 have a "
                    "verified endpoint; other values are rejected before any request."
                ),
            },
            "duration": {
                "type": "string",
                "default": "5",
                "description": "Whole seconds: 4-15 for seedance_2.0, 3-15 for kling_3.0",
            },
            "aspect_ratio": {
                "type": "string",
                "enum": ["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"],
                "default": "16:9",
                "description": "text_to_video only; image_to_video follows the input image. kling_3.0 accepts 16:9, 9:16, 1:1.",
            },
            "resolution": {
                "type": "string",
                "enum": ["480p", "720p", "1080p", "4k"],
                "description": "seedance_2.0: 480p/720p/1080p/4k (default 720p). kling_3.0 is fixed at 1080p.",
            },
            "generate_audio": {
                "type": "boolean",
                "default": True,
                "description": "Native audio track. Set false for silent clips scored in post.",
            },
            "image_url": {"type": "string", "description": "Reference image URL for image_to_video"},
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=512, vram_mb=0, disk_mb=500, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["rate_limit", "timeout"])
    idempotency_key_fields = ["prompt", "model", "operation", "duration"]
    side_effects = ["writes video file to output_path", "calls Higgsfield Cloud API"]
    user_visible_verification = ["Watch generated clip for motion coherence and visual quality"]

    def _get_credentials(self) -> tuple[str, str] | None:
        """Return (api_key, api_secret) or None if not configured."""
        combined = os.environ.get("HIGGSFIELD_KEY")
        if combined and ":" in combined:
            key, secret = combined.split(":", 1)
            return key, secret
        key = os.environ.get("HIGGSFIELD_API_KEY")
        secret = os.environ.get("HIGGSFIELD_API_SECRET")
        if key and secret:
            return key, secret
        return None

    def get_status(self) -> ToolStatus:
        if self._get_credentials():
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def _resolution(self, route: dict[str, Any], inputs: dict[str, Any]) -> str:
        if len(route["usd_per_second"]) == 1:
            return route["default_resolution"]
        return inputs.get("resolution") or route["default_resolution"]

    def _build_request(self, inputs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Return (url, payload) or raise ValueError before any network call."""
        model = inputs.get("model", _DEFAULT_MODEL)
        route = _MODEL_ROUTES.get(model)
        if route is None:
            raise ValueError(
                f"model {model!r} has no verified Higgsfield endpoint; "
                f"supported: {sorted(_MODEL_ROUTES)}"
            )

        operation = inputs.get("operation", "text_to_video")
        if operation not in ("text_to_video", "image_to_video"):
            raise ValueError(f"unknown operation {operation!r}")

        duration = int(inputs.get("duration", "5"))
        lo, hi = route["duration_range"]
        if not lo <= duration <= hi:
            raise ValueError(f"{model} duration must be {lo}-{hi} s, got {duration}")

        resolution = self._resolution(route, inputs)
        if resolution not in route["usd_per_second"]:
            raise ValueError(
                f"{model} resolution must be one of {sorted(route['usd_per_second'])}, got {resolution!r}"
            )

        audio = bool(inputs.get("generate_audio", True))
        payload: dict[str, Any] = {"prompt": inputs["prompt"], "duration": duration}
        if route["audio_param"] == "sound":
            payload["sound"] = "on" if audio else "off"
        else:
            payload["generate_audio"] = audio
        if len(route["usd_per_second"]) > 1:
            payload["resolution"] = resolution

        if operation == "text_to_video":
            aspect = inputs.get("aspect_ratio", "16:9")
            if aspect not in route["aspect_ratios"]:
                raise ValueError(
                    f"{model} aspect_ratio must be one of {list(route['aspect_ratios'])}, got {aspect!r}"
                )
            payload["aspect_ratio"] = aspect
        else:
            if not inputs.get("image_url"):
                raise ValueError("image_to_video requires image_url")
            payload["image_url"] = inputs["image_url"]

        url = f"{_API_BASE}/{route['path']}/{operation.replace('_', '-')}"
        return url, payload

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        model = inputs.get("model", _DEFAULT_MODEL)
        route = _MODEL_ROUTES.get(model)
        if route is None:
            return 0.0
        rate = route["usd_per_second"].get(self._resolution(route, inputs), 0.0)
        return round(rate * int(inputs.get("duration", "5")), 4)

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        model = inputs.get("model", _DEFAULT_MODEL)
        if model in ("veo_3.1", "sora_2", "seedance_2.0"):
            return 120.0
        if model == "seedance_2.0_fast":
            return 60.0
        return 60.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        creds = self._get_credentials()
        if not creds:
            return ToolResult(
                success=False,
                error="Higgsfield credentials not set. " + self.install_instructions,
            )

        try:
            url, payload = self._build_request(inputs)
        except ValueError as e:
            return ToolResult(success=False, error=f"Higgsfield request rejected before submit: {e}")

        import requests

        api_key, api_secret = creds
        start = time.time()
        operation = inputs.get("operation", "text_to_video")
        model = inputs.get("model", _DEFAULT_MODEL)
        headers = {
            "Authorization": f"Key {api_key}:{api_secret}",
            "Content-Type": "application/json",
        }

        request_id = None
        try:
            submit_resp = requests.post(url, headers=headers, json=payload, timeout=30)
            submit_resp.raise_for_status()
            gen_data = submit_resp.json()
            request_id = gen_data["request_id"]
            status_url = gen_data.get("status_url") or f"{_API_BASE}/requests/{request_id}/status"

            video_url = None
            for _ in range(120):  # max ~10 minutes
                time.sleep(5)
                poll_resp = requests.get(status_url, headers=headers, timeout=15)
                poll_resp.raise_for_status()
                poll_data = poll_resp.json()
                status = str(poll_data.get("status", "")).lower()

                if status == "completed":
                    video_url = (poll_data.get("video") or {}).get("url")
                    break
                if status in _TERMINAL_FAILURES:
                    return ToolResult(
                        success=False,
                        error=f"Higgsfield generation {status} (request_id={request_id}): "
                        f"{poll_data.get('error', 'unknown')}",
                    )

            if not video_url:
                return ToolResult(
                    success=False,
                    error=f"Higgsfield generation timed out or returned no video.url (request_id={request_id}).",
                )

            video_response = requests.get(video_url, timeout=120)
            video_response.raise_for_status()

            output_path = Path(inputs.get("output_path", "higgsfield_output.mp4"))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(video_response.content)

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Higgsfield video generation failed (request_id={request_id}): {e}",
            )

        from tools.video._shared import probe_output

        probed = probe_output(output_path)
        return ToolResult(
            success=True,
            data={
                "provider": "higgsfield",
                "model": model,
                "prompt": inputs["prompt"],
                "operation": operation,
                "aspect_ratio": payload.get("aspect_ratio", "follows image"),
                "request_id": request_id,
                "output": str(output_path),
                "output_path": str(output_path),
                "format": "mp4",
                **probed,
            },
            artifacts=[str(output_path)],
            cost_usd=self.estimate_cost(inputs),
            duration_seconds=round(time.time() - start, 2),
            model=model,
        )
