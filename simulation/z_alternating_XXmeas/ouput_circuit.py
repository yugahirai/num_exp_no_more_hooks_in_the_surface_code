import stim
from src import make_circuit
from src.utils import export
import os


if __name__ == "__main__":
    circuit = stim.Circuit()
    d = 5
    p = 0
    l = 0

    circuit = make_circuit.main(d, p, l, z_detector=False, x_detector=True)
    export.export_diagram(circuit, "Z")
    export.export_diagram_full(circuit, "Z")
