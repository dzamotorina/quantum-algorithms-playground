from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np


def dj_query(num_qubits):
    """
    Build a random Deutsch-Jozsa oracle.

    The oracle represents a hidden Boolean function:

        f: {0,1}^n -> {0,1}

    Deutsch-Jozsa assumes a promise:
        - f is constant: all inputs return the same value
        - OR f is balanced: exactly half return 0 and half return 1

    This function randomly creates one of those two valid cases.
    """

    # We need n input qubits plus 1 output/ancilla qubit.
    #
    # For num_qubits = 3:
    #   q0, q1, q2 = input register x
    #   q3         = output/ancilla y
    qc = QuantumCircuit(num_qubits + 1)

    # With 50% probability, flip the output qubit.
    #
    # If we later return immediately, this gives the constant-1 function:
    #   f(x) = 1 for every x
    #
    # If this line is skipped and we return immediately, we get constant-0:
    #   f(x) = 0 for every x
    if np.random.randint(0, 2):
        qc.x(num_qubits)

    # With 50% probability, return now.
    #
    # If we return here, the oracle is constant:
    #   - no X gate on output  -> constant 0
    #   - X gate on output     -> constant 1
    if np.random.randint(0, 2):
        return qc

    # If we did not return, we build a balanced function.
    #
    # There are 2^n possible input strings.
    # A balanced function must output 1 on exactly half of them.
    #
    # Example for n = 3:
    #   total inputs = 8
    #   choose 4 inputs where f(x)=1
    on_states = np.random.choice(
        range(2**num_qubits),
        2**num_qubits // 2,
        replace=False,
    )

    def prepare_controls(qc, bit_string):
        """
        Helper function that adds X gates to input qubits according to bit_string.

        We reverse bit_string because Qiskit uses little-endian qubit ordering:
            q0 corresponds to the rightmost bit.
        """

        for qubit, bit in enumerate(reversed(bit_string)):
            if bit == "1":
                qc.x(qubit)

        return qc

    # For every selected input state where f(x)=1,
    # add a multi-controlled X gate that flips the output qubit only for that input.
    for state in on_states:
        qc.barrier()

        # Convert state number into an n-bit binary string.
        #
        # Example:
        #   state = 3, num_qubits = 3
        #   bit string = "011"
        bit_string = f"{state:0{num_qubits}b}"

        # Temporarily flip selected input qubits so that the desired pattern
        # can be detected by the multi-controlled X gate.
        qc = prepare_controls(qc, bit_string)

        # Multi-controlled X:
        #
        # If all input qubits are 1, flip the output qubit.
        #
        # This is the operation that makes f(x)=1 for the selected input state.
        qc.mcx(list(range(num_qubits)), num_qubits)

        # Undo the temporary X gates.
        #
        # This is important because the oracle should not permanently change
        # the input register. It should only modify the output qubit.
        qc = prepare_controls(qc, bit_string)

    qc.barrier()

    # Return the oracle circuit U_f.
    return qc


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


def dj_algorithm(function: QuantumCircuit):
    """
    Run Deutsch-Jozsa algorithm and classify the oracle.

    Output:
        "constant" or "balanced"
    """

    # Build the full algorithm circuit.
    qc = compile_circuit(function)

    # Run the circuit once on a local simulator.
    #
    # shots=1 is enough because ideal Deutsch-Jozsa is deterministic.
    #
    # memory=True returns the actual measured bitstring, e.g.:
    #   ["000"] or ["101"]
    result = AerSimulator().run(qc, shots=1, memory=True).result()

    # Extract the measured bitstring.
    measurements = result.get_memory()

    # If any measured input bit is 1, the function is balanced.
    #
    # Constant functions always produce:
    #   00...0
    #
    # Balanced functions produce:
    #   something other than 00...0
    if "1" in measurements[0]:
        return "balanced"

    return "constant"


# Build one random Deutsch-Jozsa oracle with 3 input qubits.
query = dj_query(3)

# Print the oracle circuit only.
print(query.draw())
print()

# Run Deutsch-Jozsa on the oracle and print the classification.
print(dj_algorithm(query))