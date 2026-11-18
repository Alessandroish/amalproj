---
name: open-design
description: Entry point to the OpenDesign toolkit (nexu-io/open-design) installed in this repo — 168 design skills, craft rules and 152 DESIGN.md design systems. Use when the user says "open-design", "OpenDesign", asks to pick a design system (e.g. "в стиле Linear/Stripe/Apple"), or wants a landing page, deck, poster, dashboard, mobile screen or other design work done the OpenDesign way.
---

# OpenDesign (local install)

Source: https://github.com/nexu-io/open-design (Apache-2.0). Installed without the `od` daemon/MCP server — everything is plain files.

## Layout
- `.claude/skills/<name>/SKILL.md` — 168 functional skills (frontend-design, slides, poster-hero, data-report, shadcn-ui, gsap-*, threejs, remotion, brand-extract, design-review, …). Invoke them by name.
- `.claude/open-design/craft/*.md` — shared craft rules (typography, color, anti-ai-slop, accessibility-baseline, animation-discipline, laws-of-ux, state-coverage, form-validation, rtl-and-bidi).
- `.claude/open-design/design-systems/<brand>/DESIGN.md` — 152 design systems (linear, stripe, apple, airbnb, vercel, notion, …).

## How to run a design task
1. Pick the matching skill: `ls .claude/skills` and read its `SKILL.md`.
2. If its frontmatter has `od.craft.requires: [...]`, read those files from `.claude/open-design/craft/`.
3. If the user names a style/brand, read `.claude/open-design/design-systems/<brand>/DESIGN.md` and follow its tokens (colors, type, spacing, radius). Otherwise ask for one or pick a fitting one and say which.
4. Ignore `od:` frontmatter fields that only the OpenDesign daemon uses (mode, preview, outputs); write real files in the project instead.

## Commands the user may give
- "open-design: список скиллов" → list `.claude/skills` with one-line descriptions.
- "open-design: дизайн-системы" → list `.claude/open-design/design-systems`.
- "open-design: <задача> в стиле <brand>" → steps above.
