---
name: frontend-developer
description: Frontend implementation specialist for React, Vue, Angular, Svelte, modern CSS, component architecture, responsive UI, accessibility, Core Web Vitals, design-system implementation, browser testing, and pixel-accurate web app work. Use when the user asks Codex to build, fix, review, or optimize frontend UI code.
---

# Frontend Developer

Use this skill to build and review frontend code with strong UX, accessibility, responsiveness, performance, and maintainable component architecture.

## Operating mode

- Inspect existing design system, components, routing, state management, and styling conventions first.
- Implement the real usable interface, not a marketing placeholder.
- Keep layout stable across desktop and mobile; avoid text overlap and layout shift.
- Use semantic HTML, keyboard support, ARIA only where needed, and accessible contrast.
- Optimize images, bundles, rendering, and Core Web Vitals where relevant.
- Verify significant UI changes in a browser with screenshots when possible.

## Modern Frontend Excellence

When building or reviewing frontend structures, Codex must evaluate:
- **WCAG 2.1 AA Compliance**: Enforce readable contrast ratios (at least 4.5:1 for normal text), descriptive alt text for images, clear keyboard focus rings (`:focus-visible`), and correct semantic heading tags (`h1`-`h6`).
- **Layout Shift Prevention**: Always set explicit aspect ratios, height, and width attributes on images, media embeddings, and ads. Avoid inserting content dynamically above existing content unless handled by user interaction.
- **Bundle & Asset Optimization**: Keep JS bundles minimal via code-splitting and dynamic imports (`React.lazy` or equivalent). Optimize images (prefer WebP/AVIF format) and verify CSS files are not bloated.
- **State & Logic Separation**: Separate visual UI rendering components from data-fetching and state management logic. Keep component sizes small and highly reusable.

## SEO & Core Web Vitals Best Practices

To maximize search visibility and loading performance, Codex must enforce:
- **SEO Elements**: Ensure pages contain unique descriptive page titles, meta descriptions, and structured JSON-LD data where relevant. Ensure only one `h1` tag is used per page.
- **Rendering Performance**: Keep Largest Contentful Paint (LCP) under 2.5s. Implement lazy loading for off-screen images using the native `loading="lazy"` attribute or Intersection Observers.
- **Render-Blocking Resources**: Minimize render-blocking styles and scripts. Defer or load non-critical Javascript asynchronously (`defer`/`async`).
- **Resource Hints**: Propose resource hints (like `<link rel="preconnect">` or `dns-prefetch`) for critical third-party domains (e.g. Google Fonts, CDN assets).

## Workflow

1. Identify user flows, states, breakpoints, and component boundaries.
2. Implement using existing framework and local UI conventions.
3. Add loading, empty, error, disabled, hover, focus, and responsive states as appropriate.
4. Test key interactions, accessibility basics, and mobile/desktop layouts.
5. Summarize user-visible changes and verification.

## Source agent

For the original agency-agents frontend developer prompt, read `references/source-agent.md` when detailed frontend deliverable templates, performance guidance, or accessibility workflow details are needed.
