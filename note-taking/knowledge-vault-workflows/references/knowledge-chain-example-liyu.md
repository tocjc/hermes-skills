# Knowledge Chain Example: Li Yu (李渔) Research Notes

This is a concrete example of a **knowledge chain** — 5 notes on the same topic added incrementally, cross-linked from each to all.

## The Chain

```
li-yu-research-guide.md                          ← 5 values + 5 hotspots
  ↓ links to
李渔全集研究报告.md                               ← 22 vols + 7 directions
  ↓ links to
李渔全集研究_硕士生视角.md                         ← version lineage + linguistics
  ↓ links to
《李渔全集》研究价值与学术前沿.md                    ← 10 scholars + 5 methodologies
  ↓ links to
李渔全集研究_硕士生深入挖掘.md                     ← market-literature crossover + 20 topics
```

## Cross-linking Pattern

Each note's "关联笔记" section lists all siblings with a one-line unique contribution summary:

```markdown
## 关联笔记

- [[li-yu-research-guide|李渔研究：学术价值、热点、方向与方法]] — 侧重5大研究价值与5个核心热点
- [[李渔全集研究报告]] — 侧重22卷册文献构成、7条选题方向、7类研究方法
- [[李渔全集研究_硕士生视角]] — 版本谱系、研究热点量化分布图、语言学选题方向
- [[《李渔全集》研究价值与学术前沿]] — 善本收藏机构、10位代表性学者、5层方法论体系
- [[李渔全集研究_硕士生深入挖掘]] — "文学—市场—舞台—生活"交叉空间定位、20个推荐选题
```

## Updating Pattern

When adding a new note to the chain:
1. Write the new note with "关联笔记" linking to all existing siblings
2. `patch` the most comprehensive existing note to add a backlink to the new one
3. `memory_vec(action='add', ...)` to index the new note

## Tags

Consistent tag taxonomy used:
- `[李渔, 明清文学, 戏曲理论, 硕士论文, 研究方法, 生活美学]` — core tags
- Additional tags added per note's unique focus: `[版本学, 语言学, 学术前沿, 数字人文, 文学商业化, 文化消费]`