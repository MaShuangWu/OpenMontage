---
name: OpenMontage Clip Studio
description: A local-first workspace for selecting and exporting short video clips.
colors:
  primary: "#625cf0"
  primary-hover: "#514bdc"
  accent-soft: "#f0efff"
  neutral-canvas: "#f5f6fa"
  neutral-surface: "#ffffff"
  neutral-ink: "#202234"
  neutral-muted: "#656a7c"
  neutral-border: "#e5e7ef"
  focus-outline: "#9692ff"
  upload-border: "#c9c7f1"
  selection-border: "#dbd9ff"
  local-indicator: "#35a878"
  breadcrumb-muted: "#b6b9c5"
  status-surface: "#e1eee7"
  status-text: "#357657"
  stage-copy: "#c3c4cf"
  stage-control: "#555563"
  stage-control-hover: "#343443"
  stage-copy-secondary: "#b4b5c1"
  error-surface: "#fff0f2"
  video-stage: "#11121a"
typography:
  ui-xs:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "8px"
  ui-caption:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "9px"
  ui-small:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "10px"
  ui-control:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "11px"
  ui-panel:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "12px"
  ui-subtitle:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "13px"
  body:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "14px"
    lineHeight: 1.5
  ui-large:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "16px"
  ui-icon:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "17px"
  ui-mark:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "19px"
  ui-heading:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "20px"
  page-title:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "23px"
rounded:
  xs: "5px"
  sm: "6px"
  row: "7px"
  control: "8px"
  md: "9px"
  mark: "10px"
  pill: "99px"
spacing:
  sm: "8px"
  md: "16px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    rounded: "{rounded.sm}"
    height: "35px"
---

# Design System: OpenMontage Clip Studio

## Overview

**Creative North Star: "The hands-on editing desk."**

Clip Studio is a focused work surface: bring a source into view, find exact moments, review a short queue, and export. The visual language uses the familiar navigation and controls of a creator tool while keeping its local, manual workflow explicit. Klap.app informs the product category only; its identity, assets, claims, and exact visual design are not reused.

The interface favors clear state over promotional decoration. The source library, video stage, and clip queue remain distinct, and the active action is easy to find.

**Key Characteristics:**
- Light editing canvas with a compact persistent navigation rail.
- Violet marks selection and primary actions.
- Dark video stage is reserved for the footage itself.
- Manual editing and local processing are described honestly.

## Colors

A restrained light neutral system uses violet for active work and green only for local-ready status.

### Primary
- **OpenMontage violet** (#625cf0): Primary actions, active navigation, and scrubber progress.
- **Violet hover** (#514bdc): Hover state for primary actions.
- **Soft violet** (#f0efff): Selected navigation and clip markers.

### Neutral
- **Canvas** (#f5f6fa): Main workspace background.
- **Surface** (#ffffff): Sidebar, panels, and controls.
- **Ink** (#202234): Main text.
- **Muted ink** (#656a7c): Supporting text and labels.
- **Divider** (#e5e7ef): Panel and control boundaries.
- **Video stage** (#11121a): Preview background around source footage.

## Typography

**Body Font:** Segoe UI, system-ui, -apple-system, sans-serif.

**Character:** A familiar system sans keeps dense editing controls readable and native-feeling.

### Hierarchy
- **Page title** (680, 23px): Main editing task.
- **Panel title** (650, 12-13px): Source, clip, and export sections.
- **Body** (400-600, 10-14px, 1.5 line-height): Instructions, source metadata, and state.
- **Control label** (600, 9-10px): Short field labels and secondary metadata.

## Layout

The desktop shell reserves a 248px sidebar for navigation and local sources. The work area pairs a flexible preview/editor column with a 318px clip queue. At narrower widths the queue moves below the editor; on small screens the sidebar becomes a compact top navigation and the editor uses a single column.

## Elevation & Depth

Panels are flat at rest. Thin neutral borders distinguish work areas; the video stage provides the main tonal contrast. No decorative shadows are used.

## Shapes

Controls and panels use restrained 6-9px corners with thin boundaries. Pills are reserved for short status and count labels.

## Components

### Buttons
- **Shape:** Compact 6px corners.
- **Primary:** OpenMontage violet with white text; 35px minimum height.
- **Hover / Focus:** Darker violet hover; a visible violet outline for keyboard focus.
- **Disabled:** Reduced opacity and a non-interactive cursor.

### Cards / Containers
- **Corner Style:** 9px panels, 7px nested rows.
- **Background:** White panels against the light canvas.
- **Border:** Thin neutral boundary; selected sources receive a soft violet surface and boundary.
- **Internal Padding:** 14-16px for editing panels.

### Inputs / Fields
- **Style:** White fill with a neutral border and 6px corners.
- **Focus:** Visible violet outline.
- **Disabled / Error:** Disabled actions are subdued; upload and export errors use clear red text.

### Navigation
- **Style:** Persistent left rail on desktop with compact labels and simple glyphs.
- **Active:** Soft violet background and violet text.
- **Mobile:** Navigation moves into a horizontal, scrollable top row.

### Video Stage and Timeline
- The source video sits on a dark 16:9 stage. A labeled range control scrubs the source; in/out fields and mark buttons provide exact manual boundaries.

## Do's and Don'ts

### Do:
- **Do** keep source, editor, clip queue, and export status visually distinct.
- **Do** use violet for selected and primary-action states.
- **Do** keep local-storage and manual-selection behavior explicit.

### Don't:
- **Don't** imply automatic highlight detection, captions, subject tracking, or publishing.
- **Don't** introduce Klap branding, exact compositions, or third-party assets.
- **Don't** use decorative accents that compete with the video preview.
