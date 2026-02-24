import stim
from abc import ABC, abstractmethod
from typing import List
from . import _location as loc
from . import _operators as op
from . import record as rec


class ConstBase(ABC):
    def __init__(
        self, circuit: stim.Circuit, z_detector: bool = True, x_detector: bool = True
    ):
        self.circuit = circuit
        self.d: int = 0
        self.loc: loc.Location = loc.Location()
        self.data_list: List[int] = []
        self.x_ancilla_list: List[int] = []
        self.z_ancilla_list: List[int] = []
        self.p: float = 0.0
        self.tick: int = 0
        self.record: rec.Record = {}
        self.z_detector = z_detector
        self.x_detector = x_detector

    @abstractmethod
    def append_syndrome(self):
        pass

    def append_body_detector(self):
        if self.z_detector:
            for qubit_index in self.z_ancilla_list:
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                rec_now = self.record.get_record((x, y, self.record.get_t() - 1))
                rec_prev = self.record.get_record((x, y, self.record.get_t() - 2))
                if rec_now is not None and rec_prev is not None:
                    self.append_detector([rec_now, rec_prev])

        if self.x_detector:
            for qubit_index in self.x_ancilla_list:
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                rec_now = self.record.get_record((x, y, self.record.get_t() - 1))
                rec_prev = self.record.get_record((x, y, self.record.get_t() - 2))
                if rec_now is not None and rec_prev is not None:
                    self.append_detector([rec_now, rec_prev])

    def append_detector(self, target_rec: list):
        stim_target_rec = []
        for target in target_rec:
            stim_target_rec.append(
                stim.target_rec(target - len(self.record.get_all_records()))
            )
        self.circuit.append("DETECTOR", stim_target_rec)

    def append_data_list(self, qubit_index: int):
        self.data_list.append(qubit_index)

    def append_x_ancilla_list(self, qubit_index: int):
        self.x_ancilla_list.append(qubit_index)

    def append_z_ancilla_list(self, qubit_index: int):
        self.z_ancilla_list.append(qubit_index)

    def append_tick(self):
        op.append_tick(self.circuit)
        self.tick += 1

    def delete_data_qubit(self, x: int, y: int):
        qubit_index = self.loc.get_qubit(x, y)
        if qubit_index is not None and qubit_index in self.data_list:
            self.data_list.remove(qubit_index)

    def delete_x_ancilla_qubit(self, x: int, y: int):
        qubit_index = self.loc.get_qubit(x, y)
        if qubit_index is not None and qubit_index in self.x_ancilla_list:
            self.x_ancilla_list.remove(qubit_index)

    def delete_z_ancilla_qubit(self, x: int, y: int):
        qubit_index = self.loc.get_qubit(x, y)
        if qubit_index is not None and qubit_index in self.z_ancilla_list:
            self.z_ancilla_list.remove(qubit_index)
