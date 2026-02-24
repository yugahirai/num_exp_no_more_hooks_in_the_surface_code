# NUMERICAL EXPERIMENTS FOR NO MORE HOOKS IN THE SURFACE CODE


## Directories
```
.
└── num_exp_no_more_hooks_in_the_surface_code
    ├── README.md
    ├── pyproject.toml
    └── simulation
        ├── circuit
        ├── csv
        ├── figs
        ├── _noise.py
        ├── make_noisy_circuit.py
        ├── plot.py
        └── run_sinter.py
```


## Usage
All commands are executed in '/num_exp_no_more_hooks_in_the_surface_code'

Install the all Python libraries in 'pyproject.toml'. If you can use uv command, execute the following command;
```
uv sync
```

All Stim circuits used for the numerical results in the paper are in '\simulation'.
The results of the logical error rates are in '\csv'

The all commands are executed in '\num_exp_no_more_hooks_in_the_surface_code'.

Use the following command;
```
python simulation/run_sinter.py {num_workers}
```

Here, '{num_workers}' is the number of parallel workers used by Sinter for Monte Carlo sampling.

'plot.py' plot the results from 'run_sinter.py'. Please, chose the code type that you want to plot.
The name of code types means '{type of logical observable}\_{protocol}\_{operation}'

```

CODE_TYPES_TO_PLOT = [
    "z_normal_memory",
    "z_ZX_interleaved_Z2Z_X2X_memory",
    "z_ZX_interleaved_Z2X_X2Z_memory",
    "z_normal_hook_proned_memory",
    "z_alternating_memory",
    "z_normal_XXmeas",
    "z_ZX_interleaved_XXmeas",
    "z_alternating_XXmeas",
    "x_normal_XXmeas",
    "x_ZX_interleaved_XXmeas",
    "x_alternating_XXmeas",
]
```

The plots are in '\figs'
