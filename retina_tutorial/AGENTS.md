# Repository Guidelines

## Project Structure & Module Organization

This ChatGPT-created Python/Jupyter tutorial predicts the next visual-field measurement from three previous examinations. The repository records an analysis carried out while reading as little code as possible.

- `retina_tutorial.ipynb` is the main Japanese-language tutorial; `run_analysis.py` contains its executable analysis.
- `retina_exploration.ipynb` contains exploratory work; `figs/` holds examination plots.
- `data/` contains bundled CSVs, original R data, coordinates, licenses, provenance, and `prepare_visualfields.py` for source reproduction.
- `outputs/` contains generated metrics, figures, patient splits, environment details, and research notes.
- `README.txt` provides execution instructions; the HTML guide and glossary support browser-based reading.

## Build, Test, and Development Commands

Run commands from this directory; analysis outputs use relative paths. No build step is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter notebook retina_tutorial.ipynb
```

These commands create an isolated environment, install dependencies, and launch the tutorial. Run `python run_analysis.py` for the complete script workflow, or `MPLBACKEND=Agg python run_analysis.py` for headless validation. Both regenerate files in `outputs/` and create `retina_results.zip`; review resulting changes before committing. Normal tutorial execution needs neither R nor a GPU nor data downloads.

## Coding Style & Naming Conventions

Use four-space Python indentation, `snake_case` functions and variables, and uppercase constants such as `SEED`, `HISTORY`, and `ALPHA`. Match surrounding code and preserve Japanese teaching explanations. Keep corresponding notebook cells and script sections synchronized, and refresh affected HTML examples when behavior changes. Preserve numbered figure names such as `01_three_fields.png`. No formatter or linter is configured.

## Testing Guidelines

There is no dedicated test suite or coverage threshold. Run the analysis script and restart the notebook kernel before running all cells. Existing assertions check data integrity, patient separation, array shapes, and finite predictions; extend these checks when changing behavior. Inspect `outputs/qc.json`, `metrics.csv`, and generated figures. Treat `outputs/validation.json` as a historical record, not proof of a new run.

## Commit & Pull Request Guidelines

History uses short, informal English/Japanese summaries, sometimes with prefixes such as `sim2:`; no strict convention is established. Use concise, descriptive imperative subjects. PRs should explain the change, list validation commands, identify affected notebook/script sections, and summarize metric changes. Include plot previews for visualization changes and link relevant issues when available.

## Data & Reproducibility

Preserve source hashes, licenses, and provenance. Retain the fixed seed, disjoint 21/9 patient split, and exclusion of `l26`/`l35` unless explicitly documenting a design change. Fit preprocessing only on training patients and exclude future measurements from features.
