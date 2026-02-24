import stim
from . import _constbase as constbase
from . import _location as loc
from . import _operators as op
from . import record as rec


class shrink(constbase.ConstBase):
    def __init__(
        self,
        circuit: stim.Circuit,
        location: loc.Location,
        d: int,
        p: float,
        tick: int,
        record: rec.Record,
        previous_data_list: list[int],
        previous_x_ancilla_list: list[int],
        previous_z_ancilla_list: list[int],
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
        self.previous_data_list = previous_data_list
        self.previous_x_ancilla_list = previous_x_ancilla_list
        self.previous_z_ancilla_list = previous_z_ancilla_list
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

    def append_syndrome(self, round: int, MAX_ROUND: int):
        op.append_hadamard(self.circuit, self.x_ancilla_list, self.p)
        self.append_tick()

        self.check_direction_x.reverse()
        self.check_direction_z.reverse()

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
        self.append_measurement()
        if round < MAX_ROUND - 1:
            self.append_tick()
            self.append_reset()
            self.append_tick()

    def shrink(self):
        for qubit_index in self.previous_data_list:
            pos = self.loc.get_location(qubit_index)
            x = pos[0]
            y = pos[1]
            if y < self.Q1_MIN_Y:
                op.append_measurement(self.circuit, [qubit_index], self.p)
                self.record.add_record(x, y, self.record.get_t())

    def append_measurement(self):
        for qubit_index in self.x_ancilla_list + self.z_ancilla_list:
            pos = self.loc.get_location(qubit_index)
            x = pos[0]
            y = pos[1]
            op.append_measurement(self.circuit, [qubit_index], self.p)
            self.record.add_record(x, y, self.record.get_t())
        self.record.increment_t()

    def append_reset(self):
        for qubit_index in self.x_ancilla_list + self.z_ancilla_list:
            pos = self.loc.get_location(qubit_index)
            x = pos[0]
            y = pos[1]
            op.append_reset(self.circuit, [qubit_index], self.p)

    def append_head_detector(self):
        # Z detectors
        if self.z_detector:
            for qubit_index in self.previous_z_ancilla_list:
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                if y <= self.Q1_MIN_Y and y > -1 and x < self.Q2_MAX_X + 1:
                    if y == self.Q1_MIN_Y - 1:
                        found_rec = self.search_around_detector(qubit_index)
                        rec_now = self.record.get_record(
                            (x, y, self.record.get_t() - 1)
                        )
                        rec_prev = self.record.get_record(
                            (x, y, self.record.get_t() - 2)
                        )
                        if all(r is not None for r in [found_rec, rec_now, rec_prev]):
                            self.append_detector(found_rec + [rec_now, rec_prev])
                    else:
                        found_rec = self.search_around_detector(qubit_index)
                        rec_prev = self.record.get_record(
                            (x, y, self.record.get_t() - 2)
                        )
                        if all(r is not None for r in [found_rec, rec_prev]):
                            self.append_detector(found_rec + [rec_prev])
            for qubit_index in self.z_ancilla_list:
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                if y >= self.Q1_MIN_Y:
                    rec_now = self.record.get_record((x, y, self.record.get_t() - 1))
                    rec_prev = self.record.get_record((x, y, self.record.get_t() - 2))
                    if all(r is not None for r in [rec_now, rec_prev]):
                        self.append_detector([rec_now, rec_prev])

        # X detectors
        if self.x_detector:
            for qubit_index in self.x_ancilla_list:
                pos = self.loc.get_location(qubit_index)
                x = pos[0]
                y = pos[1]
                rec_now = self.record.get_record((x, y, self.record.get_t() - 1))
                rec_prev = self.record.get_record((x, y, self.record.get_t() - 2))
                if all(r is not None for r in [rec_now, rec_prev]):
                    self.append_detector([rec_now, rec_prev])

    def search_around_detector(self, qubit_index):
        pos = self.loc.get_location(qubit_index)
        x = pos[0]
        y = pos[1]
        found_rec = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                target_rec = self.record.get_record(
                    (x + i, y + j, self.record.get_t() - 1)
                )
                if target_rec is not None:
                    found_rec.append(target_rec)
        return found_rec
