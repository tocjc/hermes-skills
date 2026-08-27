# Worked Example: goldwind-bs.log (70k-line Spring log)

Real case used to validate this skill. A Java/Spring Boot backend (`c.g.service` package) generating a PPC (power-plant controller) data-integration log.

## Scalability data point
- 70,469 lines / 4.7 MB / single day (63 min window)
- ERROR: 1,310 (1.86%), WARN: 760 (1.08%), Exception: 44
- `read_file` truncated at ~100k chars and flooded context — must use grep pipelines.

## Format
```
2026-08-07 08:38:18.403 [http-nio-0.0.0.0-8080-exec-3] DEBUG c.g.service.impl.HomeServiceImpl - message
```
Level is space-padded. `' ERROR '` / `' WARN '` (with surrounding spaces) matches reliably; anchored regexes on the timestamp fail.

## Root cause found
Misconfigured upstream address: `Failed to connect to PPC: 0.0.0.0:6000` — the system connected to the loopback instead of the real PPC device. Everything cascaded:
1. connection refused → 40× "Failed to connect"
2. 816× "IO error" (Socket closed / Connection reset / Invalid magic number)
3. 361× "All 2 retry attempts failed"
4. DB never updated → "No data found in home_2 table" (365 WARN) → re-request PPC → loop
5. Constant checksum `0xB2466F51` across many "different" checksum-mismatch errors = signature of one broken upstream returning garbage

## Secondary findings
- SQLite schema drift: INSERT column names (`Data_PCCAnaN_s_F`, `DATATYPE_UINTN`) not present in `home_0/1/3` tables — code built column names from variable names, and PPC fed type strings into names.
- Empty payloads (278 WARN) + socket timeouts (84 WARN) — broken upstream returning empty/slow responses.
- Missing variable_mapping config → "No variable mappings found" / "Unknown table name".

## Key commands that worked
```bash
grep -c ' ERROR ' /path                  # 1310
grep ' ERROR ' /path | sed 's/.*\] //' | sort | uniq -c | sort -rn | head -40
grep 'Exception' /path | sed 's/.*\] //' | sort | uniq -c | sort -rn
grep 'SQL error or missing database' /path | sed 's/.* - //' | sort | uniq -c | sort -rn
head -1 /path | cut -d' ' -f1-2; tail -1 /path | cut -d' ' -f1-2
grep ' ERROR ' /path | grep -oP '^\S+ \S+' | sort | uniq -c | sort -rn | head  # per-minute burst
```

## Lesson
A constant anomalous value (`0.0.0.0:6000`, `0xB2466F51`) carried across many distinct error types is the root cause, not the individual errors. Fix the config first, then the DB schema, then the missing mappings.