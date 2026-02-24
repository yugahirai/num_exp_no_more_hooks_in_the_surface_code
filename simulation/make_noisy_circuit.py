import os
import stim
import fire

from tqdm import tqdm
from multiprocessing import Pool
from _noise import NoiseModel
from z_normal_XXmeas.src.make_circuit import main as make_z_normal_XXmeas_circuit
from z_alternating_XXmeas.src.make_circuit import (
    main as make_z_alternating_XXmeas_circuit,
)
from z_ZX_interleaved_XXmeas.src.make_circuit import (
    main as make_z_ZX_interleaved_XXmeas_circuit,
)
from x_normal_XXmeas.src.make_circuit import main as make_x_normal_XXmeas_circuit
from x_alternating_XXmeas.src.make_circuit import (
    main as make_x_alternating_XXmeas_circuit,
)
from x_ZX_interleaved_XXmeas.src.make_circuit import (
    main as make_x_ZX_interleaved_XXmeas_circuit,
)
from z_normal_memory.src.make_circuit import main as make_z_normal_memory_circuit
from z_normal_hook_proned_memory.src.make_circuit import (
    main as make_z_normal_hook_proned_memory_circuit,
)
from z_alternating_memory.src.make_circuit import (
    main as make_z_alternating_memory_circuit,
)
from z_ZX_interleaved_Z2X_X2Z_memory.src.make_circuit import (
    main as make_z_ZX_interleaved_Z2X_X2Z_memory_circuit,
)
from z_ZX_interleaved_Z2Z_X2X_memory.src.make_circuit import (
    main as make_z_ZX_interleaved_Z2Z_X2X_memory_circuit,
)


CIRCUIT_MAKERS = {
    "z_normal_XXmeas": make_z_normal_XXmeas_circuit,
    "z_alternating_XXmeas": make_z_alternating_XXmeas_circuit,
    "z_ZX_interleaved_XXmeas": make_z_ZX_interleaved_XXmeas_circuit,
    "z_normal_memory": make_z_normal_memory_circuit,
    "z_normal_hook_proned_memory": make_z_normal_hook_proned_memory_circuit,
    "z_alternating_memory": make_z_alternating_memory_circuit,
    "z_ZX_interleaved_Z2X_X2Z_memory": make_z_ZX_interleaved_Z2X_X2Z_memory_circuit,
    "z_ZX_interleaved_Z2Z_X2X_memory": make_z_ZX_interleaved_Z2Z_X2X_memory_circuit,
    "x_normal_XXmeas": make_x_normal_XXmeas_circuit,
    "x_alternating_XXmeas": make_x_alternating_XXmeas_circuit,
    "x_ZX_interleaved_XXmeas": make_x_ZX_interleaved_XXmeas_circuit,
}

NOISE_MODELS = {
    "SI1000": lambda noise: NoiseModel.si1000(noise),
    "uniform_depolarizing": lambda noise: NoiseModel.uniform_depolarizing(noise),
}


def make_noisy_circuit(
    circuit: stim.Circuit, noise: float, noise_model: str
) -> stim.Circuit:
    model = NOISE_MODELS[noise_model](noise)
    return model.noisy_circuit(circuit)


def process_circuit(
    protocol: str,
    d: int,
    p: float,
    l: int,
    noise_model: str,
    circuit_dir: str,
    z_detector: bool,
    x_detector: bool,
):
    make_circuit = CIRCUIT_MAKERS[protocol]
    circuit = make_circuit(d, 0, l)
    # circuit = make_circuit(d, 0, l, z_detector, x_detector)

    base_circuit = circuit.without_noise()

    # Save noiseless circuit (only if not exists)
    base_path = os.path.join(circuit_dir, f"circuit_{protocol}_d{d}_without_noise.stim")
    if not os.path.exists(base_path):
        with open(base_path, "w") as fp:
            fp.write(str(base_circuit))

    # Generate noisy circuit
    noisy_circuit = make_noisy_circuit(base_circuit, p, noise_model)
    noisy_path = os.path.join(
        circuit_dir, f"circuit_{protocol}_d{d}_p{p}_{noise_model}.stim"
    )
    with open(noisy_path, "w") as fp:
        fp.write(str(noisy_circuit))


def _process_circuit_args(args):
    return process_circuit(*args)


def main(num_workers: int = 7):
    d_list = [3, 5]
    p_list = [1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2]
    l_mag_list = [0]
    z_detector = True
    x_detector = True
    # p_list = [5e-4, 6e-4, 7e-4, 8e-4, 9e-4, 1e-3, 2e-3, 5e-3, 1e-2]
    noise_model = "uniform_depolarizing"
    # noise_model = "SI1000"

    protocol_list = [
        "z_normal_XXmeas",
        "z_alternating_XXmeas",
        "z_ZX_interleaved_XXmeas",
        "z_normal_memory",
        "z_normal_hook_proned_memory",
        "z_alternating_memory",
        "z_ZX_interleaved_Z2X_X2Z_memory",
        "z_ZX_interleaved_Z2Z_X2X_memory",
        "x_normal_XXmeas",
        "x_alternating_XXmeas",
        "x_ZX_interleaved_XXmeas",
    ]
    circuit_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        f"simulation/circuit/{noise_model}",
    )
    os.makedirs(circuit_dir, exist_ok=True)

    # Prepare tasks
    tasks = []
    for protocol in protocol_list:
        for d in d_list:
            for p in p_list:
                for l_mag in l_mag_list:
                    l = (d + 1) * l_mag
                    tasks.append(
                        (
                            protocol,
                            d,
                            p,
                            l,
                            noise_model,
                            circuit_dir,
                            z_detector,
                            x_detector,
                        )
                    )

    # Use multiprocessing to process tasks in parallel with progress bar
    with Pool(num_workers) as pool:
        for _ in tqdm(
            pool.imap_unordered(_process_circuit_args, tasks), total=len(tasks)
        ):
            pass


if __name__ == "__main__":
    fire.Fire(main)
