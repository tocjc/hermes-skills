---
name: hermes-plugin-authoring
description: Build and install Hermes Agent memory provider plugins. Write a MemoryProvider subclass, register via plugin.yaml + __init__.py, use register(ctx) entry point.
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [hermes, plugins, memory, development]
    related_skills: [hermes-agent]
---

# Hermes Plugin Authoring — Memory Providers

Build a custom Hermes Agent memory provider plugin. Covers the MemoryProvider ABC, directory discovery rules, registration, and common pitfalls.

> **Trigger**: User asks you to build/install a custom memory provider for Hermes, or you need to extend Hermes with persistent vector/semantic memory.

## Architecture

### Directory Discovery

Memory provider plugins are discovered from **two locations**:

| Source | Path | Precedence |
|--------|------|-----------|
| Bundled | `{hermes-source}/plugins/memory/<name>/` | **Higher** (wins name collisions) |
| User-installed | `$HERMES_HOME/plugins/<name>/` | Lower |

**Critical discovery rule**: User plugins go DIRECTLY under `$HERMES_HOME/plugins/<name>/`, NOT `$HERMES_HOME/plugins/memory/<name>/`. The `_is_memory_provider_dir()` heuristic scans `$HERMES_HOME/plugins/` for subdirectories containing `register_memory_provider` or `MemoryProvider` in their `__init__.py`.

### Minimal File Structure

```
$HERMES_HOME/plugins/<name>/
├── __init__.py      # MemoryProvider subclass + register(ctx)
├── plugin.yaml      # Metadata + pip_dependencies
└── README.md        # Setup instructions
```

### plugin.yaml

```yaml
name: my-provider
version: 1.0.0
description: "Short description."
hooks:
  - on_session_end      # list your implemented hooks
pip_dependencies:       # auto-installed by `hermes memory setup`
  - my-package
```

The `pip_dependencies` field causes `hermes memory setup` to auto-install missing packages via `uv pip install` or `python -m pip install`.

## MemoryProvider ABC

Import from `agent.memory_provider`:

```python
from agent.memory_provider import MemoryProvider
```

### Required Methods

| Method | Called When | Purpose |
|--------|------------|---------|
| `name` (property) | Always | Return provider identifier string |
| `is_available()` | Agent init | Quick check (no network calls) |
| `initialize(session_id, **kwargs)` | Agent startup | Set up DB, clients, connections |
| `get_tool_schemas()` | After init | Return tool schemas for agent |
| `handle_tool_call(tool_name, args, **kwargs)` | Agent uses your tools | Dispatch to handlers |
| `get_config_schema()` | Setup wizard | Declare config fields for `hermes memory setup` |
| `save_config(values, hermes_home)` | Setup completion | Write non-secret config to disk |

### Optional Hooks

| Method | Called | Use Case |
|--------|--------|----------|
| `system_prompt_block()` | System prompt assembly | Tell agent about memory store state |
| `prefetch(query, *, session_id="")` | Before each API call | Return relevant memories as context |
| `sync_turn(user, assistant, *, session_id="", messages=None)` | After each completed turn | Persist conversation content |
| `on_session_end(messages)` | Conversation ends | Final extraction / flush |
| `on_memory_write(action, target, content)` | Built-in memory writes | Mirror to your backend |
| `shutdown()` | Process exit | Clean up connections |

### Threading Contract

**`sync_turn()` MUST be non-blocking.** If your backend has latency, run work in a daemon thread:

```python
def sync_turn(self, user_content, assistant_content, **kwargs):
    def _sync():
        try: self._backend.ingest(...)
        except Exception as e: logger.warning("Sync failed: %s", e)

    t = threading.Thread(target=_sync, daemon=True)
    t.start()
```

### Key Detail: `messages` Parameter

`sync_turn()` receives an optional `messages` parameter (OpenAI-style conversation context). When present, it includes user/assistant messages, tool calls, and tool results. Providers that don't need raw turn context can omit this parameter; Hermes continues calling with the legacy signature.

## Registration Entry Point

```python
def register(ctx) -> None:
    """Called by the memory plugin discovery system."""
    ctx.register_memory_provider(MyMemoryProvider())
```

The `_ProviderCollector` class in `plugins/memory/__init__.py` simulates a plugin context. It captures `register_memory_provider()` calls and ignores others (`register_tool`, `register_hook`, `register_cli_command`).

## Config Schema Pattern

Fields with `secret: True` and `env_var` go to `.env`. Non-secret fields go to `save_config()`.

```python
def get_config_schema(self):
    return [
        {"key": "api_key", "description": "API key", "secret": True,
         "required": True, "env_var": "MY_API_KEY"},
        {"key": "db_path", "description": "Database path",
         "default": f"{display_hermes_home()}/store.db"},
    ]
```

Keep schema minimal — only fields the user must configure. Document optional settings in the README or a separate config file.

## Profile Isolation

All storage paths MUST use the `hermes_home` kwarg from `initialize()`, not hardcoded `~/.hermes`. The `hermes_constants.get_hermes_home()` function returns the profile-scoped path.

## Activation

```bash
hermes memory setup          # interactive picker + config
# OR set directly:
hermes config set memory.provider <name>
```

Plugin takes effect after `/reset` (new session).

## References

- Full developer docs: `{hermes-source}/website/docs/developer-guide/memory-provider-plugin.md`
- Reference implementation: `plugins/memory/holographic/` (local SQLite-based provider)
- cfg_get utility: `from hermes_cli.config import cfg_get`

## Pitfalls

### ❌ Wrong directory for user plugins
**Symptom**: `hermes memory setup` or `hermes memory status` doesn't see your plugin.

**Fix**: Place plugin at `$HERMES_HOME/plugins/<name>/`, NOT `$HERMES_HOME/plugins/memory/<name>/`. The discovery scans `$HERMES_HOME/plugins/` directly for subdirectories matching the heuristic.

### ❌ Plugin not showing as "available"
**Cause**: `is_available()` raises an exception or returns False. The discovery system catches exceptions and marks it unavailable.

**Fix**: Ensure `is_available()` is a simple check — no network calls, no heavy imports. Just check the import works.

### ❌ Relative imports failing
**Symptom**: `ModuleNotFoundError: No module named '_hermes_user_memory'`

**Cause**: User-installed plugins are loaded under the `_hermes_user_memory` namespace package, but its parent wasn't registered in `sys.modules`.

**Fix**: The discovery system handles this automatically via `_register_synthetic_package()`. If you hit this, ensure your `__init__.py` doesn't use relative imports that bypass the loader.

### ❌ Changes not visible until /reset
Memory provider plugins are loaded at session start, not mid-conversation. After install + activation, always `/reset` or start a new session.

### ❌ `sync_turn()` blocking the main loop
If your backend is slow, the agent's turn resolution stalls. Always use a daemon thread for sync operations (see threading contract above).