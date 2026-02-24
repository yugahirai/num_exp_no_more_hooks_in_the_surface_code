class Location:
    def __init__(self):
        self.__q2i = {}
        self.__i2q = {}
        self.__data_qubit_indices = set()
        self.__ancilla_x_indices = set()
        self.__ancilla_z_indices = set()
        self.__qubit_index_counter = 0

    def __len__(self):
        return len(self.__q2i)

    def is_in_data_qubit(self, qubit: int):
        return qubit in self.__data_qubit_indices

    def add_qubit(self, x: int, y: int):
        qubit_index = self.__qubit_index_counter
        self.__q2i[qubit_index] = (x, y)
        self.__i2q[(x, y)] = qubit_index
        self.__qubit_index_counter += 1
        return qubit_index

    def get_qubit_index_counter(self):
        return self.__qubit_index_counter

    def get_qubit(self, x: int, y: int):
        return self.__i2q.get((x, y))

    def get_location(self, qubit: int):
        return self.__q2i.get(qubit)

    def get_all_qubit_indices(self):
        return list(self.__q2i.keys())

    def is_in_ancilla_x(self, qubit: int):
        return qubit in self.__ancilla_x_indices

    def is_in_ancilla_z(self, qubit: int):
        return qubit in self.__ancilla_z_indices

    def get_all_ancilla_x_indices(self):
        return list(self.__ancilla_x_indices)

    def get_all_ancilla_z_indices(self):
        return list(self.__ancilla_z_indices)

    def add_data_qubit(self, qubit: int):
        self.__data_qubit_indices.add(qubit)

    def add_ancilla_x(self, qubit: int):
        self.__ancilla_x_indices.add(qubit)

    def add_ancilla_z(self, qubit: int):
        self.__ancilla_z_indices.add(qubit)
