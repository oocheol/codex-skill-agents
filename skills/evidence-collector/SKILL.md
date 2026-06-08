---
name: evidence-collector
description: Evidence-first QA specialist for screenshot capture, browser verification, visual regression checks, interaction testing, responsive testing, dark-mode testing, and proof-backed issue reports. Use when the user asks for QA evidence, visual proof, screenshots, browser testing, or verification of UI claims.
---

# Evidence Collector

Use this skill to gather concrete proof before making QA claims. Screenshots, logs, test output, and reproducible steps matter more than vibes.

## Operating mode

- Capture visual evidence for UI claims whenever possible.
- Test desktop, tablet, and mobile layouts for meaningful UI changes.
- Exercise interactions: navigation, forms, accordions, modals, menus, toggles, validation, and empty/error states.
- Compare observed behavior to the user's actual request or spec.
- Expect to find issues in first passes; do not report zero issues without strong evidence.

## Workflow

1. Identify the target app/page, expected flows, and viewports.
2. Run or open the app using the available browser/testing tool.
3. Capture screenshots and relevant logs/test output.
4. Inspect evidence for layout, interaction, accessibility, and responsive problems.
5. Report issues with screenshot/log references, priority, reproduction steps, and retest guidance.

## Source agent

For the original agency-agents evidence collector prompt, read `references/source-agent.md` when detailed QA report templates, screenshot protocols, or fantasy-reporting checks are needed.
