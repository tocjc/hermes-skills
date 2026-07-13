# Knowledge Base Organisation Patterns

Patterns for creating structured multi-note knowledge bases in an Obsidian vault,
with rich bidirectional linking.

## Anatomy of a Good Knowledge Base

```
topic/
├── README.md          ← Hub page: overview, learning paths, data-flow diagram
├── core-concept.md    ← Foundational theory, linked by every dependent note
├── sub-area-1.md      ← Specific domain, links back to core-concept
├── sub-area-2.md      ← Another sub-domain
├── sub-area-3.md      ← ...
├── reference.md       ← Tools, CLI commands, API docs
└── cases.md           ← Real-world examples (template for future entries)
```

## Linking Strategy

| Goal | Pattern | Example |
|------|---------|---------|
| Cross-ref core idea | `[[Note#Section]]` | `[[基础理论#采样定理]]` |
| Reference whole note | `[[Note Name]]` | `[[故障诊断]]` |
| Custom display text | `[[Note\|alias]]` | `[[FFT 详解\|FFT]]` |
| Embed content inline  | `![[Note]]` | `![[故障诊断#诊断流程]]` |
| Mark reusable block   | `^block-id` | `^citation` for pinpoint linking |

## README Hub Page Checklist

- [ ] 知识体系目录（树形或列表）
- [ ] 学习路径建议（入门 / 进阶 / 实战）
- [ ] 数据流 / 流程示意图（ASCII 或 Mermaid）
- [ ] 各笔记的前置依赖关系
- [ ] `![[assets/knowledge-graph.svg]]`（如已生成图谱）

## Useful YAML Frontmatter

```yaml
---
created: 2026-07-13
tags: [vibration, signal-processing, index]
aliases: [振动信号, 振动分析总览]
---
```

## Pitfalls

- Don't put the hub page inside `.obsidian/` — it won't show in file explorer.
- Keep note names short (≤ 20 chars) so `[[` autocomplete is fast.
- Mark too-rarely-linked notes with `related:` in frontmatter rather than forcing a link.
- When creating 8+ notes, batch `write_file` calls (parallel) for speed, not serial.