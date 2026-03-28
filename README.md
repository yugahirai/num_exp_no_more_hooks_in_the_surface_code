# Numerical Experiments for "No More Hooks in the Surface Code"

This repository contains the numerical simulation code and data for reproducing the results in the paper *"No More Hooks in the Surface Code."*
It compares the logical error rates of several surface code scheduling protocols -- including hook-avoiding, hook-prone, ZX-interleaved, and alternating schedules -- under depolarizing noise via Monte Carlo sampling.

## Overview

The simulation pipeline works as follows:

1. **Pre-generated Stim circuits** encode surface code experiments (memory and XX-measurement protocols) at various code distances and physical error rates.
2. **Sinter** performs Monte Carlo sampling of these circuits, using **PyMatching** as the decoder.
3. Results are saved to CSV and plotted as logical error rate vs. physical error rate curves.

## Directory Structure

```
.
├── pyproject.toml
├── README.md
└── simulation/
    ├── run_sinter.py          # Monte Carlo sampling driver
    ├── plot.py                # Plotting script
    ├── circuit/
    │   └── uniform_depolarizing/   # Pre-generated Stim circuits (.stim)
    ├── csv/
    │   └── no_more_hooks.csv       # Sampling results
    └── figs/                       # Output figures
```

## Requirements

- Python >= 3.12
- Dependencies (see `pyproject.toml`):
  - [Stim](https://github.com/quantumlib/Stim) -- quantum error correction circuit simulator
  - [Sinter](https://github.com/quantumlib/Stim/tree/main/glue/sample) -- Monte Carlo sampling framework for Stim
  - [PyMatching](https://github.com/oscarhiggott/PyMatching) -- MWPM decoder
  - [Fire](https://github.com/google/python-fire) -- CLI interface
  - matplotlib, numpy, tqdm

## Installation

Using [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Or with pip:

```bash
pip install .
```

## Usage

All commands should be run from the repository root.

### Running Simulations

```bash
python simulation/run_sinter.py {num_workers}
```

where `{num_workers}` is the number of parallel workers for Monte Carlo sampling. Results are saved (with resume support) to `simulation/csv/no_more_hooks.csv`. The sampling runs until 300 logical errors are collected or 10^9 shots are reached per data point.

### Plotting Results

```bash
python simulation/plot.py
```

To plot from a specific CSV file:

```bash
python simulation/plot.py --csv path/to/file.csv
```

Output figures are saved to `simulation/figs/` in both PNG and PDF formats.

### Configuration

The plotting script (`simulation/plot.py`) has configurable parameters at the top of the file:

- **`CODE_TYPES_TO_PLOT`** -- which scheduling protocols to include
- **`NOISE_MODELS_TO_PLOT`** -- noise model selection (`uniform_depolarizing`, `SI1000`)
- **`DISTANCES_TO_PLOT`** -- code distances to plot (default: 3, 5, 7, 9, 11, 13)
- **`P_RANGE`** -- physical error rate range

## Code Types

Each code type is named as `{logical_observable}_{protocol}_{operation}`:

| Code Type | Description |
|---|---|
| `z_normal_memory` | Z-basis, hook-avoiding N/Z schedule, memory experiment |
| `z_normal_hook_proned_memory` | Z-basis, hook-prone N/Z schedule, memory experiment |
| `z_ZX_interleaved_Z2Z_X2X_memory` | Z-basis, ZX-interleaved (Z->Z, X->X), memory experiment |
| `z_ZX_interleaved_Z2X_X2Z_memory` | Z-basis, ZX-interleaved (Z->X, X->Z), memory experiment |
| `z_alternating_memory` | Z-basis, alternating schedule, memory experiment |
| `z_normal_XXmeas` | Z-basis, N/Z schedule, XX measurement |
| `z_ZX_interleaved_XXmeas` | Z-basis, ZX-interleaved, XX measurement |
| `z_alternating_XXmeas` | Z-basis, alternating schedule, XX measurement |
| `x_normal_XXmeas` | X-basis, N/Z schedule, XX measurement |
| `x_ZX_interleaved_XXmeas` | X-basis, ZX-interleaved, XX measurement |
| `x_alternating_XXmeas` | X-basis, alternating schedule, XX measurement |

## Data Format

The CSV file follows Sinter's output format:

| Column | Description |
|---|---|
| `shots` | Number of Monte Carlo samples |
| `errors` | Number of logical errors observed |
| `discards` | Number of discarded shots |
| `seconds` | Wall-clock time |
| `decoder` | Decoder used (`pymatching`) |
| `strong_id` | Unique circuit identifier |
| `json_metadata` | JSON with `base`, `name`, `d`, `p`, `noise_model` |

## License

See the paper for terms of use.
