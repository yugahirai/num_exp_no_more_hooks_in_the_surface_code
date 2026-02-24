import stim
from . import _constbase as constbase
from . import _location as loc
from . import _operators as op
from . import record as rec


class XX_measurement(constbase.ConstBase):
    def __init__(
        self,
        circuit: stim.Circuit,
        location: loc.Location,
        d: int,
        p: float,
        tick: int,
        record: rec.Record,
        l: int,
        x_detector: bool = True,
        z_detector: bool = True,
    ):
        super().__init__(circuit)
        self.loc = location
        self.d = d
        self.p = p
        self.tick = tick
        self.check_direction_x = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.check_direction_z = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        self.record = record
        self.type = type
        self.Q1_MIN_X = 0
        self.Q1_MAX_X = 2 * (self.d - 1)
        self.Q1_MIN_Y = 0 + 2 * (self.d)
        self.Q1_MAX_Y = 2 * (self.d - 1) + 2 * (self.d)
        self.Q2_MIN_X = 2 * (2 * self.d) + 2 * l
        self.Q2_MAX_X = 2 * (self.d - 1) + 2 * (2 * self.d) + 2 * l
        self.Q2_MIN_Y = 0 + 2 * (self.d)
        self.Q2_MAX_Y = 2 * (self.d - 1) + 2 * (self.d)
        self.x_detector = x_detector
        self.z_detector = z_detector

    def initialize(self):
        self.make_data_list()
        self.make_x_ancilla_list()
        self.make_z_ancilla_list()
        self.delete_x_ancilla_qubit(self.Q1_MAX_X + 1, self.Q1_MAX_Y + 1)
        self.delete_x_ancilla_qubit(self.Q2_MAX_X + 1, self.Q2_MAX_Y + 1)

    def make_data_list(self):
        # logical qubit 1
        min_x = self.Q1_MIN_X
        max_x = self.Q1_MAX_X
        min_y = self.Q1_MIN_Y
        max_y = self.Q1_MAX_Y
        for qubit_index in self.loc.get_all_qubit_indices():
            if self.loc.is_in_data_qubit(qubit_index):
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                if x >= min_x and x <= max_x and y >= min_y and y <= max_y:
                    self.append_data_list(qubit_index)

        # logical qubit 2
        min_x = self.Q2_MIN_X
        max_x = self.Q2_MAX_X
        min_y = self.Q2_MIN_Y
        max_y = self.Q2_MAX_Y
        for qubit_index in self.loc.get_all_qubit_indices():
            if self.loc.is_in_data_qubit(qubit_index):
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                if x >= min_x and x <= max_x and y >= min_y and y <= max_y:
                    self.append_data_list(qubit_index)

        # lattice surgery qubit
        for qubit_index in self.loc.get_all_qubit_indices():
            if self.loc.is_in_data_qubit(qubit_index):
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                if x <= self.Q2_MAX_X and y < self.Q2_MIN_Y:
                    self.append_data_list(qubit_index)

    def make_x_ancilla_list(self):
        # logical qubit 1
        min_x = self.Q1_MIN_X - 1
        max_x = self.Q1_MAX_X + 1
        min_y = self.Q1_MIN_Y - 1
        max_y = self.Q1_MAX_Y + 1
        for qubit_index in self.loc.get_all_ancilla_x_indices():
            pos = self.loc.get_location(qubit_index)
            x = pos[0]
            y = pos[1]
            if x >= min_x and x <= max_x and y > min_y and y < max_y:
                self.append_x_ancilla_list(qubit_index)

        # logical qubit 2
        min_x = self.Q2_MIN_X - 1
        max_x = self.Q2_MAX_X + 1
        min_y = self.Q2_MIN_Y - 1
        max_y = self.Q2_MAX_Y + 1
        for qubit_index in self.loc.get_all_ancilla_x_indices():
            pos = self.loc.get_location(qubit_index)
            x = pos[0]
            y = pos[1]
            if x >= min_x and x <= max_x and y > min_y and y < max_y:
                self.append_x_ancilla_list(qubit_index)

        # lattice surgery qubit
        for qubit_index in self.loc.get_all_ancilla_x_indices():
            if self.loc.is_in_ancilla_x(qubit_index):
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                if x <= self.Q2_MAX_X + 1 and y < self.Q2_MIN_Y:
                    if qubit_index not in self.x_ancilla_list:
                        self.append_x_ancilla_list(qubit_index)

    def make_z_ancilla_list(self):
        # logical qubit 1
        min_x = self.Q1_MIN_X - 1
        max_x = self.Q1_MAX_X + 1
        min_y = self.Q1_MIN_Y - 1
        max_y = self.Q1_MAX_Y + 1
        for qubit_index in self.loc.get_all_ancilla_z_indices():
            pos = self.loc.get_location(qubit_index)
            x = pos[0]
            y = pos[1]
            if x > min_x and x < max_x and y >= min_y and y <= max_y:
                self.append_z_ancilla_list(qubit_index)

        # logical qubit 2
        min_x = self.Q2_MIN_X - 1
        max_x = self.Q2_MAX_X + 1
        min_y = self.Q2_MIN_Y - 1
        max_y = self.Q2_MAX_Y + 1
        for qubit_index in self.loc.get_all_ancilla_z_indices():
            pos = self.loc.get_location(qubit_index)
            x = pos[0]
            y = pos[1]
            if x > min_x and x < max_x and y >= min_y and y <= max_y:
                self.append_z_ancilla_list(qubit_index)

        # lattice surgery qubit
        for qubit_index in self.loc.get_all_ancilla_z_indices():
            if self.loc.is_in_ancilla_z(qubit_index):
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                if x >= 0 and x < self.Q2_MAX_X and y < self.Q2_MIN_Y - 2 and y >= 0:
                    if qubit_index not in self.z_ancilla_list:
                        self.append_z_ancilla_list(qubit_index)

    def append_syndrome(self, round: int, MAX_ROUND: int):
        op.append_hadamard(self.circuit, self.x_ancilla_list, self.p)
        self.append_tick()

        for cycle in range(len(self.check_direction_x)):
            for qubit_index in self.x_ancilla_list:
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                target = self.loc.get_qubit(
                    x + self.check_direction_x[cycle][0],
                    y + self.check_direction_x[cycle][1],
                )
                if target in self.data_list:
                    op.append_cnot(self.circuit, qubit_index, target, self.p)
            for qubit_index in self.z_ancilla_list:
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                target = self.loc.get_qubit(
                    x + self.check_direction_z[cycle][0],
                    y + self.check_direction_z[cycle][1],
                )
                if target in self.data_list:
                    op.append_cnot(self.circuit, target, qubit_index, self.p)
            self.append_tick()
        op.append_hadamard(self.circuit, self.x_ancilla_list, self.p)
        self.append_tick()
        self.append_measurement(round, MAX_ROUND)
        self.append_tick()
        self.append_reset()
        self.append_tick()

    def append_measurement(self, round: int, MAX_ROUND: int):
        for qubit_index in self.x_ancilla_list + self.z_ancilla_list:
            pos = self.loc.get_location(qubit_index)
            x = pos[0]
            y = pos[1]
            op.append_measurement(self.circuit, [qubit_index], self.p)
            self.record.add_record(x, y, self.record.get_t())
        self.record.increment_t()

        if round == MAX_ROUND - 1:
            for qubit_index in self.data_list:
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                if y < self.Q1_MIN_Y:
                    op.append_measurement(self.circuit, [qubit_index], self.p)
                    self.record.add_record(x, y, self.record.get_t())

    def append_reset(self):
        for qubit_index in self.x_ancilla_list + self.z_ancilla_list:
            pos = self.loc.get_location(qubit_index)
            x = pos[0]
            y = pos[1]
            op.append_reset(self.circuit, [qubit_index], self.p)

    def append_head_detector(self):
        if self.z_detector:
            for qubit_index in self.z_ancilla_list:
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                rec_now = self.record.get_record((x, y, self.record.get_t() - 1))
                rec_prev = self.record.get_record((x, y, self.record.get_t() - 2))
                if all(r is not None for r in [rec_now, rec_prev]):
                    self.append_detector([rec_now, rec_prev])
            for qubit_index in self.z_ancilla_list:
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                if y <= self.Q1_MIN_Y - 2:
                    rec_now = self.record.get_record((x, y, self.record.get_t() - 1))
                    if rec_now is not None:
                        self.append_detector([rec_now])

        if self.x_detector:
            for qubit_index in self.x_ancilla_list:
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                rec_now = self.record.get_record((x, y, self.record.get_t() - 1))
                rec_prev = self.record.get_record((x, y, self.record.get_t() - 2))
                if all(r is not None for r in [rec_now, rec_prev]):
                    self.append_detector([rec_now, rec_prev])
