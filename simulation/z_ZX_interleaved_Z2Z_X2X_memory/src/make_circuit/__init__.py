import stim
from .allocation import Allocation
from . import _operators as op
from . import record as rec
from ..utils import export
from .Z_intialization import Z_intialization
from .Z_measurement import Z_measurement
import os


def reset_new_qubits(
    circuit: stim.Circuit,
    qubit_list_old: list[int],
    qubit_list_new: list[int],
    p: float,
):
    for qubit in qubit_list_new:
        if qubit not in qubit_list_old:
            op.append_reset(circuit, [qubit], p)


def main(d: int, p: float, l: int, z_detector: bool = True, x_detector: bool = True):
    circuit = stim.Circuit()
    record = rec.Record()

    # allocation
    alloc = Allocation(circuit, d, p, l)
    alloc.allocate_data_qubits()
    alloc.allocate_ancilla_qubits()
    alloc.append_coords()
    alloc.append_reset_all_qubits()

    # Z_intialization
    z_intialization = Z_intialization(
        circuit, alloc.loc, d, p, 0, record, "Z", l, z_detector, x_detector
    )
    z_intialization.initialize()

    MAX_ROUND_Z_INIT = d - 1
    for round_z_init in range(MAX_ROUND_Z_INIT):
        z_intialization.append_syndrome(round_z_init, MAX_ROUND_Z_INIT)
        if round_z_init == 0:
            z_intialization.append_head_detector()
        else:
            z_intialization.append_body_detector(round_z_init)

    # Z measurement
    z_measurement = Z_measurement(circuit, alloc.loc, d, p, 0, record, l, z_detector)
    z_measurement.initialize()
    z_measurement.append_syndrome()
    z_measurement.append_head_detector()

    for qubit_index in z_measurement.data_list:
        pos = z_measurement.loc.get_location(qubit_index)
        x = pos[0]
        y = pos[1]
        if x == z_measurement.Q1_MAX_X:
            target_rec = record.get_record((x, y, record.get_t() - 1))
            if target_rec is not None:
                circuit.append(
                    "OBSERVABLE_INCLUDE",
                    [stim.target_rec(target_rec - len(record.get_all_records()))],
                    0,
                )

    return circuit
