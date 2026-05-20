# Anti-Pattern Scan — Without Skill

Agent hit 429 rate limit before finishing and committing.

## Changes Made (partial)
- Removed ViewTransitions from src/pages/index.astro
- Replaced Astro.glob with import.meta.glob
- Kept define:vars (not removed)
- No changes to Gallery.astro (format props still present)

## NOT Done
- Did NOT remove define:vars
- Did NOT remove Image format props
- Did NOT commit changes
