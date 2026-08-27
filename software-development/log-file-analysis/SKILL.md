---
name: log-file-analysis
description: Analyze large log files to extract ERROR/WARN patterns.
---

# Log File Analysis

Systematic workflow for turning a large log file (tens of thousands of lines) into a concise, evidence-backed diagnosis report. Proven on a 70k-line Java/Spring (goldwind-bs.log) case.

## When to use
- User provides a `.log` file and asks to analyze/extract/汇总 errors, warnings, timeouts, exceptions.
- User wants root-cause analysis or a Markdown report of log problems.
- Any debugging task where the evidence is a timestamped log.

## Workflow

### 1. Size up the file first (never read it raw)
```bash
wc -l /path/app.log
ls -lh /path/app.log
```
A 70k-line / 5MB log must NOT be pulled into context with `read_file` (truncates at ~100k chars and floods tokens). Use grep/awk pipelines instead.

### 2. Count severity levels
```bash
grep -c ' ERROR ' /path/app.log
grep -c ' WARN '  /path/app.log
grep -c 'Exception' /path/app.log
grep -c 'failed' /path/app.log
```
Note the exact log format: Java/Spring lines are `TIMESTAMP [thread] LEVEL logger - message`. Match on the literal `' ERROR '` with spaces (level is padded) — `'^... ERROR\s'` regexes often fail on the millisecond timestamp.

### 3. Categorize messages (the core move)
Strip the common timestamp/thread prefix, then `sort | uniq -c | sort -rn` to collapse repeated messages into buckets:
```bash
grep ' ERROR ' /path/app.log | sed 's/.*\] //' | sort | uniq -c | sort -rn | head -40
grep ' WARN '  /path/app.log | sed 's/.*\] //' | sort | uniq -c | sort -rn | head -30
```
For sub-categorization, further `sed` to erase varying fields (table names, timestamps, attempt numbers, IP ports) so related messages group:
```bash
grep ' ERROR ' file | sed 's/.*\] //' | sed 's/ (table:.*//' | sed 's/ on attempt.*//' | sort | uniq -c | sort -rn
```

### 4. Dig into exceptions and DB errors
```bash
grep 'Exception' file | sed 's/.*\] //' | sort | uniq -c | sort -rn
grep 'SQL error or missing database' file | sed 's/.* - //' | sort | uniq -c | sort -rn
```

### 5. Establish time range and distribution
```bash
head -1 file | cut -d' ' -f1-2
tail -1 file | cut -d' ' -f1-2
grep ' ERROR ' file | grep -oP '^\S+ \S+' | sort | uniq -c | sort -rn | head
```
The busiest-minute distribution reveals whether errors are constant, bursting, or tied to a schedule.

### 6. Correlate the "weird constant" values
Look for a fixed/anomalous value repeated across many errors (e.g. a constant checksum `0xB2466F51`, a loopback address `0.0.0.0:6000`). A constant across many "different" failures is the smoking-gun signature of a misconfiguration or a single broken upstream.

## Diagnostic frame
After categorizing, ask: what is the *root* cause that cascades into the others? Common pattern: misconfigured upstream address → connection refused → all dependent requests fail → DB never updates → queries return empty → system "spins" retrying. Report the root cause first, then list knock-on effects.

## Report structure
Write a Markdown report with:
1. **Overview** — file, time range, total lines, ERROR/WARN counts + percentages
2. **ERROR breakdown** — categorized table (category, count, %)
3. **WARN breakdown** — categorized table
4. **Root-cause analysis** — each problem with evidence (exact log lines) and a confidence-ranked fix
5. **Severity-prioritized fix list** — P0/P1/P2 table
6. **Timeline** — the failure lifecycle

Keep the report evidence-grounded: quote real log lines, never invent missing data.

## Pitfalls
- Do NOT `read_file` a large log into context; grep pipelines only.
- Timestamps include milliseconds — match levels with `' ERROR '` (spaces), not anchored regexes.
- `sort | uniq -c | sort -rn` is the workhorse; always use it before trying to read individual lines.
- Distinguish "symptom" from "root cause" — a constant repeated value across many message types is the root; the individual IO/SQL errors are symptoms.
- If the log is a single day and errors are constant the whole time, say the system never succeeded (not "occasionally failed") — that's the honest reading.

## References
- `references/goldwind-bs-case.md` — worked example: 70k-line Spring log, PPC connection misconfiguration, full categorization commands.