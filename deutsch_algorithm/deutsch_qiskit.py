from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def deutsch_function(case: int):
    """
    Build one of the four possible oracle circuits U_f.

    There are only four Boolean functions from one bit to one bit:

        Case 1: f(x) = 0          (constant)
        Case 2: f(x) = x          (balanced)
        Case 3: f(x) = NOT(x)     (balanced)
        Case 4: f(x) = 1          (constant)

    Instead of returning f(x), the oracle implements

        |x,y> → |x, y XOR f(x)>

    where
        x = input qubit
        y = output/ancilla qubit
    """

    # Reject invalid cases.
    if case not in [1, 2, 3, 4]:
        raise ValueError("`case` must be 1, 2, 3, or 4.")

    # Create a 2-qubit oracle.
    #
    # q0 = input x
    # q1 = output/ancilla y
    f = QuantumCircuit(2)

    # Cases 2 and 3 both require:
    #
    # y -> y XOR x
    #
    # A CNOT performs exactly this operation:
    #
    # if x=1:
    #     flip y
    #
    # Therefore:
    #
    # Case 2:
    #     f(x)=x
    #
    # Case 3:
    #     starts as f(x)=x,
    #     then another X gate changes it into NOT(x).
    if case in [2, 3]:
        f.cx(0, 1)

    # Cases 3 and 4 require flipping the output qubit.
    #
    # Case 4:
    #     y -> y XOR 1
    #
    # giving
    #
    #     f(x)=1
    #
    # Case 3:
    #
    #     y XOR x XOR 1
    #
    # which is
    #
    #     y XOR NOT(x)
    if case in [3, 4]:
        f.x(1)

    # Return the oracle U_f.
    return f


def compile_circuit(function: QuantumCircuit):
    """
    Build the complete Deutsch algorithm.

    Structure:

        prepare input state
            ↓
        prepare ancilla
            ↓
        Hadamards
            ↓
        Oracle U_f
            ↓
        Hadamards
            ↓
        Measure
    """

    # Number of input qubits.
    #
    # The oracle has:
    #
    #     n input qubits
    #     1 ancilla/output qubit
    #
    # Therefore
    #
    #     n = total qubits - 1
    n = function.num_qubits - 1

    # Build the complete circuit.
    #
    # Quantum bits:
    #     n+1
    #
    # Classical bits:
    #     n
    #
    # We only measure the input register.
    qc = QuantumCircuit(n + 1, n)

    # Prepare ancilla.
    #
    # Initial state:
    #
    #     |0>|0>
    #
    # After X:
    #
    #     |0>|1>
    #
    # Later Hadamard transforms
    #
    #     |1> -> |->
    #
    # which enables phase kickback.
    qc.x(n)

    # Apply Hadamard to every qubit.
    #
    # Input:
    #
    #     |0> -> |+>
    #
    # giving superposition of all inputs.
    #
    # Ancilla:
    #
    #     |1> -> |->
    qc.h(range(n + 1))

    # Visual separator only.
    qc.barrier()

    # Insert the oracle into the circuit.
    #
    # This is the only query to the hidden function.
    #
    # Because the ancilla is |->,
    # the oracle no longer stores f(x) in the ancilla.
    #
    # Instead it changes the PHASE of each basis state:
    #
    #     f(x)=0  -> plus sign
    #     f(x)=1  -> minus sign
    qc.compose(function, inplace=True)

    # Visual separator.
    qc.barrier()

    # Apply Hadamard again.
    #
    # This converts the phase information
    # into constructive/destructive interference.
    #
    # Constant:
    #
    #     measure 0
    #
    # Balanced:
    #
    #     measure 1
    qc.h(range(n))

    # Measure only the input qubits.
    #
    # The ancilla has already done its job.
    qc.measure(range(n), range(n))

    return qc


# Draw the complete circuit for Case 3.
#
# Case 3:
#
#     f(0)=1
#     f(1)=0
#
# which is balanced.
print(compile_circuit(deutsch_function(3)).draw())


def deutsch_algorithm(function: QuantumCircuit):
    """
    Run Deutsch's algorithm and classify the oracle.

    Output:

        constant
        or
        balanced
    """

    # Build the complete Deutsch circuit.
    qc = compile_circuit(function)

    # Run on the simulator.
    #
    # Deutsch's algorithm is deterministic,
    # therefore one shot is sufficient.
    result = AerSimulator().run(
        qc,
        shots=1,
        memory=True
    ).result()

    # Retrieve the measured bit.
    #
    # Example:
    #
    #     ["0"]
    #
    # or
    #
    #     ["1"]
    measurements = result.get_memory()

    # Interpretation:
    #
    #     0 -> constant
    #     1 -> balanced
    if measurements[0] == "0":
        return "constant"

    return "balanced"


# Build Case 4 oracle.
#
# Case 4:
#
#     f(x)=1
#
# Constant function.
f = deutsch_function(4)

# Run Deutsch's algorithm.
print(deutsch_algorithm(f))