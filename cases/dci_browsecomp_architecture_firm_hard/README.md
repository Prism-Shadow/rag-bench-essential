# DCI case materialization

`dci_browsecomp_architecture_firm_hard` 是固定 15-case suite 的一部分，来自 BrowseComp-Plus / DCI Bench。

本仓库包含实际实验使用的 canonical `task.md` 和外部评分材料，但不直接提交约
1.74 GB 的 BrowseComp-Plus corpus。官方来源为：

- [DCI benchmark dataset](https://huggingface.co/datasets/DCI-Agent/dci-bench)
- [DCI corpus dataset](https://huggingface.co/datasets/DCI-Agent/corpus)
- [官方 BrowseComp-Plus 解密脚本](https://github.com/DCI-Agent/DCI-Agent-Lite/blob/271f37e71f053bf0c99c05ce6d2fb53b841d922e/scripts/bcplus_eval/extract_bcplus_qa.py)

安装依赖后运行：

```bash
pip install -r requirements-eval.txt
python scripts/materialize_dci.py
```

该命令会从 Hugging Face 下载包含 query 861 的官方 benchmark shard 和
BrowseComp-Plus corpus，在 `.bench-cache/dci/` 下验证/导出，并创建未跟踪的
`data/corpus` 符号链接。之后即可使用标准 `scripts/stage_case.py`。

直接下载文件：

- [query shard 0, about 508 MB](https://huggingface.co/datasets/DCI-Agent/dci-bench/resolve/main/data/browsecomp-plus/test-00000-of-00006.parquet?download=true)
- [BrowseComp-Plus corpus, about 1.74 GB](https://huggingface.co/datasets/DCI-Agent/corpus/resolve/main/browsecomp_plus/data.parquet?download=true)
