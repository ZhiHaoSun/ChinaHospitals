# MedTour AI Design System

Status: project design system draft  
Last updated: 2026-07-20  
Scope: frontend UI rendering, content patterns, and visual quality standards

## Product Design Read

MedTour AI is a trust-first medical travel planning workspace for overseas patients, families, and advisors comparing treatment options in China. The interface should feel calm, precise, international, and operational. It is not a travel landing page, a hospital brochure, or a generic AI dashboard.

Design dials:

- `DESIGN_VARIANCE`: 4
- `MOTION_INTENSITY`: 3
- `VISUAL_DENSITY`: 7

The product should prioritize usable planning surfaces over decoration. The first screen should expose the planning input and route the user into comparison, plan review, and readiness decisions.

## Core Principles

1. Calm precision
   Use restrained visual hierarchy, clear labels, measured spacing, and low-noise surfaces. The user is making high-stakes decisions.

2. Compare before commit
   City, cost, timeline, and support differences should be visible before any plan feels final.

3. Uncertainty is part of the interface
   Assumptions, disclaimers, estimates, and missing information should be visible in context instead of hidden behind generic confidence language.

4. Medical constraints stay visible
   Visa, treatment duration, language support, discharge timing, and follow-up readiness should remain close to the decisions they affect.

5. Every number needs context
   Currency, estimate type, inclusions, exclusions, and source assumptions should be clear around prices and timelines.

6. International by default
   UI text, generated dates, form labels, and empty states must work across English and Chinese without hardcoded visible strings.

7. Action without pressure
   CTAs should help the user proceed, save, compare, or clarify. Avoid sales language and remove dead or low-value actions.

## Source Of Truth

Primary frontend files:

- `styles.css`: design tokens, component styles, responsive behavior
- `index.html`: static shell, semantic sections, top-level i18n hooks
- `app.js`: rendered states, generated cards, timeline, comparisons, translated labels
- `design.md`: product design intent and component expectations

This project currently uses native HTML, CSS, and JavaScript. Do not introduce a component library only to express the existing design system.

## Visual Language

The UI should read as a planning console with warm clinical clarity:

- Quiet off-white background
- White and pale green-gray operational surfaces
- Teal as the primary decision and selection color
- Blue as a secondary support color
- Red, amber, and teal semantic states used sparingly
- Border-first cards with small radius
- Shadows only for hierarchy, hover, and modal focus

Avoid:

- Generic SaaS gradients
- Oversized marketing heroes
- Decorative blobs, orbs, and abstract background shapes
- Card walls with no hierarchy
- Placeholder CTAs
- Hardcoded English in dynamic UI

## Color Tokens

Use the existing CSS custom properties in `:root`.

| Token | Value | Usage |
| --- | --- | --- |
| `--background` | `#f6f8f7` | Page background |
| `--surface` | `#ffffff` | Main panels, cards, form surfaces |
| `--surface-low` | `#eef4f2` | Subtle grouped surfaces and input shells |
| `--surface-high` | `#e4ece9` | Hover and secondary background emphasis |
| `--surface-highest` | `#d4e2de` | Stronger neutral fills and selected affordances |
| `--text` | `#142126` | Primary copy |
| `--muted` | `#52615d` | Secondary copy and metadata |
| `--border` | `#c7d2ce` | Standard borders |
| `--border-soft` | `#dbe5e1` | Low-emphasis borders and dividers |
| `--primary` | `#0f766e` | Primary actions, selected state, key progress |
| `--primary-strong` | `#0b5f59` | Primary hover and high-emphasis text |
| `--primary-soft` | `#dff5f1` | Selected backgrounds and supportive accents |
| `--secondary` | `#2563eb` | Links, secondary highlights, focus support |
| `--danger` | `#b42318` | Error and destructive state text |
| `--danger-bg` | `#ffe7e3` | Error backgrounds |
| `--warning` | `#9a5b12` | Warning text |
| `--warning-bg` | `#fff0d8` | Warning backgrounds |
| `--ready` | `#0f766e` | Success and readiness complete state |
| `--focus-ring` | `rgba(37, 99, 235, 0.28)` | Keyboard focus ring |
| `--shadow` | `0 1px 2px rgba(20, 33, 38, 0.06)` | Resting elevation |
| `--shadow-hover` | `0 14px 34px rgba(20, 33, 38, 0.1)` | Interactive lift and modal support |

Color rules:

- Primary teal should signal selection, progress, and the safest next action.
- Blue should support navigation, links, and focus. Do not compete with teal for primary action.
- Warning and danger should be reserved for real plan risks, not decorative badges.
- Maintain contrast for text over tinted backgrounds.

## Typography

Font stack:

```css
font-family: "Outfit", "Noto Sans SC", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
```

Typography rules:

- Use `Outfit` for Latin UI clarity and `Noto Sans SC` for Chinese coverage.
- Keep `font-variant-numeric: tabular-nums` for prices, durations, and comparison tables.
- Use short, direct labels. Avoid vague AI claims.
- Keep heading scale modest inside panels, tables, cards, and tool surfaces.
- Do not scale type with viewport width.
- Letter spacing should remain `0`, except small uppercase metadata where the existing CSS intentionally uses tracking.

Recommended hierarchy:

| Role | Typical size | Weight | Notes |
| --- | ---: | ---: | --- |
| Product mark | 21-23px | 700 | Top nav identity |
| Main planning headline | 32-40px | 700 | First screen only |
| Section title | 24-30px | 700 | Compare, plan, readiness |
| Panel title | 17-20px | 650-700 | Cards and grouped content |
| Body | 15-16px | 400-500 | Default readable copy |
| Metadata | 12-13px | 600-700 | Pills, step labels, table labels |
| Button | 14-15px | 700 | Stable command labels |

## Spacing

Use a 4px-based spacing rhythm.

Page structure:

- Main shell: `width: min(1280px, calc(100vw - 96px))`
- Center shell: `width: min(960px, calc(100vw - 48px))`
- Mobile shell: 16-18px side gutter
- Sticky nav height: about 72px desktop, 76px mobile

Component spacing:

- Tight inline gaps: 6-8px
- Button/icon gaps: 8-10px
- Field gaps: 10-14px
- Card internal padding: 18-24px
- Section spacing: 28-48px
- Major page section spacing: 72-92px

Spacing rules:

- Dense operational views are preferred over sparse brochure layouts.
- Repeated cards should align their actions to the bottom when comparison matters.
- Avoid nested cards. Use bands, borders, or simple grouped surfaces instead.

## Radius And Shape

| Radius | Usage |
| ---: | --- |
| 4px | Small labels, table accents, compact status tags |
| 6px | Skip links, recovery notices, small utility surfaces |
| 8px | Standard buttons, inputs, cards, summaries |
| 12px | Major panels, modal surfaces, city option cards |
| 999px | Pills, chips, switches, circular icon buttons |

Cards should generally stay at 8px or 12px. Avoid large rounded marketing cards.

## Elevation

Elevation should be quiet:

- Resting cards use borders and `--shadow` only when needed.
- Hover lift may use `--shadow-hover` and a small `translateY`.
- Sticky nav can use blur plus a subtle border and shadow.
- Modals use stronger elevation because they interrupt the workspace.

Do not use elevation to make decorative floating sections.

## Motion

Motion should confirm interaction, not entertain.

Preferred durations:

- Micro interaction: 160-180ms
- Panel or card transition: 200-260ms
- Loading or progress shimmer: subtle and non-blocking

Preferred properties:

- `transform`
- `opacity`
- `background-color`
- `border-color`
- `color`

Rules:

- Avoid large animated layout shifts.
- Honor reduced motion preferences.
- Loading states should preserve layout dimensions.

## Layout System

Top-level sections:

- `#intake`
- `#compare`
- `#plan`
- `#readiness`

Expected flow:

1. The user enters planning details.
2. Agent progress explains what the system is checking.
3. The comparison view presents city options before commitment.
4. The plan view shows itinerary, cost, insurance, and follow-up details.
5. The readiness view converts uncertainty into concrete tasks.

Desktop layout:

- Keep compare cards in a grid that supports scanning across cities.
- Use side navigation in plan detail when content becomes long.
- Keep critical numbers close to city and treatment context.

Mobile layout:

- Collapse multi-column grids into single-column sections.
- Keep primary actions full width only when it improves reach and clarity.
- Make timeline details collapsible to reduce long-scroll fatigue.

## Component Standards

### Top Navigation

Selectors: `.top-nav`, `.nav-shell`, `.brand`, `.nav-links`, `.language-switch`, `.auth-button`

Standards:

- Sticky at top with subtle translucent surface.
- Brand stays visually present but does not dominate the planner.
- Links should point to real sections and remain keyboard accessible.
- Language and account controls live at the right side on desktop.
- On mobile, nav links can be hidden while language and account controls remain usable.

### Buttons

Selectors: `.primary-button`, `.outline-button`, `.select-plan`, `.auth-button`, `.google-button`, `.choice-button`

Standards:

- Minimum height: 42px for primary and outline actions.
- Radius: 8px.
- Font weight: 700.
- Use teal fill for the safest main action.
- Use outline buttons for secondary navigation and lower-risk commands.
- Remove actions that do not currently produce value.

States:

- Hover: subtle lift or color shift.
- Active: return closer to resting position.
- Focus-visible: `--focus-ring`.
- Disabled: reduced opacity and no pointer action.

### Forms

Selectors: `.form-card`, `.form-grid`, `.field`, `.input-shell`, `.choice-grid`, `.choice-card`, `.note-area`

Standards:

- Inputs are clear, compact, and grouped by decision.
- Labels remain visible.
- Placeholder text should guide expected content, not replace labels.
- Choice cards should show selection through border, background, and icon state.
- Medical notes should support longer text without crowding.

### Chips And Tags

Selectors: `.quick-chip`, `.status-pill`, `.metric-tag`, `.risk-pill`, `.feature-pill`

Standards:

- Use chips for filters, quick suggestions, compact status, and city attributes.
- Avoid too many colors in one group.
- Status chips should carry real information.

### Switches

Selectors: `.switch`, `.toggle`

Standards:

- Use for binary settings only.
- Keep the label adjacent and explicit.
- Selected state should use teal.

### Agent Progress

Selectors: `.agent-progress`, `.progress-steps`, `.progress-step`, `.progress-bar`

Standards:

- The system should feel transparent while working.
- Progress copy should describe concrete checks such as hospitals, visa timing, cost assumptions, and follow-up readiness.
- Avoid overpromising certainty.

### City Comparison Cards

Selectors: `.city-grid`, `.city-card`, `.city-card.selected`, `.city-card-header`, `.city-metrics`, `.metric`, `.city-pros`, `.city-warnings`

Standards:

- Cards must be comparable at a glance.
- Selected city should use teal border and soft teal background.
- Put decision metrics before narrative detail.
- Keep risks visible but not alarmist.
- Align action buttons across cards when possible.

### Tables

Selectors: `.analysis-table`, `.analysis-row`, `.analysis-cell`

Standards:

- Use tables or table-like grids for values users compare.
- Use tabular numerals.
- Keep labels short.
- Preserve horizontal scan on desktop.
- Collapse carefully on mobile without losing label-value relationships.

### Plan Navigation

Selectors: `.plan-detail`, `.plan-side-nav`, `.plan-nav-item`, `.plan-card`

Standards:

- Side navigation is for orientation inside a long plan.
- Active and hover states should be obvious but quiet.
- Plan cards should expose the decision, evidence, and next step.

### Timeline

Selectors: `.timeline`, `.timeline-item`, `.timeline-dot`, `.timeline-body`, `.timeline-details`

Standards:

- Timeline dates must be localized through app i18n helpers.
- Use collapsed details for long content.
- Make duration, city, appointment, and recovery assumptions visible.
- Do not hardcode weekday names.

### Cost And Insurance

Selectors: `.cost-grid`, `.cost-card`, `.insurance-card`, `.total-estimate`

Standards:

- Show currency and estimate context.
- Make inclusions and exclusions visible.
- Keep disclaimers close to the estimate.
- Avoid presenting provisional costs as guaranteed prices.

### Readiness Checklist

Selectors: `.readiness-grid`, `.readiness-card`, `.readiness-item`, `.readiness-actions`

Standards:

- Checklist items should convert plan risk into concrete user tasks.
- Use semantic state color only when a task has real status.
- Keep task names action-oriented and short.

### Modal And Auth

Selectors: `.auth-modal`, `.modal-backdrop`, `.modal-dialog`, `.modal-close`

Standards:

- Modal should trap visual focus and present one clear task.
- Close action must be accessible.
- Auth copy should explain account value without pressure.

## Content Standards

Tone:

- Calm
- Specific
- Service-oriented
- International
- Medically cautious

Avoid:

- "Best treatment guaranteed"
- "Unlock your journey"
- "AI-powered magic"
- Vague superlatives
- Sales urgency
- Visible placeholder commands

Preferred wording:

- "Compare plans"
- "Review readiness"
- "Estimated total"
- "Assumptions"
- "Follow-up needs"
- "Visa timing"
- "Language support"

## Internationalization

All visible UI text must use the existing i18n system.

Rules:

- Static HTML text should use `data-i18n` where possible.
- Dynamic JavaScript text should use `t()` or structured translation maps.
- Generated dates should use `localeForLanguage()`.
- Prices should use the existing money formatting helper.
- Avoid hardcoded English in rendered timeline, cards, buttons, empty states, and warnings.
- When adding text, update both English and Chinese translation entries in the same change.

Regression search patterns:

```sh
rg -n "Wednesday|Monday|Tuesday|Thursday|Friday|Saturday|Sunday" app.js index.html
rg -n "Adjust Parameters|Adjust parameter|href=\"#\"" index.html app.js
```

## Accessibility

Baseline requirements:

- Preserve the skip link.
- Every interactive element must be keyboard reachable.
- Use `:focus-visible` consistently.
- Icon-only buttons need an accessible name.
- Decorative icons should be `aria-hidden="true"`.
- Progress updates should be compatible with assistive technology.
- Do not rely on color alone for selected, warning, or error states.
- Form fields need persistent labels.
- Text must not overlap or overflow on narrow screens.

## Responsive Rules

Breakpoints currently used:

- `max-width: 1000px`: collapse major grids, stack navigation areas, reduce section spacing.
- `max-width: 560px`: tighten type, buttons, gutters, and form/card padding.

Responsive checks:

- 390px mobile width
- 768px tablet width
- 1440px desktop width

Every check should confirm:

- No horizontal overflow.
- Top navigation remains usable.
- Card actions remain visible.
- Timeline details do not create unreadable long walls.
- Button labels fit their containers.

## Patterns To Preserve

- First-screen planner instead of marketing landing.
- Sticky nav with real section anchors.
- Teal selected state for decisions.
- Compare-before-plan workflow.
- Collapsible timeline detail.
- Tabular numbers for estimates.
- Border-first cards.
- Compact, operational density.

## Patterns To Retire

- Dead buttons and placeholder actions.
- Hardcoded generated English.
- Floating decorative card stacks.
- Generic AI feature copy.
- Overly large hero typography inside tool panels.
- Nested cards.
- Vague labels like "optimize", "unlock", or "adjust" when the result is unclear.

## Quality Checklist

Before merging frontend UI changes:

- Run `node --check app.js` after JavaScript changes.
- Search for hardcoded weekday names in dynamic renderers.
- Search for dead anchors and placeholder CTAs.
- Confirm no Python or data files changed unless explicitly requested.
- Review mobile at 390px and desktop at 1440px.
- Check hover, focus, selected, loading, and empty states.
- Confirm English and Chinese strings were updated together.
- Verify visible numbers include currency, estimate context, or assumptions.

## Implementation Notes

- Keep tokens in `:root` in `styles.css`.
- Prefer extending existing selectors before adding new naming systems.
- Keep visual changes scoped to render and style files for UI-only requests.
- Use small utility classes only when they are reused and easier to audit than one-off CSS.
- Keep comments rare and useful.
- Preserve the existing no-framework runtime unless a future requirement justifies a larger frontend architecture.
