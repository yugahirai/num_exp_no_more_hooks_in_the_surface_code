import stim
from src import make_circuit
from src.utils import export
import os


if __name__ == "__main__":
    circuit = stim.Circuit()
    d = 3
    p = 0
    l = 0

    circuit = make_circuit.main(d, p, l)

    export.export_diagram(circuit, "X")
    export.export_diagram_full(circuit, "X")
