# Restricted DCI case

`dci_browsecomp_architecture_firm_hard` 是固定 15-case suite 的一部分，来自 BrowseComp-Plus / DCI Bench。

上游要求禁止将 benchmark 明文以普通在线文件发布，因此本仓库不包含：

- `task.md`
- `truth/`
- materialized `data/corpus/`

`env.md` 和 `data/README.md` 仅记录运行环境与上游数据来源。授权用户应从官方 DCI/BrowseComp-Plus 分发渠道在本地解密和 materialize，不得将明文回写到 Git。
