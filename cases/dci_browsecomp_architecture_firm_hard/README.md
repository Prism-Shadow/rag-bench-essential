# Restricted DCI case

`dci_browsecomp_architecture_firm_hard` 是固定 15-case suite 的一部分，来自 BrowseComp-Plus / DCI Bench。

上游要求禁止将 benchmark 明文以普通在线文件发布，因此本仓库不包含：

- `task.md`
- materialized `data/corpus/`

`data/README.md` 只记录上游数据来源。受限内容应从官方
DCI/BrowseComp-Plus 分发渠道获取，不得回写到 Git。
