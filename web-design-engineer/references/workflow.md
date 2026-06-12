## Workflow

### Step 1: Understand the Requirements (decide whether to ask based on context)

Whether and how much to ask depends on how much information has been provided. **Do not mechanically fire off a long list of questions every time**:

| Scenario | Ask? |
|---|---|
| "Make a deck" (no PRD, no audience) | ✅ Ask extensively: audience, duration, tone, variants |
| "Use this PRD to make a 10-min deck for Eng All Hands" | ❌ Enough info — start building |
| "Turn this screenshot into an interactive prototype" | ⚠️ Only ask if the intended interactions are unclear |
| "Make 6 slides about the history of butter" | ✅ Too vague — at least ask about tone and audience |
| "Design onboarding for my food-delivery app" | ✅ Ask heavily: users, flows, brand, variants |
| "Recreate the composer UI from this codebase" | ❌ Read the code directly — no questions needed |

Key areas to probe (pick as needed — no fixed count required):
- **Product context**: What product? Target users? Existing design system / brand guidelines / codebase?
- **Output type**: Web page / prototype / slide deck / animation / dashboard? Fidelity level?
- **Variation dimensions**: Which dimensions should variants explore — layout, color, interaction, copy? How many?
- **Constraints**: Responsive breakpoints? Dark/light mode? Accessibility? Fixed dimensions?

### Step 2: Gather Design Context (by priority)

Good design is rooted in existing context. **Never start from thin air.** Priority order:

1. **Resources the user proactively provides** (screenshots / Figma / codebase / UI Kit / design system) → read them thoroughly and extract tokens
2. **Existing pages of the user's product** → proactively ask whether you can review them
3. **Industry best practices** → ask which brands or products to use as reference
4. **Starting from scratch** → explicitly tell the user that "no reference will affect the final quality," and establish a temporary system based on industry best practices

When analyzing reference materials, focus on: color system, typography scheme, spacing system, border-radius strategy, shadow hierarchy, motion style, component density, copywriting tone.

> **Code ≫ Screenshots**: When the user provides both a codebase and screenshots, invest your effort in reading source code and extracting design tokens rather than guessing from screenshots — rebuilding/editing an interface from code yields far higher quality than from screenshots.

#### When Adding to an Existing UI

This is more common than designing from scratch. **Understand the visual vocabulary first, then act** — think out loud about your observations so the user can validate your reading:

- **Color & tone**: The actual usage ratio of primary / neutral / accent colors? Does the copy feel engineer-oriented, marketing-oriented, or neutral?
- **Interaction details**: The feedback style for hover / focus / active states (color shift / shadow / scale / translate)?
- **Motion language**: Easing function preferences? Duration? Are transitions handled with CSS transition, CSS animation, or JS?
- **Structural language**: How many elevation levels? Card density — sparse or dense? Border-radius uniform or hierarchical? Common layout patterns (split pane / cards / timeline / table)?
- **Graphics & iconography**: Icon library in use? Illustration style? Image treatment?

Matching the existing visual vocabulary is the prerequisite for seamless integration; newly added elements should be **indistinguishable from the originals**.

### Step 3: Declare the Design System Before Writing Code

**Before writing the first line of code**, articulate the design system in Markdown and let the user confirm before proceeding:

```markdown
Design Decisions:
- Color palette: [primary / secondary / neutral / accent]
- Typography: [heading font / body font / code font]
- Spacing system: [base unit and multiples]
- Border-radius strategy: [large / small / sharp]
- Shadow hierarchy: [elevation 1–5]
- Motion style: [easing curves / duration / trigger]
```

### Step 4: Show a v0 Draft Early

**Don't hold back a big reveal.** Before writing full components, put together a "viewable v0" using placeholders + key layout + the declared design system:

- The goal of v0: **let the user course-correct early** — Is the tone right? Is the layout direction right? Are the variant directions right?
- Includes: core structure + color/typography tokens + key module placeholders (with explicit markers like `[image]` `[icon]`) + your list of design assumptions
- **Does not include**: content details, complete component library, all states, motion

A v0 with assumptions and placeholders is more valuable than a "perfect v1" that took 3x the time — if the direction is wrong, the latter has to be scrapped entirely.

### Step 5: Full Build

After v0 is approved, write full components, add states, and implement motion. Follow the technical specifications and design principles below. If an important decision point arises during the build (e.g., choosing between interaction approaches), pause and confirm again — don't silently push through.

### Step 6: Verification

Walk through the "Pre-delivery Checklist" item by item.

---


📂 **Technical Specifications** → see [`references/technical-specs.md`](references/technical-specs.md) (loaded on demand)


📂 **Design Principles** → see [`references/design-principles.md`](references/design-principles.md) (loaded on demand)
