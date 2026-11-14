# Repository Guidelines

## Project Structure & Module Organization

`work_sim_2/` is a research workspace within the parent `bisignal_training` Git repository.

- `report.odt`: local research report.
- `EyeMovementDetectorEvaluation/`: Git submodule containing MATLAB code and reference data.
- `EyeMovementDetectorEvaluation/matlab_annotator/`: `EventTag.m`, its paired GUI layout `EventTag.fig`, and coordinate conversion helpers.
- `EyeMovementDetectorEvaluation/matlab_analysis_code/`: detection, confusion-matrix, and Cohen's kappa analysis scripts.
- `EyeMovementDetectorEvaluation/annotated_data/`: original annotations, the publication subset, and `fix_by_Zemblys2018/` corrections.
- `EyeMovementDetectorEvaluation/Stimuli/`: image and video assets.

## Build, Test, and Development Commands

Run shell commands from `work_sim_2/`:

```sh
git submodule update --init --recursive -- EyeMovementDetectorEvaluation
git -C EyeMovementDetectorEvaluation status --short
```

These initialize the research dependency and inspect its changes. There is no configured build system or package installation step.

To launch the annotation GUI, run in MATLAB from `work_sim_2/`:

```matlab
cd('EyeMovementDetectorEvaluation/matlab_annotator');
EventTag
```

For static analysis, run `checkcode('EventTag.m')` from that directory. No formatter or lint configuration is checked in. `mainDetection.m` is an incomplete research script: configure input paths and supply missing helpers such as `getParams` and detector implementations before attempting analysis.

## Coding Style & Naming Conventions

Use four-space indentation for new MATLAB blocks and match surrounding code when editing. Match function names to `.m` filenames; follow existing descriptive names such as `pixels2degrees` and `callKappa3`. Document inputs, outputs, units, and event-label assumptions with `%` comments. Preserve GUIDE callback names and keep `EventTag.m` consistent with `EventTag.fig`.

## Testing Guidelines

No automated test suite or coverage threshold is configured. Validate changed helpers with small, known inputs and record expected versus observed results. For GUI changes, load a copy of an annotated `.mat` file and verify plotting, label edits, and saving. Record the MATLAB version and dataset used. If adding automated tests, use MATLAB unit tests named `test*.m` under `tests/` in the relevant repository, then run `runtests('tests')` there.

## Commit & Pull Request Guidelines

History uses short, descriptive subjects such as `add work simulation` and `Add missing function`; no uniform prefix convention exists. Use imperative summaries and focused commits. Commit submodule changes inside its repository, then update the parent repository's pointer. PRs should explain the change, link relevant issues, describe validation and dataset provenance, and include screenshots for GUI changes.

## Data Integrity

Preserve reference datasets; save experimental outputs separately. State whether results use the publication subset or corrected annotations. Retain upstream licensing and attribution, including the credit in `kappa.m`.
