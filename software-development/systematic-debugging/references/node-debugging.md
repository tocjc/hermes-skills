# Node.js Debugging Reference — node inspect + CDP

Full reference for Node.js debugging techniques, absorbed from the former `node-inspect-debugger` skill.

When `console.log` isn't enough, drive Node's built-in V8 inspector programmatically. Two tools:

- **`node inspect`** — built-in, zero install, CLI REPL. Best for quick poking.
- **CDP via `chrome-remote-interface`** — scriptable from Node/Python; best for automating many breakpoints or collecting state across runs.

**Prefer `node inspect` first.**

## `node inspect` REPL Reference

Launch paused on first line:
```bash
node inspect path/to/script.js
node --inspect-brk $(which tsx) path/to/script.ts   # TypeScript
```

| Command | Action |
|---------|--------|
| `c` or `cont` | continue |
| `n` or `next` | step over |
| `s` or `step` | step into |
| `o` or `out` | step out |
| `pause` | pause running code |
| `sb('file.js', 42)` | set breakpoint at file.js:42 |
| `sb(42)` | set breakpoint at current file line 42 |
| `sb('functionName')` | break when function is called |
| `cb('file.js', 42)` | clear breakpoint |
| `breakpoints` | list all breakpoints |
| `bt` | backtrace (call stack) |
| `list(5)` | show 5 lines of source around current position |
| `watch('expr')` | evaluate expr on every pause |
| `watchers` | show watched expressions |
| `repl` | drop into REPL in current scope (Ctrl+C to exit) |
| `exec expr` | evaluate expression once |
| `restart` | restart script |
| `kill` | kill the script |
| `.exit` | quit debugger |

## Attaching to a Running Process

```bash
# Enable inspector on existing process
kill -SIGUSR1 <pid>

# Attach the debugger CLI
node inspect -p <pid>
# or by URL
node inspect ws://127.0.0.1:9229/<uuid>
```

Start with inspector from beginning:
```bash
node --inspect script.js           # keep running, listen on 9229
node --inspect-brk script.js       # pause on first line
```

TypeScript via tsx:
```bash
node --inspect-brk --import tsx script.ts
```

## Programmatic CDP (for automation)

Install: `npm i -g chrome-remote-interface`

Driver script template:
```javascript
const CDP = require('chrome-remote-interface');

(async () => {
  const client = await CDP({ port: 9229 });
  const { Debugger, Runtime } = client;

  Debugger.paused(async ({ callFrames, reason }) => {
    const top = callFrames[0];
    console.log(`PAUSED: ${reason} @ ${top.url}:${top.location.lineNumber + 1}`);

    // Walk scopes for locals
    for (const scope of top.scopeChain) {
      if (scope.type === 'local' || scope.type === 'closure') {
        const { result } = await Runtime.getProperties({
          objectId: scope.object.objectId,
          ownProperties: true,
        });
        for (const p of result) {
          console.log(`  ${scope.type}.${p.name} =`, p.value?.value ?? p.value?.description);
        }
      }
    }
    await Debugger.resume();
  });

  await Runtime.enable();
  await Debugger.enable();
  await Debugger.setBreakpointByUrl({
    urlRegex: '.*app\\.tsx$',
    lineNumber: 119,
    columnNumber: 0,
  });
  await Runtime.runIfWaitingForDebugger();
})();
```

## Debugging Hermes ui-tui

### Debug a single Ink component

```bash
cd <hermes-agent>/ui-tui
npm run build
node --inspect-brk dist/entry.js
# In another terminal:
node inspect -p <node pid>
# debug> sb('dist/app.js', 220)
# debug> cont
# When paused: repl → inspect props, state refs, etc.
```

### Debug a running `hermes --tui`

```bash
hermes --tui &
TUI_PID=$(pgrep -f 'ui-tui/dist/entry' | head -1)
kill -SIGUSR1 "$TUI_PID"
curl -s http://127.0.0.1:9229/json/list | jq -r '.[0].webSocketDebuggerUrl'
node inspect ws://127.0.0.1:9229/<uuid>
```

### Run vitest tests under debugger

```bash
cd <hermes-agent>/ui-tui
node --inspect-brk ./node_modules/vitest/vitest.mjs run --no-file-parallelism src/app/foo.test.tsx
```

## Heap Snapshots & CPU Profiles (Non-interactive)

```javascript
// CPU profile
await client.Profiler.enable();
await client.Profiler.start();
await new Promise(r => setTimeout(r, 5000));
const { profile } = await client.Profiler.stop();
require('fs').writeFileSync('/tmp/cpu.cpuprofile', JSON.stringify(profile));

// Heap snapshot
await client.HeapProfiler.enable();
const chunks = [];
client.HeapProfiler.addHeapSnapshotChunk(({ chunk }) => chunks.push(chunk));
await client.HeapProfiler.takeHeapSnapshot({ reportProgress: false });
require('fs').writeFileSync('/tmp/heap.heapsnapshot', chunks.join(''));
```

## Common Pitfalls

1. **Wrong line numbers in TS source.** Breakpoints hit emitted JS, not `.ts`. Use built `dist/*.js` or enable sourcemaps with `node --enable-source-maps`.
2. **`--inspect` vs `--inspect-brk`.** `--inspect` doesn't pause; use `--inspect-brk` to set breakpoints before any code runs.
3. **Port collisions.** Default is `9229`. Use `--inspect=0` (random port) and check `/json/list`.
4. **Child processes.** `--inspect` on parent doesn't inspect children. Use `NODE_OPTIONS='--inspect-brk'` to propagate.
5. **Background kills.** If you Ctrl+C out of `node inspect` while target is paused, target stays paused. `cont` first or `kill`.
6. **`--inspect=0.0.0.0:9229`** exposes arbitrary code execution. Always bind to `127.0.0.1` unless isolated.