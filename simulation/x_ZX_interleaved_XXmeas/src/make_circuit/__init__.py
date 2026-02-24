import stim
from .allocation import Allocation
from . import _operators as op
from . import record as rec
from ..utils import export
from .Z_intialization import Z_intialization
from .XX_measurement import XX_measurement
from .shrink import shrink
from .X_measurement import X_measurement
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


def main(d: int, p: float, l: int):
    circuit = stim.Circuit()
    record = rec.Record()

    # allocation
    alloc = Allocation(circuit, d, p, l)
    alloc.allocate_data_qubits()
    alloc.allocate_ancilla_qubits()
    alloc.append_coords()
    alloc.append_reset_all_qubits()

    op.append_tick(circuit)
    # Z_intialization
    z_intialization = Z_intialization(circuit, alloc.loc, d, p, 0, record, "Z", l)
    z_intialization.initialize()

    MAX_ROUND_Z_INIT = d - 1
    for round_z_init in range(MAX_ROUND_Z_INIT):
        z_intialization.append_syndrome(round_z_init)
        if round_z_init == 0:
            z_intialization.append_head_detector()
        else:
            z_intialization.append_body_detector(round_z_init)

    # XX_measurement
    xx_measurement = XX_measurement(circuit, alloc.loc, d, p, 0, record, l)
    xx_measurement.initialize()
    reset_new_qubits(
        circuit,
        z_intialization.data_list
        + z_intialization.x_ancilla_list
        + z_intialization.z_ancilla_list,
        xx_measurement.data_list
        + xx_measurement.x_ancilla_list
        + xx_measurement.z_ancilla_list,
        p,
    )
    op.append_tick(circuit)

    MAX_ROUND_XX_MEASUREMENT = d + 1
    for round_xx_measurement in range(MAX_ROUND_XX_MEASUREMENT):
        xx_measurement.append_syndrome(round_xx_measurement)
        if round_xx_measurement == 0:
            xx_measurement.append_head_detector()
        else:
            xx_measurement.append_body_detector(round_xx_measurement)

    for qubit_index in xx_measurement.x_ancilla_list:
        pos = xx_measurement.loc.get_location(qubit_index)
        x = pos[0]
        y = pos[1]
        if y < xx_measurement.Q1_MIN_Y:
            target_rec = record.get_record((x, y, record.get_t() - 1))
            if target_rec is not None:
                circuit.append(
                    "OBSERVABLE_INCLUDE",
                    [stim.target_rec(target_rec - len(record.get_all_records()))],
                    0,
                )

    for qubit_index in xx_measurement.z_ancilla_list:
        pos = xx_measurement.loc.get_location(qubit_index)
        x = pos[0]
        y = pos[1]
        if y == -1:
            target_rec = record.get_record((x, y, record.get_t() - 1))
            if target_rec is not None:
                circuit.append(
                    "OBSERVABLE_INCLUDE",
                    [stim.target_rec(target_rec - len(record.get_all_records()))],
                    0,
                )
        elif x == xx_measurement.Q2_MAX_X + 1 and y < xx_measurement.Q2_MIN_Y:
            target_rec = record.get_record((x, y, record.get_t() - 1))
            if target_rec is not None:
                circuit.append(
                    "OBSERVABLE_INCLUDE",
                    [stim.target_rec(target_rec - len(record.get_all_records()))],
                    0,
                )

    # shrink
    shrk = shrink(circuit, alloc.loc, d, p, 0, record, l)
    shrk.initialize()
    shrk.shrink()

    MAX_ROUND_SHRINK = d - 1
    for round_shrink in range(MAX_ROUND_SHRINK):
        shrk.append_syndrome(round_shrink)
        if round_shrink == 0:
            shrk.append_head_detector()
        else:
            shrk.append_body_detector(round_shrink)

    # X_measurement
    x_measurement = X_measurement(circuit, alloc.loc, d, p, 0, record, l)
    x_measurement.initialize()
    x_measurement.append_syndrome()
    x_measurement.append_head_detector()

    for qubit_index in x_measurement.data_list:
        pos = x_measurement.loc.get_location(qubit_index)
        x = pos[0]
        y = pos[1]
        if y == x_measurement.Q1_MIN_Y:
            target_rec = record.get_record((x, y, record.get_t() - 1))
            if target_rec is not None:
                circuit.append(
                    "OBSERVABLE_INCLUDE",
                    [stim.target_rec(target_rec - len(record.get_all_records()))],
                    0,
                )

    return circuit
