
# Deutsch–Jozsa Execution Trace (Worked Example)

This document explains the implementation by tracing **one concrete execution** of the code.

We assume:

```python
num_qubits = 3
```

and that the random choices produced

```python
on_states = [1, 3, 4, 7]
```

This means the hidden Boolean function is:

| Input | f(x) |
|------|------|
|000|0|
|001|1|
|010|0|
|011|1|
|100|1|
|101|0|
|110|0|
|111|1|

The rest of `dj_query()` constructs a quantum circuit that behaves exactly like this truth table.

---

# Step 1

```python
qc = QuantumCircuit(num_qubits + 1)
```

Current values:

```text
num_qubits = 3
```

Creates four qubits.

```
q0
q1
q2
q3
```

Initial quantum state:

```
|0000⟩
```

where

- q0,q1,q2 = input register
- q3 = output (ancilla)

---

# Step 2

```python
if np.random.randint(0,2):
    qc.x(num_qubits)
```

For this example assume the random value is

```python
0
```

Therefore

```python
qc.x(3)
```

is **not executed**.

Circuit is still

```
q0 ─────

q1 ─────

q2 ─────

q3 ─────
```

---

# Step 3

```python
if np.random.randint(0,2):
    return qc
```

Assume second random value is

```python
0
```

Therefore the function **does not return**.

Execution continues to build a balanced oracle.

---

# Step 4

```python
on_states = np.random.choice(...)
```

Assume NumPy returns

```python
on_states = [1,3,4,7]
```

Interpretation:

```
001 -> flip output
011 -> flip output
100 -> flip output
111 -> flip output
```

Everything else leaves the output unchanged.

---

# First loop iteration

```python
state = 1
```

Convert to binary:

```python
bit_string = f"{state:0{num_qubits}b}"
```

Evaluation:

```python
bit_string = "001"
```

Meaning:

We are building the oracle for input **001**.

---

## prepare_controls()

Call:

```python
prepare_controls(qc, "001")
```

Inside:

```python
reversed("001")
```

becomes

```
100
```

Loop execution:

```
qubit = 0, bit='1'
→ qc.x(0)

qubit = 1, bit='0'
→ nothing

qubit = 2, bit='0'
→ nothing
```

Temporary circuit:

```
q0 ─X──

q1 ─────

q2 ─────

q3 ─────
```

The purpose is **not** to compute the function.

It temporarily prepares the controls so the next gate can recognize this input.

---

## MCX

```python
qc.mcx([0,1,2],3)
```

Conceptually:

```
IF controls match the prepared pattern

↓

flip q3
```

This is the line that implements

```
y → y XOR f(x)
```

for this one input.

---

## Undo preparation

Immediately afterwards

```python
prepare_controls(qc,"001")
```

runs again.

The same X gate is applied twice.

```
X · X = Identity
```

So q0 is restored.

The input register finishes exactly as it started.

---

# Second loop iteration

```python
state = 3
```

Binary:

```python
bit_string = "011"
```

Inside prepare_controls():

```
reversed("011")
```

↓

```
110
```

Loop:

```
qubit=0 bit='1'
→ qc.x(0)

qubit=1 bit='1'
→ qc.x(1)

qubit=2 bit='0'
→ nothing
```

Temporary circuit:

```
q0 ─X──

q1 ─X──

q2 ─────
```

Then

```python
qc.mcx(...)
```

marks the input **011**.

The second call to `prepare_controls()` removes the temporary X gates.

---

# Remaining iterations

Exactly the same process happens for

```
state = 4
```

(binary `100`)

and

```
state = 7
```

(binary `111`).

Each iteration adds one more condition under which the ancilla is flipped.

---

# Final result

After the loop finishes, the oracle behaves as:

| Input | Output |
|------|------|
|000|0|
|001|1|
|010|0|
|011|1|
|100|1|
|101|0|
|110|0|
|111|1|

This is exactly the Boolean function defined at the beginning.

---

# The three key lines

Whenever you see

```python
prepare_controls(qc, bit_string)

qc.mcx(list(range(num_qubits)), num_qubits)

prepare_controls(qc, bit_string)
```

read it as:

> "Build the oracle behavior for **one particular input**."

The first call prepares the controls.

The `mcx` flips the ancilla for that prepared input.

The second call restores the input register.

After repeating this for every element of `on_states`, the complete oracle has been constructed.
