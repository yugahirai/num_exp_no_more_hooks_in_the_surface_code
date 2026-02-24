class Record:
    def __init__(self):
        self.record = {}
        self.__t = 0
        self.record_counter = 0

    def add_record(self, x: int, y: int, t: int):
        self.record[(x, y, t)] = self.record_counter
        self.record_counter += 1

    def get_record(self, x_y_t_pos: tuple):
        return self.record.get(x_y_t_pos)

    def get_all_records(self):
        return list(self.record.keys())

    def get_t(self):
        return self.__t

    def increment_t(self):
        self.__t += 1
