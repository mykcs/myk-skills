## API Key Management

### Key Source Priority

```
--api_key CLI flag  >  .env file (ANYSEARCH_API_KEY)  >  system environment variable  >  anonymous access
```

**Anonymous access is available** with lower rate limits. An API Key is optional but recommended for higher rate limits. If no key is found, the agent may proceed with anonymous access. If the user wants higher limits, guide them to configure a key securely.

All bundled CLIs automatically load `.env` from the skill directory at startup (if present). The `.env` file format:

```
ANYSEARCH_API_KEY=<your_api_key_here>
```

### Scenarios

| Scenario | Behavior |
|----------|----------|
| **No key** | Proceed with anonymous access (lower rate limits). Optionally inform the user that a key provides higher limits. |
| **Has key** | Key is sent via `Authorization: Bearer <key>` header. Higher rate limits. |
| **Key exhausted — response returns new key** | API response contains `auto_registered` field with a new `api_key`. Agent MUST: (1) extract the key, (2) ask the user for explicit confirmation before saving, (3) after user approval, write it to `.env` file, (4) retry the failed call. |
| **Key exhausted — no new key returned** | Inform the user that the quota is exhausted and suggest configuring a new API key via `.env` or environment variable. |

**Key Configuration Guide** (display in the user's language if the user asks about API keys):

> **Optional: Configure an AnySearch API Key for higher rate limits.**
>
> To configure a key:
> 1. Visit https://anysearch.com/console/api-keys to create a free API key
> 2. Add it to your `.env` file: `ANYSEARCH_API_KEY=<your_api_key_here>`
> 3. Or set the environment variable: `export ANYSEARCH_API_KEY=<your_api_key_here>`
>
> For security, avoid pasting API keys directly in chat. Anonymous access remains available with lower limits.

### Persisting Keys

When a new key is obtained via auto-registration, the agent MUST:
1. Ask the user for explicit confirmation before saving the key to disk.
2. Inform the user: "A new API key was received. Save it to .env for future use?"
3. Only after user approval, update the `.env` file.
4. Inform the user where the key is stored and that it will be reused in future sessions.

When a user provides a key in chat, advise them to configure it via `.env` or environment variable instead, for security.
