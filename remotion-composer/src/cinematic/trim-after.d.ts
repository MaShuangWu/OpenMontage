import type { CinematicVideoScene } from "./types";

export function resolveSceneDurationFrames(
  scene: CinematicVideoScene,
  fps: number,
): number;

export function resolveTrimAfterFrames(
  scene: CinematicVideoScene,
  fps: number,
): number | undefined;
