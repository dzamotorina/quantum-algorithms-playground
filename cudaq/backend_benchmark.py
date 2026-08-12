import cudaq
import timeit

@cudaq.kernel
def kernel(qubit_count: int):
    qvector = cudaq.qvector(qubit_count)
    h(qvector[0])

    for i in range(qubit_count - 1):
        x.ctrl(qvector[i], qvector[i + 1])

    mz(qvector)

qubit_count = 25
shots = 100000

def run():
    cudaq.sample(kernel, qubit_count, shots_count=shots)

cudaq.set_target("qpp-cpu")

print("Target:", cudaq.get_target().name)
print("CPU time:", timeit.timeit(run, number=1))

if cudaq.num_available_gpus() > 0:
    cudaq.set_target("nvidia")
    print("GPU time:", timeit.timeit(run, number=1))