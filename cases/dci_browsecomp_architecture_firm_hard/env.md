# Environment

Runtime assumptions for this case:

- bash
- python3 >= 3.10
- `rg` / ripgrep strongly recommended
- Offline during solving: no web search, no hosted retrieval service, no vector
  index, and no external database server

The corpus is a local read-only directory exposed at `data/corpus/`. It may be a
symlink to a shared corpus outside the workspace.
