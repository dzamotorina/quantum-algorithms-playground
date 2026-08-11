from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def bv_query(secret: str):
    """
    Build a Bernstein-Vazirani oracle.

    The oracle hides a binary string

        s ∈ {0,1}ⁿ

    and implements the Boolean function

        f(x) = s · x

    where the dot product is computed modulo 2.

    Each 1-bit of the secret becomes one CNOT gate from the
    corresponding input qubit to the ancilla.

    Example:

        secret = "1011"

        q0 ----■---------
                |
        q1 --------------
                |
        q2 ----■---------
                |
        q3 ----■---------
                |
        anc ----X---------
    """

    # Create n input qubits plus one ancilla/output qubit.
    qc = QuantumCircuit(len(secret) + 1)

    # Iterate over the secret string.
    #
    # We reverse it because Qiskit uses little-endian ordering:
    #
    #     q0 corresponds to the rightmost bit.
    #
    # Every 1-bit in the secret becomes one CNOT gate.
    for index, bit in enumerate(reversed(secret)):
        if bit == "1":
            qc.cx(index, len(secret))

    return qc


print(bv_query("1011").draw())


def compile_circuit(function: QuantumCircuit):
    """
    Build the full Bernstein-Vazirani circuit.

    Structure:

        prepare input superposition
        prepare ancilla |-> state
        apply oracle
        apply Hadamards again
        measure input register

    The circuit is almost identical to Deutsch-Jozsa.
    The main difference is the oracle.
    """

    # Number of input qubits.
    #
    # The oracle contains:
    #   n input qubits
    #   1 ancilla/output qubit
    n = function.num_qubits - 1

    # Create the complete algorithm circuit.
    #
    # We measure only the input register,
    # so we need n classical bits.
    qc = QuantumCircuit(n + 1, n)

    # Prepare the ancilla as |1>.
    #
    # All qubits begin in |0>.
    qc.x(n)

    # Apply Hadamard gates.
    #
    # Input register:
    #   creates an equal superposition over all x.
    #
    # Ancilla:
    #   |1> becomes
    #
    #       |-> = (|0> - |1>) / √2
    #
    # This state enables phase kickback.
    qc.h(range(n + 1))

    # Apply the Bernstein-Vazirani oracle.
    #
    # The oracle computes
    #
    #     f(x) = s · x
    #
    # Because the ancilla is |->,
    # the function value is converted into a phase:
    #
    #     |x>|->  →  (-1)^(s·x)|x>|->
    #
    # Thus the hidden string is encoded into
    # the phases of the computational basis states.
    qc.compose(function, inplace=True)

    # Apply Hadamards again to the input register.
    #
    # The second Hadamards transform the phase pattern
    #
    #     (-1)^(s·x)
    #
    # back into the computational basis.
    #
    # Constructive interference causes all amplitude
    # to concentrate on
    #
    #     |s>
    #
    # so measuring the input register directly
    # reveals the hidden string.
    qc.h(range(n))

    # Measure only the input register.
    #
    # The ancilla is no longer needed.
    qc.measure(range(n), range(n))

    return qc


def bv_algorithm(function: QuantumCircuit):
    """
    Run the Bernstein-Vazirani algorithm.

    Unlike Deutsch-Jozsa, no post-processing is required.

    An ideal execution measures the hidden string directly.
    """

    # Build the complete circuit.
    qc = compile_circuit(function)

    # One shot is sufficient because the algorithm
    # is deterministic on an ideal quantum computer.
    result = AerSimulator().run(
        qc,
        shots=1,
        memory=True,
    ).result()

    # Return the measured bit string.
    #
    # This is exactly the hidden secret s.
    return result.get_memory()[0]


# Build an oracle hiding the secret string.
oracle = bv_query("1011")

# Display the oracle circuit.
print(oracle.draw())
print()

# Recover and print the hidden string.
print(bv_algorithm(oracle))