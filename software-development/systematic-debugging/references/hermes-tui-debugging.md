# Debugging Hermes TUI Slash Commands

Full reference for debugging slash commands in the Hermes TUI, absorbed from the former `debugging-hermes-tui-commands` skill.

## Architecture

```
Python backend (hermes_cli/commands.py)     <- canonical COMMAND_REGISTRY
       │
       ▼
TUI gateway (tui_gateway/server.py)         <- slash.exec / command.dispatch
       │
       ▼
TUI frontend (ui-tui/src/app/slash/)        <- local handlers + fallthrough
```

Command definitions must be registered consistently across Python and TypeScript. The Python `COMMAND_REGISTRY` is the source of truth for: CLI dispatch, gateway help, Telegram BotCommand menu, Slack subcommand map, and autocomplete data shipped to Ink.

## Investigation Steps

1. **Check TUI frontend:**
   ```bash
   search_files --pattern "/commandname" --file_glob "*.ts" --path ui-tui/
   search_files --pattern "/commandname" --file_glob "*.tsx" --path ui-tui/
   ```

2. **Examine TUI command definition:**
   ```bash
   read_file ui-tui/src/app/slash/commands/core.ts
   search_files --pattern "commandname" --path ui-tui/src/app/slash/commands --target files
   ```

3. **Check Python backend:**
   ```bash
   search_files --pattern "CommandDef" --file_glob "*.py" --path hermes_cli/
   search_files --pattern "commandname" --path hermes_cli/commands.py --context 3
   ```

4. **Examine gateway implementation:**
   ```bash
   search_files --pattern "complete.slash|slash.exec" --path tui_gateway/
   ```

## Fix: Missing Command Autocomplete

1. Add a `CommandDef` to `COMMAND_REGISTRY` in `hermes_cli/commands.py`:
   ```python
   CommandDef("commandname", "Description", "Session",
              cli_only=True, aliases=("alias",),
              args_hint="[arg1|arg2|arg3]",
              subcommands=("arg1", "arg2", "arg3")),
   ```

2. Choose availability: `cli_only=True` (CLI/TUI only), `gateway_only=True` (messaging only), neither (everywhere), or `gateway_config_gate="display.foo"` (config-gated).

3. Add handler in `HermesCLI.process_command()` in `cli.py`:
   ```python
   elif canonical == "commandname":
       self._handle_commandname(cmd_original)
   ```

4. For gateway-available commands, add handler in `gateway/run.py`:
   ```python
   if canonical == "commandname":
       return await self._handle_commandname(event)
   ```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Command shows in TUI but not in autocomplete | Missing from `COMMAND_REGISTRY` in Python | Add `CommandDef` — autocomplete data ships from Python |
| Command shows in autocomplete but doesn't work | No handler in `tui_gateway/server.py` or frontend | Add handler at the right layer |
| CLI vs TUI behavior differs | Different implementations | Check `cli.py::process_command` vs TUI local handler |
| Config persists but UI doesn't update | Only `config.set`, no live state patch | Also call `patchUiState(...)` and thread state through render components |
| Gateway silently ignores command | Not in `GATEWAY_KNOWN_COMMANDS` | `cli_only=True` commands need `gateway_config_gate` if they should also work in gateway |

## Debugging Tactics

- **Python side hangs:** use `python-debugpy` to break inside `_SlashWorker.exec` or the command handler. `remote-pdb` at handler entry is fastest.
- **Ink side not reacting:** use `node-inspect-debugger` to break in `app.tsx` slash dispatch or local command branch.
- **Registry mismatch:** compare `COMMAND_REGISTRY` entry against TUI's local command list side-by-side.

## Pitfalls

- Don't forget the category field in `CommandDef` (Session, Configuration, Tools & Skills, Info, Exit).
- `aliases` tuple is the only place aliases need registering — everything downstream derives from it.
- After adding live UI state, search every consumer of the old prop/helper and thread the new state through all render paths (both live `StreamingAssistant`/`ToolTrail` and transcript/pending `MessageLine` rows).
- Rebuild: `npm --prefix ui-tui run build` before testing.

## Verification

After fixing:
```bash
cd <hermes-agent> && npm --prefix ui-tui run build
hermes --tui  # Type `/` and verify autocomplete
```
Read `~/.hermes/config.yaml` to confirm config updates persist. For gateway commands, run `scripts/run_tests.sh tests/gateway/`.