import stim
from .allocation import Allocation
from . import _operators as op
from . import record as rec
from ..utils import export
from .Z_intialization import Z_intialization
from .XX_measurement import XX_measurement
from .shrink import shrink
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
        z_intialization.append_syndrome(round_z_init)
        if round_z_init == 0:
            z_intialization.append_head_detector()
        else:
            z_intialization.append_body_detector(round_z_init)

    # XX_measurement
    xx_measurement = XX_measurement(
        circuit, alloc.loc, d, p, 0, record, l, x_detector, z_detector
    )
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
        xx_measurement.append_syndrome(round_xx_measurement, MAX_ROUND_XX_MEASUREMENT)
        if round_xx_measurement == 0:
            xx_measurement.append_head_detector()
            for qubit_index in xx_measurement.x_ancilla_list:
                pos = xx_measurement.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                if (
                    y == 1
                    and x >= xx_measurement.Q1_MAX_X
                    and x <= xx_measurement.Q2_MIN_X
                ):
                    target_rec = record.get_record((x, y, record.get_t() - 1))
                    if target_rec is not None:
                        circuit.append(
                            "OBSERVABLE_INCLUDE",
                            [
                                stim.target_rec(
                                    target_rec - len(record.get_all_records())
                                )
                            ],
                            0,
                        )
        else:
            xx_measurement.append_body_detector(round_xx_measurement)
            if round_xx_measurement == 1:
                for qubit_index in xx_measurement.z_ancilla_list:
                    pos = xx_measurement.loc.get_location(qubit_index)
                    x = pos[0]
                    y = pos[1]
                    if (
                        y == 1
                        and x >= xx_measurement.Q1_MAX_X
                        and x <= xx_measurement.Q2_MIN_X
                    ):
                        target_rec = record.get_record((x, y, record.get_t() - 1))
                        if target_rec is not None:
                            circuit.append(
                                "OBSERVABLE_INCLUDE",
                                [
                                    stim.target_rec(
                                        target_rec - len(record.get_all_records())
                                    )
                                ],
                                0,
                            )

    # shrink
    shrk = shrink(circuit, alloc.loc, d, p, 0, record, l, x_detector, z_detector)
    shrk.initialize()
    # shrk.shrink()

    MAX_ROUND_SHRINK = d - 1
    for round_shrink in range(MAX_ROUND_SHRINK):
        shrk.append_syndrome(round_shrink, MAX_ROUND_SHRINK)
        if round_shrink == 0:
            shrk.append_head_detector()
            for qubit_index in shrk.data_list:
                pos = shrk.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                if (
                    x > shrk.Q1_MAX_X - 2 and x < shrk.Q2_MIN_X
                ) and y == shrk.Q1_MIN_Y - 2:
                    target_rec = record.get_record((x, y, record.get_t() - 1))
                    if target_rec is not None:
                        circuit.append(
                            "OBSERVABLE_INCLUDE",
                            [
                                stim.target_rec(
                                    target_rec - len(record.get_all_records())
                                )
                            ],
                            0,
                        )
        else:
            shrk.append_body_detector(round_shrink)

    # Z_measurement
    z_measurement = Z_measurement(circuit, alloc.loc, d, p, 0, record, l, z_detector)
    z_measurement.initialize()
    z_measurement.append_syndrome()
    z_measurement.append_head_detector()

    for qubit_index in z_measurement.data_list:
        pos = z_measurement.loc.get_location(qubit_index)
        x = pos[0]
        y = pos[1]
        if x == z_measurement.Q1_MAX_X or x == z_measurement.Q2_MIN_X:
            target_rec = record.get_record((x, y, record.get_t() - 1))
            if target_rec is not None:
                circuit.append(
                    "OBSERVABLE_INCLUDE",
                    [stim.target_rec(target_rec - len(record.get_all_records()))],
                    0,
                )

    return circuit
