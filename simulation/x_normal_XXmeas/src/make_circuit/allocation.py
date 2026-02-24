import stim
from . import _constbase as constbase
from . import _operators as op


class Allocation(constbase.ConstBase):
    def __init__(self, circuit: stim.Circuit, d: int, p: float, l: int):
        super().__init__(circuit)
        self.d = d
        self.p = p
        self.l = l
        self.Q1_MIN_X = 0
        self.Q1_MAX_X = 2 * (self.d - 1)
        self.Q1_MIN_Y = 0 + 2 * (self.d)
        self.Q1_MAX_Y = 2 * (self.d - 1) + 2 * (self.d)
        self.Q2_MIN_X = 2 * (2 * self.d) + 2 * l
        self.Q2_MAX_X = 2 * (self.d - 1) + 2 * (2 * self.d) + 2 * l
        self.Q2_MIN_Y = 0 + 2 * (self.d)
        self.Q2_MAX_Y = 2 * (self.d - 1) + 2 * (self.d)

    def allocate_data_qubits(self):
        for i in range(0, 3 * self.d + 1 + self.l):
            for j in range(0, 2 * self.d):
                pos = (2 * i, 2 * j)
                x = pos[0]
                y = pos[1]
                if (
                    x >= self.Q1_MIN_X
                    and x <= self.Q2_MAX_X
                    and y >= 0
                    and y <= self.Q1_MAX_Y
                ):
                    qubit_index = self.loc.add_qubit(x, y)
                    self.loc.add_data_qubit(qubit_index)
                    self.append_data_list(qubit_index)

    def allocate_ancilla_qubits(self):
        for i in range(-1, 3 * self.d + 1 + self.l):
            for j in range(-1, 2 * self.d):
                pos = (2 * i + 1, 2 * j + 1)
                x = pos[0]
                y = pos[1]
                if (
                    x >= self.Q1_MIN_X - 1
                    and x <= self.Q2_MAX_X + 1
                    and y >= -1
                    and y <= self.Q1_MAX_Y + 1
                ):
                    qubit_index = self.loc.add_qubit(x, y)

                    if y % 4 == (x + 2) % 4:
                        self.loc.add_ancilla_x(qubit_index)
                        self.append_x_ancilla_list(qubit_index)
                    else:
                        self.loc.add_ancilla_z(qubit_index)
                        self.append_z_ancilla_list(qubit_index)

    def search_around(self, pos):
        found = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 or j == 0:
                    continue
                try:
                    qubit_index = self.loc.get_qubit(pos[0] + i, pos[1] + j)
                    if self.loc.is_in_data_qubit(qubit_index):
                        found.append((pos[0] + i, pos[1] + j))
                except KeyError:
                    # Position doesn't have a qubit
                    pass
        return found

    def append_coords(self):
        for qubit_index in range(self.loc.get_qubit_index_counter()):
            (x, y) = self.loc.get_location(qubit_index)
            self.circuit.append("QUBIT_COORDS", [qubit_index], [x, y])

    def append_reset_all_qubits(self):
        for qubit_index in self.loc.get_all_qubit_indices():
            op.append_reset(self.circuit, [qubit_index], self.p)

    def append_x_reset_all_qubits(self):
        for qubit_index in self.loc.get_all_qubit_indices():
            if self.loc.is_in_ancilla_x(qubit_index) or self.loc.is_in_ancilla_z(
                qubit_index
            ):
                op.append_reset(self.circuit, [qubit_index], self.p)
            else:
                op.append_x_reset(self.circuit, [qubit_index], self.p)
        self.append_tick()

    def append_syndrome(self):
        pass

    def append_detector(self):
        pass
