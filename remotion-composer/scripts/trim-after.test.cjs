const assert = require("node:assert/strict");
const test = require("node:test");

const { resolveTrimAfterFrames } = require("../src/cinematic/trim-after.js");

test("playback-rate trim preserves the source-out without exposing later regions", () => {
  const fps = 30;
  const regions = [
    ...Array(30).fill("red"),
    ...Array(30).fill("green"),
    ...Array(30).fill("blue"),
  ];

  for (const playbackRate of [0.5, 2]) {
    const scene = {
      kind: "video",
      id: `rate-${playbackRate}`,
      startSeconds: 0,
      durationSeconds: 6,
      src: "three-color-test-video",
      trimBeforeSeconds: 0,
      trimAfterSeconds: 2,
      playbackRate,
    };
    const trimAfter = resolveTrimAfterFrames(scene, fps);
    const visibleRegions = new Set();

    for (let timelineFrame = 0; timelineFrame < trimAfter; timelineFrame += 1) {
      const sourceFrame = Math.floor(timelineFrame * playbackRate);
      visibleRegions.add(regions[sourceFrame]);
    }

    assert.equal(trimAfter, Math.round((2 * fps) / playbackRate));
    assert.ok(visibleRegions.has("green"));
    assert.ok(!visibleRegions.has("blue"));
  }
});
