# Deutsch--Jozsa Algorithm Execution Trace (After the Oracle)

This document continues from the oracle construction and follows the
execution of `compile_circuit()` and `dj_algorithm()`.

Assume the oracle is balanced:

-   f(001)=1
-   f(011)=1
-   f(100)=1
-   f(111)=1

------------------------------------------------------------------------

## Step 1 -- Initial state

``` python
qc = QuantumCircuit(4, 3)
```

State:

    |0000⟩

q0,q1,q2 are the input register.

q3 is the ancilla.

------------------------------------------------------------------------

## Step 2 -- Prepare the ancilla

``` python
qc.x(3)
```

    |0000⟩

    ↓

    |0001⟩

------------------------------------------------------------------------

## Step 3 -- Apply Hadamards

``` python
qc.h(range(4))
```

Equivalent to:

``` python
qc.h(0)
qc.h(1)
qc.h(2)
qc.h(3)
```

After the first three Hadamards the input register becomes an equal
superposition of all eight inputs.

The ancilla becomes

    |−⟩ = (|0⟩−|1⟩)/√2

Overall state:

    (1/√8) Σ |x⟩|−⟩

------------------------------------------------------------------------

## Step 4 -- Execute the oracle

``` python
qc.compose(function, inplace=True)
```

The oracle implements

    |x,y⟩ → |x,y⊕f(x)⟩

Because the ancilla is in \|−⟩, flipping it introduces a minus sign.

The amplitudes become

    + |000⟩
    - |001⟩
    + |010⟩
    - |011⟩
    - |100⟩
    + |101⟩
    + |110⟩
    - |111⟩

This is phase kickback.

------------------------------------------------------------------------

## Step 5 -- Second Hadamards

``` python
qc.h(range(3))
```

Interference occurs.

For a balanced function,

    Amplitude(|000⟩)=0

The state \|000⟩ disappears.

------------------------------------------------------------------------

## Step 6 -- Measure

``` python
qc.measure(range(3), range(3))
```

Possible outcomes:

    001
    010
    011
    100
    101
    110
    111

You will never measure

    000

------------------------------------------------------------------------

## Step 7 -- Simulator

``` python
result = AerSimulator().run(qc, shots=1, memory=True).result()
```

Suppose it returns

    101

Then

``` python
if "1" in measurements[0]:
    return "balanced"
```

returns

    balanced

------------------------------------------------------------------------

# Complete Flow

    |000⟩|0⟩
          │
          ▼
    X
          │
          ▼
    |000⟩|1⟩
          │
          ▼
    Hadamards
          │
          ▼
    Uniform superposition
          │
          ▼
    Oracle
          │
          ▼
    Phase kickback
          │
          ▼
    Second Hadamards
          │
          ▼
    Interference
          │
          ▼
    Amplitude(|000⟩)=0
          │
          ▼
    Measure
          │
          ▼
    Not 000
          │
          ▼
    Balanced
