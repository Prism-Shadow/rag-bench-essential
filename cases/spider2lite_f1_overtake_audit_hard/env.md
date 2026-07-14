# Environment

Runtime assumptions for this case (see `CASE_SPEC.md`, the env piece):

- bash, python3 (>= 3.10)
- sqlite3 (Python stdlib) for the in-process `data/f1.sqlite` file
- pandas (optional)
- Offline. No network, no services, no database server, no containers.

This case needs no provisioning: the F1 database is a static `.sqlite` file
queried in-process, so there is nothing to set up or tear down.
