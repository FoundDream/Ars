---
name: better-interface
description: Build, improve, and review product interfaces as one system across accessibility, layout, UX writing, typography, color, and UI polish. Use when implementing or auditing web UI, components, screens, flows, forms, responsive behavior, interaction states, design-system details, or when the user asks for better-interface, a holistic UI review, accessibility, layout, copy, type, color, icons, surfaces, or motion polish. Supports targeted, quick, full, and implementation modes.
---

# Better Interface

Treat the interface as one system. Preserve the product's conventions, load only the domain references the task needs, and prioritize user impact over cosmetic novelty.

## Resolve the mode

Infer mode from the request and state the resolved scope when reviewing.

| Mode | Use when | Coverage |
| --- | --- | --- |
| `targeted` | One component or one domain is in scope | Load only the owning domain and relevant detailed references |
| `quick` | The user requests a fast holistic review | Inspect the primary path across all six domains; report at most 5 `HIGH` or `MEDIUM` findings |
| `full` | The user requests a complete or holistic review | Inspect the requested flow across all six domains and relevant loading, empty, error, narrow-width, keyboard, and appearance states; report at most 15 findings |
| `implementation` | The user asks to build, fix, or improve the interface | Load relevant domains, make the requested changes, and verify them; do not force a review report |

Use `full` when the user explicitly requests a holistic review without naming a mode. Otherwise infer `targeted` or `implementation` from the task. Narrow an unreviewably large scope to the highest-traffic complete flow and disclose the boundary.

## Apply the authority order

Resolve conflicts in this order:

1. Follow the user's explicit requirements and supported product constraints.
2. Meet applicable accessibility, platform, and interoperability requirements.
3. Preserve the project's component library, design tokens, styling system, density, and interaction language.
4. Apply domain heuristics when evidence supports them.
5. Use house-style recipes only when the project has no established answer.

Treat exact aesthetic values in the UI-polish references—animation scale, blur, bounce, radius, shadow, and outline recipes—as starting presets, not universal laws. Requirements may be unconditional; taste must remain contextual. Verify current standards and browser support before making compliance or compatibility claims.

## Follow the workflow

1. **Resolve scope and intent.** Identify the screen, flow, component, repository boundary, and whether the user wants review or implementation.
2. **Recon the project.** Identify framework, styling system, component library, tokens, supported viewports and browsers, localization conventions, and relevant preview or test commands.
3. **Load references.** Read every domain overview required by the mode, then read only the detailed files relevant to actual evidence. For a holistic review, read all six overviews.
4. **Inspect the artifact.** Read source for code claims. Inspect the rendered interface for visual or runtime claims. Traverse relevant states and user paths.
5. **Assign ownership.** Report one root cause once under its owning domain; mention secondary effects in the rationale.
6. **Act within intent.** Keep reviews read-only. For implementation requests, make the scoped changes using the project's existing conventions.
7. **Verify.** Run safe, relevant checks and report observed results. Mark unperformed checks `Not verified`; never turn a verification gap into a finding.

## Route domain knowledge

All reference files are directly reachable from this entry point. Do not load every detailed file by default.

| Domain | Owns | Read |
| --- | --- | --- |
| Accessibility | Semantic HTML, keyboard and focus behavior, accessible names, forms, assistive technology, reduced motion, zoom, and accessibility requirements | Start with [accessibility.md](references/accessibility.md). Read [focus and keyboard](references/accessibility-focus-and-keyboard.md), [semantics and ARIA](references/accessibility-semantics-and-aria.md), [forms](references/accessibility-forms.md), [screen readers](references/accessibility-screen-readers.md), [hit areas](references/accessibility-hit-areas.md), or [motion and zoom](references/accessibility-motion-and-zoom.md) when relevant. |
| Layout | Grouping, alignment, spacing, responsive structure, reading order, logical properties, clipping, and spatial RTL behavior | Start with [layout.md](references/layout.md). Read [grouping and alignment](references/layout-grouping-and-alignment.md) or [spacing and adaptivity](references/layout-spacing-and-adaptivity.md) when relevant. |
| Writing | Source wording, terminology, voice, tone, labels, errors, settings, and empty-state copy | Read [writing.md](references/writing.md). |
| Typography | Visual text rendering, type systems, font behavior, wrapping, punctuation, truncation, and text-level bidi behavior | Start with [typography.md](references/typography.md). Read [choosing fonts](references/typography-choosing-fonts.md), [variable fonts and OpenType](references/typography-variable-fonts-and-opentype.md), [spacing and sizing](references/typography-spacing-and-sizing.md), [wrapping and punctuation](references/typography-wrapping-and-punctuation.md), [details and accessibility](references/typography-details-and-accessibility.md), or the [CSS cheat sheet](references/typography-css-cheat-sheet.md) when relevant. |
| Colors | Color notation, semantic tokens, palette construction, gamut, appearance variants, rendered-pair contrast measurement, and color remediation | Start with [colors.md](references/colors.md). Read [conversion](references/colors-color-conversion.md), [palette generation](references/colors-palette-generation.md), [contrast](references/colors-accessibility-contrast.md), [gamut and Tailwind](references/colors-gamut-and-tailwind.md), or [color usage](references/colors-color-usage.md) when relevant. |
| UI polish | Optional surface, icon, and motion craft after interaction, accessibility, structure, copy, type, and color are sound | Start with [ui-polish.md](references/ui-polish.md). Read [surfaces](references/ui-surfaces.md), [animations](references/ui-animations.md), [icons](references/ui-icons.md), or [performance](references/ui-performance.md) when relevant. |

When concerns cross domains, use this ownership map:

- Accessibility determines whether contrast is required and classifies impact; Colors measures and remediates the rendered pair.
- Accessibility owns semantic heading structure; Typography owns its visual rendering.
- Layout owns logical properties and spatial mirroring; Typography owns language metadata, punctuation, and mixed-direction text.
- Typography owns truncation mechanics; Layout owns available room and expansion affordances; Writing owns source copy.
- Accessibility owns reduced-motion requirements; UI polish owns optional animation recipes.

## Require evidence

- Cite `path/to/file:line` for source findings. For artifacts without source, cite the exact screen and component.
- Show the current implementation and an actionable replacement.
- Do not infer runtime behavior from source alone when browser behavior decides the result.
- Do not infer a code defect from appearance alone when computed styles, DOM, or state are required.
- Consolidate repeated instances caused by one token or shared component into one finding and list all confirmed locations.
- Prefer shared-component and token fixes over leaf-level patches.
- Do not pad a review to reach its finding cap.

## Measure colors deterministically

Use the bundled script rather than estimating conversions, sRGB gamut, or WCAG 2 contrast:

```bash
python3 <skill-root>/scripts/color_tools.py convert '#3b82f6'
python3 <skill-root>/scripts/color_tools.py contrast '#111827' '#ffffff'
python3 <skill-root>/scripts/color_tools.py gamut 'oklch(0.7 0.35 150)'
python3 <skill-root>/scripts/color_tools.py clamp 'oklch(0.7 0.35 150)'
```

Do not invent APCA values. Report APCA only when a deterministic APCA calculator was actually run, and include polarity, font size, and weight context. Use WCAG 2 thresholds for WCAG 2 conformance claims. Preserve the project's established tokens and notation unless color-system migration is explicitly in scope.

## Review output

Use this format only for review modes. For implementation mode, summarize changes and verification instead.

### Scope and Coverage

State the mode, exact scope, stack, styling conventions, reviewed states, and any boundary. For `quick` and `full`, include all six domains:

| Domain | Evidence inspected | Result |
| --- | --- | --- |
| Accessibility | Files, components, states, or checks | Findings count, `Clear`, or `Not reviewed` with reason |

### Findings

Order one consolidated table by severity, then reach and leverage:

| # | Severity | Domain | Location | Before | After | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | HIGH | Accessibility | `src/Dialog.tsx:42` | `<button><XIcon /></button>` | Add an accessible name and hide the decorative icon | The icon-only control has no accessible name |

Use the shared severity scale:

- `HIGH`: blocks a task, misleads the user, hides content or controls, creates data-loss risk, or causes a repeated systemic accessibility failure.
- `MEDIUM`: meaningfully harms comprehension, efficiency, adaptability, or consistency.
- `LOW`: isolated polish with limited task impact; include only in `full` or `targeted` mode.

If there are no findings, omit the table and state `No actionable interface findings`.

### Considered but Rejected

Include this section only when real borderline candidates were inspected and deliberately rejected because evidence was insufficient, the project convention was intentional, or the change would add complexity without user benefit. Never invent filler.

### Verification

List each exact command or interaction and its observed result. Separate passed checks from `Not verified` checks.

### Verdict

End a review with exactly one:

- `Block` when one or more `HIGH` findings remain.
- `Needs changes` when only `MEDIUM` or `LOW` findings remain.
- `Approve` when no actionable findings remain and the claimed coverage was verified.

## Implementation output

Lead with the completed outcome. Name the important files or components changed, list relevant verification and observed results, and disclose anything still unverified. Do not reproduce the review template unless the user also requested a review.
