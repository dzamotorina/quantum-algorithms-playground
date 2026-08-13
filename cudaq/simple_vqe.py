import cudaq
from cudaq import spin
from typing import List


# ------------------------------------------------------------
# 1. Define the Hamiltonian H
# ------------------------------------------------------------
# This operator represents the energy of the physical system.
# VQE will try to find a quantum state whose expectation value
# <psi|H|psi> is as small as possible.
#
# Each term is a Pauli operator acting on one or more qubits.
hamiltonian = (
    5.907
    - 2.1433 * spin.x(0) * spin.x(1)
    - 2.1433 * spin.y(0) * spin.y(1)
    + 0.21829 * spin.z(0)
    - 6.125 * spin.z(1)
)


# ------------------------------------------------------------
# 2. Define the ansatz
# ------------------------------------------------------------
# The ansatz is a parameterized quantum circuit.
#
# Different values of angles[0] prepare different candidate
# quantum states |psi(theta)>.
#
# The optimizer will keep changing theta, trying to find the
# state with the lowest energy.
@cudaq.kernel
def kernel(angles: List[float]):

    # Allocate two qubits, initially in |00>.
    qubits = cudaq.qvector(2)

    # Flip the first qubit:
    # |00> -> |10>
    x(qubits[0])

    # Rotate the second qubit by an adjustable angle theta.
    # This is what makes the circuit variational.
    #
    # Different theta values produce different quantum states.
    ry(angles[0], qubits[1])

    # Entangle the two qubits.
    # q1 is the control, q0 is the target.
    x.ctrl(qubits[1], qubits[0])

    # No measurement here.
    #
    # cudaq.observe() needs access to the prepared quantum state
    # so it can evaluate the Hamiltonian on that state.


# ------------------------------------------------------------
# 3. Define the objective function
# ------------------------------------------------------------
# The classical optimizer calls this function repeatedly.
#
# Its job is:
#   theta
#      ↓
# prepare |psi(theta)>
#      ↓
# compute <psi(theta)|H|psi(theta)>
#      ↓
# return that energy
def objective(parameters):

    # Run the ansatz using the current parameters,
    # then compute the expectation value of the Hamiltonian.
    #
    # This does NOT evolve the state using H.
    # It asks:
    #
    # "What is the expected energy of this prepared state?"
    result = cudaq.observe(
        kernel,
        hamiltonian,
        parameters
    )

    # Extract the numerical expectation value.
    energy = result.expectation()

    # Print each trial so we can actually watch VQE searching.
    print(
        f"theta = {parameters[0]:.6f}, "
        f"energy = {energy:.10f}"
    )

    # COBYLA wants a number to minimize.
    # So we return the energy.
    return energy


# ------------------------------------------------------------
# 4. Choose a classical optimizer
# ------------------------------------------------------------
# COBYLA is a derivative-free optimization algorithm.
#
# It does not know quantum mechanics.
# It only sees:
#
# theta -> energy
#
# and tries to find the theta that produces the smallest energy.
optimizer = cudaq.optimizers.COBYLA()


# ------------------------------------------------------------
# 5. Run the classical optimization loop
# ------------------------------------------------------------
# dimensions=1 means there is only one adjustable parameter:
# angles[0] = theta.
#
# Internally, this repeatedly does something like:
#
# theta_1 -> quantum state -> energy_1
# theta_2 -> quantum state -> energy_2
# theta_3 -> quantum state -> energy_3
# ...
#
# until the optimizer thinks it has found the minimum.
energy, parameters = optimizer.optimize(
    dimensions=1,
    function=objective
)


# ------------------------------------------------------------
# 6. Show the VQE result
# ------------------------------------------------------------
# energy:
#   the smallest expectation value found
#
# parameters[0]:
#   the theta that produced that low-energy state
print("\nMinimum energy:", energy)
print("Optimal theta:", parameters[0])