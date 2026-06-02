---
name: eval-viewer
description: Generate and view evaluation review sessions for LLM agent outputs. Use when reviewing batches of agent traces, comparing runs, or annotating eval results.
when_to_use: Review LLM agent eval results, generate shareable review pages, annotate trace outputs
---

# Eval Viewer

Generate and view evaluation review sessions for LLM agent outputs.

## What's in this skill

- `generate_review.py` — Generates `viewer.html` from a session of agent trace data
- `viewer.html` — Static review UI (open in browser to inspect traces)

## Usage

```bash
# Generate a review page from a session
python3 generate_review.py --session <session-id> --output viewer.html

# Open the generated page
open viewer.html
```

## When to use

- Reviewing batches of agent traces
- Comparing multiple eval runs side-by-side
- Annotating outputs for fine-tuning datasets
- Sharing eval results with collaborators
