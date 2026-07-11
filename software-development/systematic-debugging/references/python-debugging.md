# Python Debugging Reference — pdb + debugpy

Full reference for Python debugging techniques, absorbed from the former `python-debugpy` skill.

## Overview

| Tool | When |
|------|------|
| **`breakpoint()` + pdb** | Local, interactive, simplest. Add `breakpoint()` in the source, run normally, get a REPL at that line. |
| **`python -m pdb`** | Launch an existing script under pdb with no source edits. Useful for quick poking. |
| **`debugpy`** | Remote / headless / "attach to already-running process." Talks DAP, scriptable from terminal, works for long-lived processes (gateway, daemon, PTY children). |

**Start with `breakpoint()`.** It's the cheapest thing that works.

## pdb Quick Reference

| Command | Action |
|---------|--------|
| `h` / `h cmd` | help |
| `n` | next line (step over) |
| `s` | step into |
| `r` | return from current function |
| `c` | continue |
| `unt N` | continue until line N |
| `j N` | jump to line N (same function only) |
| `l` / `ll` | list source around current line / full function |
| `w` | where (stack trace) |
| `u` / `d` | move up / down in the stack |
| `a` | print args of the current function |
| `p expr` / `pp expr` | print / pretty-print expression |
| `display expr` | auto-print expr on every stop |
| `b file:line` | set breakpoint |
| `b func` | break on function entry |
| `b file:line, cond` | conditional breakpoint |
| `cl N` | clear breakpoint N |
| `tbreak file:line` | one-shot breakpoint |
| `!stmt` | execute arbitrary Python (assignments included) |
| `interact` | drop into full Python REPL in current scope (Ctrl+D to exit) |
| `q` | quit |

The `interact` command is the most powerful — you can import anything, inspect complex objects, even call methods that mutate state. Locals are read-only by default; use `!x = 42` from the `(Pdb)` prompt to mutate.

## Recipe 1: Local breakpoint

```python
def compute(x, y):
    result = some_helper(x)
    breakpoint()           # <-- drops into pdb here
    return result + y
```

**Don't forget to remove `breakpoint()` before committing:**
```bash
rg -n 'breakpoint\\(\\)' --type py
```

## Recipe 2: Launch a script under pdb

```bash
python -m pdb path/to/script.py arg1 arg2
(Pdb) b path/to/script.py:42
(Pdb) c
```

## Recipe 3: Debug a pytest test

```bash
# Drop to pdb on failure
scripts/run_tests.sh tests/path/to/test_file.py::test_name --pdb

# Drop to pdb at the START of the test
scripts/run_tests.sh tests/path/to/test_file.py::test_name --trace

# Show locals in tracebacks without pdb
scripts/run_tests.sh tests/path/to/test_file.py --showlocals --tb=long
```

Note: `scripts/run_tests.sh` uses xdist (`-n 4`) by default, and pdb does NOT work under xdist:
```bash
scripts/run_tests.sh tests/foo_test.py::test_bar --pdb -p no:xdist
# or
source .venv/bin/activate
python -m pytest tests/foo_test.py::test_bar --pdb
```

## Recipe 4: Post-mortem on exceptions

```python
import pdb, sys
try:
    run_the_thing()
except Exception:
    pdb.post_mortem(sys.exc_info()[2])
```

Or wrap an entire script:
```bash
python -m pdb -c continue script.py
```

Or set a global hook:
```python
import sys
def excepthook(etype, value, tb):
    import pdb; pdb.post_mortem(tb)
sys.excepthook = excepthook
```

## Recipe 5: Remote debug with debugpy

Hook into long-lived Hermes processes (gateway, tui_gateway, daemon):

### Pattern A: Source-edit (wait for debugger at launch)

```python
import debugpy
debugpy.listen(("127.0.0.1", 5678))
print("debugpy listening on 5678, waiting for client...", flush=True)
debugpy.wait_for_client()
debugpy.breakpoint()
```

### Pattern B: No source edit

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client your_script.py arg1
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m your.module
```

### Pattern C: Attach to running process

```bash
python -m debugpy --listen 127.0.0.1:5678 --pid <pid>
```

Fix ptrace limits if needed:
```bash
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```

### Client connection: remote-pdb (preferred for terminal agents)

```bash
pip install remote-pdb
```

In code:
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)
```

Then from terminal:
```bash
nc 127.0.0.1 4444
```

`remote-pdb` is the cleanest agent-friendly choice. Use `debugpy` only when IDE integration is needed.

## Debugging Hermes-specific Processes

### tui_gateway subprocess (spawned by `hermes --tui`)

```python
# In tui_gateway/server.py near serve()
import debugpy
debugpy.listen(("127.0.0.1", 5678))
debugpy.wait_for_client()
```

Or use remote-pdb at a specific RPC handler:
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)
```

### `_SlashWorker` subprocess

Same pattern — `remote-pdb` with `set_trace()` inside the worker's `exec` path.

### Gateway (`gateway/run.py`)

Use `remote-pdb` at a handler, or `debugpy` with `--wait-for-client`.

## Common Pitfalls

1. **pdb under pytest-xdist silently does nothing.** Always use `-p no:xdist` or `-n 0`.
2. **`breakpoint()` in CI hangs the process.** Never commit it. Add a pre-commit grep.
3. **`PYTHONBREAKPOINT=0`** disables all `breakpoint()` calls. Check the env.
4. **`debugpy.listen` blocks only with `wait_for_client()`.** Without it, execution continues.
5. **Attach to PID fails on hardened kernels.** Use `ptrace_scope=0` or launch under debugpy from the start.
6. **Threads.** `pdb` only debugs the current thread. Use `debugpy` for multithreaded code.
7. **asyncio.** `pdb` works in coroutines but `await` in pdb requires Python 3.13+. For 3.11/3.12, use `asyncio.run_coroutine_threadsafe` tricks.
8. **`scripts/run_tests.sh` strips credentials.** Debug with raw `pytest` first to repro.
9. **Forking.** pdb does not follow forks. Each child needs its own `breakpoint()`.