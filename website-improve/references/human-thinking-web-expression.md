# Human-thinking web expression and information-flow lens

Last reviewed: **2026-08-12**

This is the shared semantic source of truth for a durable owner preference:

> Human-facing webpages should use HTML's expressive power to represent how people understand, compare, decide, act, and verify—not merely place prose inside decorative cards. They should balance information density with a clear, continuous reading and interaction flow.

This lens applies across projects and Agent harnesses. Project repositories keep only a thin pointer plus local product/validation constraints; they must not fork this document into divergent copies.

## Situational trigger

Evaluate this lens whenever a change can alter what a person sees or understands in a rendered web surface, including a request that sounds as small as “add one item/content block to this page.” Typical cues include:

- HTML, Astro, React, Vue, Svelte, MDX, Markdown rendered as a page, or templated/generated HTML;
- page copy, content order, navigation, onboarding, help, documentation, search/filter results, comparison, status, empty/loading/error states;
- component composition, layout, spacing, responsive behavior, theme, accessibility, or animation that affects comprehension;
- user-facing data labels, evidence, uncertainty, actions, outputs, or generated artifacts.

A pure backend, CI, dependency, data-pipeline, or infrastructure change with no rendered human-facing effect may be `NOT_APPLICABLE`. Do not invent UI work merely to satisfy the lens.

## Required disposition

Choose one disposition before editing:

### `APPLY_LIGHT`

Use for a small, local rendered change whose surrounding information architecture remains sound.

Do not start a heavyweight workflow solely for ceremony. Still decide and verify:

1. the reader's immediate goal;
2. the mental relationship being added or changed;
3. the semantic HTML form;
4. the density layer and placement;
5. the smallest evidence that proves the result reads and works correctly.

Record a compact evidence line in the task log, PR, or completion report when such a surface exists:

```text
Web expression: APPLY_LIGHT — goal=<...>; relation=<...>; HTML=<...>; density=<...>; evidence=<...>
```

### `APPLY_FULL`

Use when the change creates or substantially alters a route, feature, workflow, comparison, research explanation, navigation system, reusable visual grammar, or multi-section reading order.

Run the project-approved website workflow. When `website-improve` is selected, its independent Planner → Executor → Verifier contract remains mandatory. The plan and acceptance criteria must include the web-expression decision below.

### `NOT_APPLICABLE`

Use only when the task has no rendered human-facing consequence. State the reason briefly rather than pretending the lens was applied.

## The web-expression decision

Before implementation, answer these six questions at the smallest useful level of detail.

### 1. Reader goal

What should the reader understand, decide, do, or verify next?

A page should have a legible purpose at each major layer. “Show all available content” is not a sufficient goal.

### 2. Mental relationship

Which relationship carries the meaning?

- **sequence / journey** — what happens first, next, and last;
- **hierarchy / containment** — what belongs inside what, and which level matters now;
- **comparison / trade-off** — what dimensions differ and why the difference matters;
- **cause / dependency** — what enables, blocks, changes, or follows from something else;
- **evidence / uncertainty** — what is known, measured, inferred, missing, or disputed;
- **state / feedback** — current status, progress, success, failure, and recovery;
- **topology / data flow** — which systems, actors, or artifacts connect;
- **decision / branching** — which condition sends the reader to which action.

Do not default every relationship to an undifferentiated card grid.

### 3. Semantic HTML form

Choose native structure that exposes the relationship to browsers, assistive technology, static inspection, and future Agents.

| Meaning | Prefer | Avoid as the only structure |
| --- | --- | --- |
| ordered route or procedure | `<ol>`, headings, anchored sections | disconnected cards with decorative arrows |
| hierarchy or grouped concepts | nested sections/lists, `<nav>`, `<article>` | spacing alone as hierarchy |
| term/value or compact facts | `<dl>` | repeated label/value `<div>` soup |
| comparable dimensions | a real `<table>` when tabular, or repeated sections with identical dimensions | visually aligned but semantically unrelated boxes |
| evidence or figure | `<figure>` + `<figcaption>`, citations, explicit evidence labels | unlabeled illustration |
| optional depth | `<details>` + `<summary>` with complete static meaning | JavaScript-only hidden content |
| warning, boundary, or supporting note | `<aside>` with a clear heading/label | color alone |
| status, result, or progress | textual state plus `<output>`, `<progress>`, or suitable ARIA semantics | spinner/badge without meaning |
| action/input | `<form>`, `<label>`, `<button>`, fieldset/legend where relevant | clickable generic containers |

Custom components are welcome when they emit meaningful HTML and preserve a complete static reading order.

### 4. Density architecture

Place information in intentional layers instead of making everything equally loud or equally hidden.

```text
L0 — orientation: what this is, why it matters, and the next route/action
L1 — core path: the minimum complete sequence, comparison, or decision model
L2 — working detail: commands, examples, controls, evidence, failure handling
L3 — reference depth: provenance, exhaustive data, history, edge cases
```

Not every page needs four visible sections, but every dense page should make the current layer and next step understandable.

Use progressive disclosure for optional depth, not for facts required to make the primary decision. Preserve meaning without JavaScript; enhancement may improve interaction, not manufacture the only readable structure.

### 5. Flow and continuity

Check the affected journey, not only the edited component.

- headings should form a truthful outline;
- ordering should match dependency and reader intent;
- transitions should explain why the next section follows;
- actions should appear where the related content is consumed;
- desktop and mobile order must communicate the same meaning;
- light/dark themes, zoom, keyboard navigation, and reduced-motion behavior must not destroy the relationship;
- animation may clarify state or flow but cannot be the only carrier of meaning.

A locally attractive block is a failure when it fragments the surrounding route.

### 6. Acceptance evidence

Select evidence proportional to the changed layer:

- semantic/source inspection for native structure, headings, labels, and static meaning;
- project build/type/test checks that own the component or route;
- browser inspection of the real changed route when layout, interaction, responsive behavior, theme, or visual order matters;
- keyboard/focus and assistive-label checks for interactive changes;
- desktop/mobile and light/dark review when the project supports those states;
- screenshot or deployed-route evidence only when it materially proves the requested outcome.

A component file existing, a clean Git merge, or a provider `READY` badge is not proof that the reader can understand and use the result.

## Practical patterns

### Adding one fact

Do not automatically append a paragraph or card. Decide whether the fact is a definition, term/value, comparison dimension, evidence item, warning, or next action. Place it in the layer where it changes understanding.

### Adding an experiment step

Represent the ordered path with `<ol>` and stable anchors. Pair the step with its observable PASS condition, first failure check, and next route. Put optional background below or inside progressive disclosure.

### Adding a comparison

Name the shared dimensions first. Use a table when cells are genuinely comparable; otherwise use repeated sections with the same labeled dimensions. Separate measured facts, inference, and unknowns.

### Adding status or generated output

Show state, timestamp/provenance when relevant, what the state proves, what it does not prove, and the local action (copy/open/download/retry). Do not force the user to reconstruct the output elsewhere.

## Permanent anti-patterns

- ❌ treating “use HTML expressively” as “add more visual decoration”;
- ❌ replacing a mental model with a wall of equally weighted cards;
- ❌ using headings, spacing, color, arrows, or motion as the only semantic carrier;
- ❌ hiding the primary path to make the first viewport look cleaner;
- ❌ showing every detail at once and calling it information density;
- ❌ optimizing one component while breaking the page journey, mobile order, or theme contrast;
- ❌ duplicating the same explanation across multiple repositories instead of linking the shared source;
- ❌ claiming completion without evidence from the actual changed layer.

## Project adaptation contract

A project with human-facing web surfaces should add only a short route in its existing `AGENTS.md`, scenario registry, UI policy, or Agent docs index:

1. identify which tasks trigger this lens automatically;
2. point to this shared reference;
3. name local product, design-system, route, accessibility, and validation owners;
4. preserve project-specific exceptions and executable truth;
5. avoid copying this full document.

Non-web projects do not need a cosmetic adapter. The account-level trigger can classify their ordinary work as `NOT_APPLICABLE` until a real web surface enters scope.
