# Repository Guidelines

## Project Structure & Module Organization

This guide covers `work_sim/`, the visual-field analysis workspace within `bisignal_training`.

- `load_data.ipynb` contains data exploration, visualizations, three-visit training windows, and patient-grouped train/test splitting.
- `uwhv/` is the upstream UWHVF dataset Git submodule. Its `CSV/` directory supplies measurements and coordinates; `README.md`, `datasheet.md`, and `schema.json` document the data.
- `imgs/` holds generated patient plots, such as `pat_647F.png`. Review generated files before staging them.
- There are no separate source modules, test directories, or build configuration in this workspace.

## Build, Test, and Development Commands

Run these commands from `work_sim/`. Use Python 3.12 or newer; the notebook uses Python 3.12-compatible f-string syntax.

```bash
git submodule update --init --recursive -- uwhv
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install jupyterlab pandas numpy matplotlib scikit-learn tqdm
jupyter lab load_data.ipynb
```

These initialize the dataset, create an isolated environment, install notebook dependencies, and launch the editor. Select that environment's Python kernel. No dependency lockfile or build command exists here; keep `.venv/` untracked.

For a lightweight notebook JSON check:

```bash
python -m json.tool load_data.ipynb > /dev/null
```

## Coding Style & Naming Conventions

Use four-space Python indentation and descriptive `snake_case` names. Existing cells use `df_`, `np_`, and `l_` prefixes for DataFrames, arrays, and lists. Preserve dataset column names such as `PatID`, `FieldN`, and `Sens_1`. Keep paths relative to `work_sim/` and explain analysis assumptions in Markdown cells. No formatter or linter is configured.

## Testing Guidelines

There is no automated test framework or coverage threshold. Restart the kernel and execute relevant completed cells in dependency order. Full execution currently encounters exploratory errors, including a reference before assignment and an unfinished `def calc`; report these separately from regressions.

Check coordinate alignment, blind-spot exclusion (`Cluster == 0`), chronological windows, matching input/target counts, and zero patient overlap between training and test sets. Keep split seeds reproducible (`random_state=42`). Inspect representative plots after visualization changes.

## Commit & Pull Request Guidelines

History uses short, informal action summaries, such as `add work simulation` and `day5 fix test`; no strict convention is evident. Use concise summaries identifying the changed analysis. PRs should describe the purpose, affected cells, validation performed, and known execution limitations. Link relevant issues and include representative images for plot changes. Avoid unrelated notebook-output churn. Preserve the dataset's BSD license and citation; make submodule updates explicit.
