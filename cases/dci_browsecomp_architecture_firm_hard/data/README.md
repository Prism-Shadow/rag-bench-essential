# Data

This case uses BrowseComp-Plus data distributed by `DCI-Agent/dci-bench` and
`DCI-Agent/corpus`.

- Benchmark: BrowseComp-Plus
- Source dataset: `DCI-Agent/dci-bench`
- Corpus dataset: `DCI-Agent/corpus`
- Corpus shape: approximately 100,195 documents

The plaintext query, ground truth, and corpus are intentionally not stored in
this Git repository. Authorized users must obtain the official encrypted
benchmark shard and corpus through the upstream distribution, decrypt them
locally, and expose the exported read-only corpus at `data/corpus/` only inside
an untracked materialization or staged workspace.

Never commit `data/corpus/`, the decrypted task, or the decrypted truth.
