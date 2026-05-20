---
name: hello-world
description: Greets the user by name with a personalized message. Use this skill whenever the user wants to be greeted, says hello, or asks for a greeting with their name. Works even when the user doesn't explicitly mention "greeting" - phrases like "say hi to me", "greet me", "hello there", or any request to generate a personalized greeting should trigger this skill. If no name is provided, ask the user for their name before proceeding.
disable-model-invocation: true
---

# Hello World Skill

This skill greets the user with their name in a friendly way.

## Workflow

1. **Get the user's name**: If not provided in the conversation, ask the user "What is your name?"
2. **Generate a greeting**: Create a warm, friendly greeting message that includes the user's name
3. **Save to file**: Write the greeting to `/tmp/hello-greeting.txt`
4. **Display**: Read the file back and show the greeting to the user

## Example

**Input**: "Hello, my name is Alice"

**Output**:
```
Hello, Alice! Welcome! Your greeting has been saved.
```

## Output Format

Display the greeting clearly to the user, then confirm the file was saved to `/tmp/hello-greeting.txt`.