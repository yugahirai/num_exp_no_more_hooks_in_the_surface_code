import stim

from src import make_circuit

d = 11
l = 0

circuit = make_circuit.main(d, 0.1, l)
sampler = circuit.compile_detector_sampler()
dem = circuit.detector_error_model(decompose_errors=False)
length = dem.shortest_graphlike_error()

print(length)
print(len(length))
