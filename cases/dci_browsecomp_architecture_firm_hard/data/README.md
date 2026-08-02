# Data

This case uses BrowseComp-Plus data distributed by `DCI-Agent/dci-bench` and
`DCI-Agent/corpus`.

- Benchmark: BrowseComp-Plus
- Source dataset: [`DCI-Agent/dci-bench`](https://huggingface.co/datasets/DCI-Agent/dci-bench)
- Corpus dataset: [`DCI-Agent/corpus`](https://huggingface.co/datasets/DCI-Agent/corpus)
- Corpus shape: approximately 100,195 documents

Use `python scripts/materialize_dci.py` from the repository root. The script
downloads these official artifacts:

- [`test-00000-of-00006.parquet`](https://huggingface.co/datasets/DCI-Agent/dci-bench/resolve/main/data/browsecomp-plus/test-00000-of-00006.parquet?download=true)
- [`browsecomp_plus/data.parquet`](https://huggingface.co/datasets/DCI-Agent/corpus/resolve/main/browsecomp_plus/data.parquet?download=true)

The canonical task is tracked in the case directory. The corpus is generated
locally and exposed at `data/corpus/`, which remains untracked.

Never commit `data/corpus/`.
