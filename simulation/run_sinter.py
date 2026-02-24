import re
import os
import fire
import stim
import sinter
from glob import glob
from tqdm import tqdm


def main(num_worker: int):

    stim_path_dir = os.path.join(os.path.dirname(__file__), "circuit")
    stim_path_list_uniform = glob(
        os.path.join(stim_path_dir, "uniform_depolarizing/*.stim")
    )

    sinter_tasks = []

    for stim_path in tqdm(stim_path_list_uniform):
        circuit = stim.Circuit.from_file(stim_path)
        pattern = r"circuit_([^_]+)_(.+?)_d(\d+)_p([\d\.]+)_([^\.]+)"
        match = re.search(pattern, stim_path)
        if match:
            base, name, d, p, noise_model = match.groups()

            if int(d) >= 11:
                continue

            task = sinter.Task(
                circuit=circuit,
                detector_error_model=circuit.detector_error_model(
                    decompose_errors=True
                ),
                json_metadata={
                    "base": base,
                    "name": name,
                    "d": d,
                    "p": p,
                    "noise_model": noise_model,
                },
            )
            sinter_tasks.append(task)

    _ = sinter.collect(
        tasks=sinter_tasks,
        num_workers=num_worker,
        print_progress=True,
        decoders=["pymatching"],
        max_shots=1_000_000_000,
        max_errors=300,
        save_resume_filepath=os.path.join(
            os.path.dirname(__file__), "csv", "no_more_hooks.csv"
        ),
    )


if __name__ == "__main__":
    fire.Fire(main)
