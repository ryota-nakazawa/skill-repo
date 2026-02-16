---
name: html-slide-generator-ja
description: Generate 16:9 single-file HTML slide decks from Japanese Markdown reports with clear long-distance readability and modern visual styling. Use when converting attached markdown/documents into presentation slides, defining slide structure and density, implementing keyboard navigation/UI, removing citation artifacts, adding understandable visual elements (charts/diagrams), and producing export-friendly HTML without external libraries.
---

# HTML Slide Generator JA

## Overview

- Convert a Japanese report-style Markdown file into a presentation-grade HTML deck.
- Keep output as a single `index.html` file with embedded CSS/JS and no external dependencies.
- Prioritize readability from distance (large type, high contrast, low clutter).

## Workflow

### 1. Read Source and Fix Constraints

- Read the entire source Markdown.
- Extract headings and section boundaries before drafting slide titles.
- Remove or ignore citation artifacts such as `cite...` and `entity...`.
- Lock constraints early: aspect ratio, target slide count range, style direction, animation policy, and UI policy.

### 2. Build Slide Outline Before Coding

- Map one message per slide.
- Preserve section order unless user explicitly asks to reorganize.
- For dense reports, use 14-24 slides as default range.
- Reserve dedicated slides for: title, agenda, key framework visuals, comparison tables, checklist/closing.

### 3. Implement Single-File Deck

- Start from `assets/modern-16x9-template.html` when available.
- Implement with one `index.html` containing HTML/CSS/JS.
- Use a fixed stage design for 16:9.
- Recommended base: `1600x900` stage scaled to viewport.
- Include keyboard controls:
  - `ArrowLeft` / `ArrowRight`
  - `Home` / `End`
  - optional `M` for TOC
- Include minimal presenter UI:
  - progress bar
  - page indicator
  - optional TOC panel

### 4. Apply Readability-First Visual Design

- Read `references/slide-design-rules-ja.md` before final styling.
- Use explicit CSS variables for color tokens and typography.
- Keep minimum size guidelines:
  - title around 64px
  - section heading around 42px
  - body around 28px
  - notes around 22px
- Keep strong contrast and avoid overloaded backgrounds.
- Prefer cards/grids/process blocks over long paragraphs.

### 5. Add Visual Elements Where Useful

- Insert charts/diagram-like blocks where they improve comprehension.
- Choose visual forms by message type:
  - comparison -> matrix/table/bar
  - progression -> timeline/stair/flowline
  - composition -> donut/stacked blocks
  - process -> node/arrow flow
- Use CSS/SVG/native HTML for lightweight visuals.
- Treat chart values as relative indicators unless hard data exists in source.
- Keep labels readable at presentation distance.

### 6. Optional Export-Friendly Mode

- Add optional query-driven export mode for PNG capture.
- Example policy:
  - `?slide=<n>&export=1`
  - hide HUD/TOC/progress overlays
  - force full-frame slide render
- Keep normal presentation mode unchanged.

### 7. Validate Before Delivery

- Verify slide count matches planned outline.
- Verify no citation artifacts remain.
- Verify keyboard navigation and page indicator behavior.
- Verify no external JS/CSS dependencies are required.
- Verify all slides stay within 16:9 layout without overflow.

## Resources

- `references/slide-design-rules-ja.md`
  - Use as the design QA checklist before final delivery.
- `assets/modern-16x9-template.html`
  - Use as the default starter template for new slide generation tasks.

## Output Contract

- Main deliverable: `index.html`.
- Optional deliverables:
  - `png-export/slide-XX.png`
  - image-based PPTX for fidelity comparison
  - hybrid editable PPTX when requested

## Default Decisions

- Prefer readability over information density when tradeoffs appear.
- Prefer deterministic structure over heavy animation.
- Keep Japanese text natural and concise for spoken presentation.
