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

module.exports = { resolveTrimAfterFrames };
