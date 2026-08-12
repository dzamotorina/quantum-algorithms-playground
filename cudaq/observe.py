import cudaq
from cudaq import spin

operator = spin.z(0)
print("Operator:", operator)

@cudaq.kernel
def kernel():
    qubit = cudaq.qubit()
    h(qubit)

result = cudaq.observe(kernel, operator)

print("Expectation value:", result.expectation())