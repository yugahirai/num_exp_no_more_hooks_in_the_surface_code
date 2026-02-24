import stim
from typing import Tuple, List

CANCEL = False


def allocate_qubits(circuit: stim.Circuit, index: int, coords: Tuple[int, int]):
    circuit.append("QUBIT_COORDS", [index], [coords[0], coords[1]])


def append_reset(circuit: stim.Circuit, qubits: List[int], phys_error: float):
    circuit.append("R", qubits)
    if not CANCEL:
        circuit.append("X_ERROR", qubits, phys_error)


def append_x_reset(circuit: stim.Circuit, qubits: List[int], phys_error: float):
    circuit.append("RX", qubits)
    if not CANCEL:
        circuit.append("Z_ERROR", qubits, phys_error)


def append_y_reset(circuit: stim.Circuit, qubits: List[int], phys_error: float):
    circuit.append("RY", qubits)
    if not CANCEL:
        circuit.append("Z_ERROR", qubits, phys_error)


def append_cnot(circuit: stim.Circuit, ancilla: int, target: int, phys_error: float):
    circuit.append("CNOT", [ancilla, target])
    if not CANCEL:
        circuit.append("DEPOLARIZE2", [ancilla, target], phys_error)


def append_hadamard(circuit: stim.Circuit, qubits: List[int], phys_error: float):
    circuit.append("H", qubits)
    if not CANCEL:
        circuit.append("DEPOLARIZE1", qubits, phys_error)


def append_measurement(circuit: stim.Circuit, qubits: List[int], phys_error: float):
    if not CANCEL:
        circuit.append("DEPOLARIZE1", qubits, phys_error)
        circuit.append("X_ERROR", qubits, phys_error)
    circuit.append("M", qubits)


def append_measurement_reset(
    circuit: stim.Circuit, qubits: List[int], phys_error: float
):
    if not CANCEL:
        circuit.append("DEPOLARIZE1", qubits, phys_error)
        circuit.append("X_ERROR", qubits, phys_error)
    circuit.append("M", qubits)
    circuit.append("R", qubits)
    if not CANCEL:
        circuit.append("X_ERROR", qubits, phys_error)


def append_y_measurement(circuit: stim.Circuit, qubits: List[int], phys_error: float):
    if not CANCEL:
        circuit.append("DEPOLARIZE1", qubits, phys_error)
        circuit.append("X_ERROR", qubits, phys_error)
    circuit.append("MY", qubits)


def append_x_measurement(circuit: stim.Circuit, qubits: List[int], phys_error: float):
    if not CANCEL:
        circuit.append("DEPOLARIZE1", qubits, phys_error)
        circuit.append("Z_ERROR", qubits, phys_error)
    circuit.append("MX", qubits)


def append_x_measurement_x_reset(
    circuit: stim.Circuit, qubits: List[int], phys_error: float
):
    if not CANCEL:
        circuit.append("DEPOLARIZE1", qubits, phys_error)
        circuit.append("Z_ERROR", qubits, phys_error)
    circuit.append("MX", qubits)
    circuit.append("RX", qubits)
    if not CANCEL:
        circuit.append("Z_ERROR", qubits, phys_error)


def append_cz(circuit: stim.Circuit, ancilla: int, target: int, phys_error: float):
    circuit.append("CZ", [ancilla, target])
    if not CANCEL:
        circuit.append("DEPOLARIZE2", [ancilla, target], phys_error)


def append_swap(circuit: stim.Circuit, qubit: int, target: int, phys_error: float):
    circuit.append("SWAP", [qubit, target])
    if not CANCEL:
        circuit.append("DEPOLARIZE2", [qubit, target], phys_error)


def append_tick(circuit: stim.Circuit):
    circuit.append("TICK")


def append_sqrt_x(circuit: stim.Circuit, qubit: int, phys_error: float):
    circuit.append("SQRT_X", [qubit])
    if not CANCEL:
        circuit.append("DEPOLARIZE1", [qubit], phys_error)


def append_s(circuit: stim.Circuit, qubit: int, phys_error: float):
    circuit.append("S", [qubit])
    if not CANCEL:
        circuit.append("DEPOLARIZE1", [qubit], phys_error)


def append_x(circuit: stim.Circuit, qubit: int, phys_error: float):
    circuit.append("X", [qubit])
    if not CANCEL:
        circuit.append("DEPOLARIZE1", [qubit], phys_error)


def append_cy(circuit: stim.Circuit, ancilla: int, target: int, phys_error: float):
    circuit.append("CY", [ancilla, target])
    if not CANCEL:
        circuit.append("DEPOLARIZE2", [ancilla, target], phys_error)


def append_s_dag(circuit: stim.Circuit, qubit: int, phys_error: float):
    circuit.append("S_dag", [qubit])
    if not CANCEL:
        circuit.append("DEPOLARIZE1", [qubit], phys_error)


def append_ycx(circuit: stim.Circuit, ancilla: int, target: int, phys_error: float):
    circuit.append("YCX", [ancilla, target])
    if not CANCEL:
        circuit.append("DEPOLARIZE2", [ancilla, target], phys_error)


def append_xcx(circuit: stim.Circuit, ancilla: int, target: int, phys_error: float):
    circuit.append("XCX", [ancilla, target])
    if not CANCEL:
        circuit.append("DEPOLARIZE2", [ancilla, target], phys_error)


def append_sqrt_x_dag(circuit: stim.Circuit, qubit: int, phys_error: float):
    circuit.append("SQRT_X_dag", [qubit])
    if not CANCEL:
        circuit.append("DEPOLARIZE1", [qubit], phys_error)
