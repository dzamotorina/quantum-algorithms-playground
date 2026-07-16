from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np


def bv_query(s):
    # Create a quantum circuit implementing a query gate for the
    # Bernstein-Vazirani problem.

    qc = QuantumCircuit(len(s) + 1)
    for index, bit in enumerate(reversed(s)):
        if bit == "1":
            qc.cx(index, len(s))
    return qc


print(bv_query("1011").draw())


def compile_circuit(function: QuantumCircuit):
    """
    Build the full Deutsch-Jozsa circuit using the given oracle.

    Structure:

        prepare input superposition
        prepare ancilla |-> state
        apply oracle
        apply Hadamards again
        measure input register
    """

    # Number of input qubits.
    #
    # The oracle has:
    #   n input qubits + 1 output/ancilla qubit
    n = function.num_qubits - 1

    # Create full Deutsch-Jozsa circuit:
    #   n + 1 quantum bits
    #   n classical bits for measuring the input register
    qc = QuantumCircuit(n + 1, n)

    # Prepare the ancilla/output qubit as |1>.
    #
    # It starts as |0>, so X turns it into |1>.
    qc.x(n)

    # Apply Hadamard to all qubits.
    #
    # Input register:
    #   |00...0> becomes equal superposition over all inputs.
    #
    # Ancilla:
    #   |1> becomes |-> = (|0> - |1>) / sqrt(2)
    #
    # This |-> state is what enables phase kickback.
    qc.h(range(n + 1))

    # Insert the oracle U_f.
    #
    # Because the ancilla is |->, the oracle encodes f(x)
    # as a phase:
    #
    #   f(x)=0 -> + sign
    #   f(x)=1 -> - sign
    qc.compose(function, inplace=True)

    # Apply Hadamard to the input register again.
    #
    # This causes interference.
    #
    # If f is constant:
    #   all phases align, and measurement gives 00...0
    #
    # If f is balanced:
    #   phases cancel for 00...0, so measurement gives something else
    qc.h(range(n))

    # Measure only the input qubits.
    #
    # We do not need to measure the ancilla.
    qc.measure(range(n), range(n))

    return qc


def bv_algorithm(function: QuantumCircuit):
    qc = compile_circuit(function)
    result = AerSimulator().run(qc, shots=1, memory=True).result()
    return result.get_memory()[0]


print(bv_algorithm(bv_query("1011")))