# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

An individual creator working with their own long-form video and looking to prepare short clips. This audience is inferred from the personal clipper brief.

## Product Purpose

Clip Studio lets a person import a local video, manually mark and review moments, and export selected clips as MP4.

## Positioning

A local-first, manual editing path that keeps the creator in control of which moments become clips. It does not claim automatic highlight selection.

## Operating Context

The user works in a browser on their own computer with local source videos and FFmpeg available on the machine.

## Capabilities and Constraints

The current MVP supports local video import, manual in/out selection, clip previews, and MP4 export in the source aspect ratio or a fixed-center 9:16 crop. It does not provide automatic highlight detection, subject tracking, automatic captions, or social publishing.

## Brand Commitments

Use the OpenMontage name. Klap.app is a product-category reference, not a source for copied code, branding, exact visual design, or assets.

## Evidence on Hand

The Clip Studio implementation and its focused tests are in `clipper_studio/` and `tests/clipper_studio/`.

## Product Principles

- Keep source footage local.
- Make manual selection and edit state clear.
- Describe only capabilities that are implemented.
- Preserve a direct path from source video to downloadable MP4 clips.
