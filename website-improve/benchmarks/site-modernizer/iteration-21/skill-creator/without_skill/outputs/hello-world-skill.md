---
name: hello-world
description: Greets the user by name. Asks for name if not provided, generates a greeting, saves to /tmp/hello-greeting.txt, and displays the result.
---

# Hello World Skill

This skill greets the user with their name.

## Workflow

1. Check if the user's name was provided in the request
2. If no name provided, ask the user for their name
3. Generate a personalized greeting
4. Save the greeting to `/tmp/hello-greeting.txt`
5. Read back the file and display the greeting

## Implementation

The skill should be invoked with `/hello-world` followed by an optional name parameter.

### Example Usage

```
/hello-world
/hello-world Alice
```

### Output File

The greeting is saved to `/tmp/hello-greeting.txt` with the format:
```
Hello, {name}! Welcome to Claude Code.
```

Generated on: 2026/05/15
