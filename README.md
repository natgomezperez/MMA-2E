# SwarmPAL MMA

## Development setup (uv)

Create or update the environment:

```bash
uv sync
```

By default, `swarmpal` is sourced from the [staging branch on GitHub](https://github.com/Swarm-DISC/SwarmPAL/tree/staging). To update that Git dependency:

```bash
uv sync --upgrade-package swarmpal
```

To work against a local SwarmPAL checkout, switch the source configured in `[tool.uv.sources]` in `pyproject.toml` and re-run `uv sync`  (alternatively use `uv add --editable ../SwarmPAL`). Revert the change before committing if you do not want to lock the repo to a local path.

## Updating the environment

When `pyproject.toml` or `uv.lock` changes, update the environment with:

```bash
uv sync
```

For CI or reproducible installs, prefer:

```bash
uv sync --frozen
```

To upgrade a specific dependency and update the lockfile:

```bash
uv lock --upgrade-package viresclient
uv sync
```

## Testing

Run the test suite (executes `MMA_SHA_2E.ipynb` via pytest + nbmake):

```bash
uv run pytest
```

The notebook is configured to run automatically as a test in `[tool.pytest.ini_options]`.
