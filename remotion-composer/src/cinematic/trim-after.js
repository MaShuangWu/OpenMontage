/**
 * Scale the source interval into timeline frames for Remotion's trimAfter.
 * Its internal Sequence bounds trimAfter - trimBefore in timeline frames
 * without scaling by playbackRate, so the bound must account for the rate.
 */
function resolveTrimAfterFrames(scene, fps) {
  if (scene.trimAfterSeconds === undefined) {
    return undefined;
  }

  const playbackRate =
    scene.playbackRate && scene.playbackRate > 0 ? scene.playbackRate : 1;
  const trimBeforeSeconds = scene.trimBeforeSeconds ?? 0;
  const sourceIntervalFrames = Math.round(
    (scene.trimAfterSeconds - trimBeforeSeconds) * fps,
  );

  return (
    Math.round(trimBeforeSeconds * fps) +
    Math.round(sourceIntervalFrames / playbackRate)
  );
}

/**
 * Bound a video scene by its requested duration and selected source interval.
 * Remotion's trim Sequence is rate-blind, so convert the source interval to
 * timeline frames before using it to limit the parent scene Sequence.
 */
function resolveSceneDurationFrames(scene, fps) {
  const requestedFrames = Math.max(1, Math.round(scene.durationSeconds * fps));
  if (scene.trimAfterSeconds === undefined) {
    return requestedFrames;
  }

  const playbackRate =
    scene.playbackRate && scene.playbackRate > 0 ? scene.playbackRate : 1;
  const trimBeforeSeconds = scene.trimBeforeSeconds ?? 0;
  const sourceIntervalFrames = Math.round(
    (scene.trimAfterSeconds - trimBeforeSeconds) * fps,
  );
  const availableTimelineFrames = Math.max(
    1,
    Math.round(sourceIntervalFrames / playbackRate),
  );

  return Math.min(requestedFrames, availableTimelineFrames);
}

module.exports = { resolveSceneDurationFrames, resolveTrimAfterFrames };
