"""
Plot logical error rates comparing surface code variants.

Reads sinter-format CSV from compressed_csv/ and produces comparison plots
of logical error rate vs physical error rate, separated by noise model.
"""

import csv
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
import sinter
from pathlib import Path
from collections import defaultdict


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Select code types to plot (format: "{base}_{name}", e.g. "z_normal_memory").
# Set to None to plot all code types found in the data.
CODE_TYPES_TO_PLOT = [
    # "z_normal_memory",
    # "z_ZX_interleaved_Z2Z_X2X_memory",
    # "z_ZX_interleaved_Z2X_X2Z_memory",
    # "z_normal_hook_proned_memory",
    # "z_alternating_memory",
    # "z_normal_XXmeas",
    # "z_ZX_interleaved_XXmeas",
    # "z_alternating_XXmeas",
    # "x_normal_XXmeas",
    # "x_ZX_interleaved_XXmeas",
    # "x_alternating_XXmeas",
]
# CODE_TYPES_TO_PLOT = None

# Select noise models to plot. Each gets its own figure.
# Set to None to plot all noise models found in the data.
NOISE_MODELS_TO_PLOT = ["uniform_depolarizing"]
# NOISE_MODELS_TO_PLOT = ["SI1000"]

# Select physical error rate range. Set to None for full range.
# P_RANGE = None
P_RANGE = (8e-5, 1.1e-2)

# Select distances to plot. Set to None for all distances.
# Each distance gets its own color.
DISTANCES_TO_PLOT = [3, 5]

FONT_SIZE_TICK = 18
FONT_SIZE_LEGEND = 10
FONT_SIZE_LABEL = 18
FONT_SIZE_TITLE = 0

# Fixed axis limits (set to None to auto-scale)
X_RANGE = (1e-4, 1e-2)
Y_RANGE = (1e-11, 1e0)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_sinter_csv(csv_path: Path) -> list[dict]:
    """Load a sinter-format CSV and parse json_metadata into flat records.

    Rows sharing the same ``(code_type, d, p, noise_model)`` are aggregated
    (shots and errors summed) before computing the logical error rate.
    A composite ``code_type`` field is created from ``base`` + ``name``
    (e.g. ``"z_normal_memory"``), so Z- and X-basis experiments can be
    distinguished in the configuration and legend.
    """
    aggregated: dict[tuple, dict] = {}
    with open(csv_path) as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            meta = json.loads(row["json_metadata"])
            code_type = f"{meta['base']}_{meta['name']}"
            d = int(meta["d"])
            p = float(meta["p"])
            noise_model = meta["noise_model"]
            key = (code_type, d, p, noise_model)

            if key not in aggregated:
                aggregated[key] = {
                    "code_type": code_type,
                    "name": meta["name"],
                    "base": meta["base"],
                    "d": d,
                    "l": int(meta["l"]) if "l" in meta else d,
                    "p": p,
                    "noise_model": noise_model,
                    "shots": 0,
                    "errors": 0,
                }
            aggregated[key]["shots"] += int(row["shots"])
            aggregated[key]["errors"] += int(row["errors"])

    records = []
    for rec in aggregated.values():
        rec["logical_error_rate"] = (
            rec["errors"] / rec["shots"] if rec["shots"] > 0 else 0.0
        )
        records.append(rec)
    return records


def load_all_csvs(csv_dir: Path) -> list[dict]:
    """Load and combine all CSV files in a directory."""
    csv_files = sorted(csv_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {csv_dir}")

    all_records = []
    for csv_path in csv_files:
        records = load_sinter_csv(csv_path)
        print(f"Loaded: {csv_path.name} ({len(records)} rows)")
        all_records.extend(records)

    print(f"Total: {len(all_records)} data points")
    return all_records


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def plot_comparison(
    records: list[dict],
    output_dir: Path,
    p_range=None,
    code_types_to_plot=None,
    noise_models_to_plot=None,
    distances_to_plot=None,
):
    """Plot logical error rate vs physical error rate, one figure per noise model."""

    # Filter by p range
    if p_range is not None:
        p_min, p_max = p_range
        records = [r for r in records if p_min <= r["p"] <= p_max]

    # Discover unique values
    all_code_types = sorted(set(r["code_type"] for r in records))
    all_noise_models = sorted(set(r["noise_model"] for r in records))
    all_distances = sorted(set(r["d"] for r in records))

    target_code_types = (
        [ct for ct in code_types_to_plot if ct in all_code_types]
        if code_types_to_plot is not None
        else all_code_types
    )
    target_noise_models = (
        [nm for nm in noise_models_to_plot if nm in all_noise_models]
        if noise_models_to_plot is not None
        else all_noise_models
    )
    target_distances = (
        [d for d in distances_to_plot if d in all_distances]
        if distances_to_plot is not None
        else all_distances
    )

    # Style maps — keyed by code_type ("{base}_{name}")
    code_type_labels = {
        "z_normal_XXmeas": "Z Normal XXmeas",
        "z_normal_memory": "N/Z hook-avoiding",
        "z_normal_hook_proned_memory": "N/Z hook-prone",
        "z_ZX_interleaved_XXmeas": "Z ZX Interleaved XXmeas",
        "z_ZX_interleaved_Z2Z_X2X_memory": "ZX Interleaved Z→Z X→X",
        "z_ZX_interleaved_Z2X_X2Z_memory": "ZX Interleaved Z→X X→Z",
        "z_alternating_XXmeas": "Z Alternating XXmeas",
        "z_alternating_memory": "Alternating",
        "x_normal_XXmeas": "X Normal XXmeas",
        "x_normal_memory": "X N/Z hook-avoiding",
        "x_normal_hook_proned_memory": "X N/Z hook-prone",
        "x_ZX_interleaved_XXmeas": "X ZX Interleaved XXmeas",
        "x_ZX_interleaved_Z2Z_X2X_memory": "X ZX Interleaved Z→Z X→X",
        "x_ZX_interleaved_Z2X_X2Z_memory": "X ZX Interleaved Z→X X→Z",
        "x_alternating_XXmeas": "X Alternating XXmeas",
        "x_alternating_memory": "X Alternating (memory)",
    }

    code_type_markers = {
        "z_normal_XXmeas": "o",
        "z_normal_memory": "o",
        "z_normal_hook_proned_memory": "s",
        "z_ZX_interleaved_XXmeas": "s",
        "z_ZX_interleaved_Z2Z_X2X_memory": "v",
        "z_ZX_interleaved_Z2X_X2Z_memory": "^",
        "z_alternating_XXmeas": "D",
        "z_alternating_memory": "D",
        "x_normal_XXmeas": "o",
        "x_normal_memory": "o",
        "x_normal_hook_proned_memory": "v",
        "x_ZX_interleaved_XXmeas": "s",
        "x_ZX_interleaved_Z2Z_X2X_memory": "s",
        "x_ZX_interleaved_Z2X_X2Z_memory": "^",
        "x_alternating_XXmeas": "D",
        "x_alternating_memory": "D",
    }

    code_type_linestyles = {
        "z_normal_XXmeas": "-.",
        "z_normal_memory": "-.",
        "z_normal_hook_proned_memory": "-.",
        "z_ZX_interleaved_XXmeas": "-",
        "z_ZX_interleaved_Z2Z_X2X_memory": "-",
        "z_ZX_interleaved_Z2X_X2Z_memory": "-",
        "z_alternating_XXmeas": "--",
        "z_alternating_memory": "--",
        "x_normal_XXmeas": "-.",
        "x_normal_memory": "-.",
        "x_normal_hook_proned_memory": "-.",
        "x_ZX_interleaved_XXmeas": "-",
        "x_ZX_interleaved_Z2Z_X2X_memory": "-",
        "x_ZX_interleaved_Z2X_X2Z_memory": "-",
        "x_alternating_XXmeas": "--",
        "x_alternating_memory": "--",
    }

    # Fixed color per distance
    d_color_map = {
        3: "tab:blue",
        5: "tab:orange",
        7: "tab:green",
        9: "tab:red",
        11: "tab:purple",
        13: "tab:brown",
    }

    # Group records for fast lookup: (noise_model, code_type, d) -> sorted list
    grouped = defaultdict(list)
    for r in records:
        key = (r["noise_model"], r["code_type"], r["d"])
        grouped[key].append(r)
    for key in grouped:
        grouped[key].sort(key=lambda r: r["p"])

    from matplotlib.ticker import LogLocator

    # One figure per noise_model (all distances on the same plot)
    for noise_model in target_noise_models:
        n_curves = sum(
            1
            for ct in target_code_types
            for d in target_distances
            if (noise_model, ct, d) in grouped
        )
        n_curves += 1  # for the p_L = p reference line
        legend_ncol = max(1, (n_curves + 11) // 12)
        legend_width = legend_ncol * 3.5
        fig_w = max(8, legend_width + 4)
        fig_h = max(6, 1.5 + 0.35 * ((n_curves + legend_ncol - 1) // legend_ncol) + 4)
        fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)
        has_data = False

        for code_type in target_code_types:
            for d in target_distances:
                data = grouped.get((noise_model, code_type, d), [])
                if not data:
                    continue
                has_data = True

                p_values = np.array([r["p"] for r in data])
                logical_rates = np.array([r["logical_error_rate"] for r in data])

                ci_low = []
                ci_high = []
                for r in data:
                    fit = sinter.fit_binomial(
                        num_shots=r["shots"],
                        num_hits=r["errors"],
                        max_likelihood_factor=1e3,
                    )
                    ci_low.append(fit.low)
                    ci_high.append(fit.high)
                ci_low = np.array(ci_low)
                ci_high = np.array(ci_high)

                color = d_color_map.get(d, "tab:gray")
                marker = code_type_markers.get(code_type, "o")
                linestyle = code_type_linestyles.get(code_type, "-")
                label_name = code_type_labels.get(code_type, code_type)

                ax.plot(
                    p_values,
                    logical_rates,
                    marker=marker,
                    linestyle=linestyle,
                    color=color,
                    label=f"{label_name} (d={d})",
                    markersize=6,
                    linewidth=1.5,
                    markeredgecolor=np.array(plt.cm.colors.to_rgba(color)[:3]) * 0.5,
                    markeredgewidth=0.8,
                )
                ax.fill_between(
                    p_values,
                    ci_low,
                    ci_high,
                    color=color,
                    alpha=0.15,
                )

        if not has_data:
            plt.close(fig)
            continue

        ax.set_xscale("log")
        ax.set_yscale("log")

        ax.set_xlim(X_RANGE)
        ax.set_ylim(Y_RANGE)

        if p_range is not None:
            ax.set_xlim(p_range)

        ax.xaxis.set_major_locator(LogLocator(base=10, numticks=20))
        ax.yaxis.set_major_locator(LogLocator(base=10, numticks=20))
        ax.xaxis.set_minor_locator(
            LogLocator(base=10, subs=np.arange(2, 10), numticks=100)
        )
        ax.yaxis.set_minor_locator(
            LogLocator(base=10, subs=np.arange(2, 10), numticks=100)
        )

        all_p = [r["p"] for r in records if r["noise_model"] == noise_model]
        if all_p:
            p_line = np.array([min(all_p), max(all_p)])
            ax.plot(p_line, p_line, "k--", alpha=0.3, label=r"$p_L = p$")

        ax.set_xlabel("Physical Error Rate $p$", fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel("Logical Error Rate $p_L$", fontsize=FONT_SIZE_LABEL)
        ax.tick_params(axis="both", labelsize=FONT_SIZE_TICK)
        ax.legend(loc="lower right", fontsize=FONT_SIZE_LEGEND, ncol=legend_ncol)
        ax.grid(True, alpha=0.3, which="both")

        stem = f"comparison_memory_{noise_model}"
        png_path = output_dir / f"{stem}.png"
        pdf_path = output_dir / f"{stem}.pdf"
        plt.savefig(png_path, dpi=150)
        plt.savefig(pdf_path)
        print(f"Saved: {png_path}")
        print(f"Saved: {pdf_path}")
        # plt.show()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Plot logical error rates from sinter CSV results."
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Path to a single CSV file (default: load all from compressed_csv/)",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    csv_dir = script_dir / "csv"
    figs_dir = script_dir / "figs"
    figs_dir.mkdir(exist_ok=True)

    if args.csv:
        records = load_sinter_csv(Path(args.csv))
        print(f"Loaded: {args.csv} ({len(records)} rows)")
    else:
        records = load_all_csvs(csv_dir)

    # Print summary
    code_types = sorted(set(r["code_type"] for r in records))
    distances = sorted(set(r["d"] for r in records))
    noise_models = sorted(set(r["noise_model"] for r in records))
    p_values = sorted(set(r["p"] for r in records))
    print(f"\nData summary:")
    print(f"  Code types:   {code_types}")
    print(f"  Distances:    {distances}")
    print(f"  Noise models: {noise_models}")
    print(f"  p values:     {p_values}")
    print()

    plot_comparison(
        records,
        figs_dir,
        p_range=P_RANGE,
        code_types_to_plot=CODE_TYPES_TO_PLOT,
        noise_models_to_plot=NOISE_MODELS_TO_PLOT,
        distances_to_plot=DISTANCES_TO_PLOT,
    )


if __name__ == "__main__":
    main()
