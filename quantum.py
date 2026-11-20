"""A small quantum circuit simulator, written from scratch.

Qubit 0 is the leftmost one in results like "01" (so in "10", qubit 0 is 1).
"""
import numpy as np

# ---- the basic gates (small grids of numbers) -----------------------------
I = np.array([[1, 0],
              [0, 1]])                       # do nothing
X = np.array([[0, 1],
              [1, 0]])                       # flip 0 <-> 1
Z = np.array([[1, 0],
              [0, -1]])                      # flips the sign of the "1" number
H = (1 / np.sqrt(2)) * np.array([[1, 1],
                                 [1, -1]])   # 0 -> 50/50 mix

ONE_QUBIT_GATES = {"H": H, "X": X, "Z": Z}


# ---- turning a gate into a grid that fits the whole circuit ---------------
def single_gate_matrix(gate, qubit, n):
    """Put a one-qubit gate on `qubit`; every other qubit gets 'do nothing'."""
    result = np.array([[1]])
    for q in range(n):
        result = np.kron(result, gate if q == qubit else I)
    return result


def cnot_matrix(control, target, n):
    """If the control qubit is 1, flip the target qubit."""
    size = 2 ** n
    m = np.zeros((size, size))
    for i in range(size):                      # i = one possible result, e.g. 10
        control_bit = (i >> (n - 1 - control)) & 1
        j = i ^ (1 << (n - 1 - target)) if control_bit else i
        m[j, i] = 1                            # result i turns into result j
    return m


# ---- the circuit ----------------------------------------------------------
class Circuit:
    def __init__(self, n_qubits):
        if not 1 <= n_qubits <= 10:
            raise ValueError("Use between 1 and 10 qubits")
        self.n = n_qubits
        self.ops = []                          # list of (name, qubits...)
        self._matrices = {}                    # remembers grids so we build each once

    # adding gates (each returns self so you can chain them)
    def _add(self, name, *qubits):
        for q in qubits:
            if not 0 <= q < self.n:
                raise ValueError(f"Qubit {q} does not exist")
        self.ops.append((name, *qubits))
        return self

    def h(self, q): return self._add("H", q)
    def x(self, q): return self._add("X", q)
    def z(self, q): return self._add("Z", q)

    def cnot(self, control, target):
        if control == target:
            raise ValueError("Control and target must be different")
        return self._add("CNOT", control, target)

    # running
    def _matrix_for(self, op):
        if op not in self._matrices:
            name, *qs = op
            if name == "CNOT":
                self._matrices[op] = cnot_matrix(qs[0], qs[1], self.n)
            else:
                self._matrices[op] = single_gate_matrix(ONE_QUBIT_GATES[name], qs[0], self.n)
        return self._matrices[op]

    def _flip(self, state, qubit):
        """A tiny mistake: flip one qubit (swap its 0 and 1 parts)."""
        grid = state.reshape((2,) * self.n)
        return np.flip(grid, axis=qubit).reshape(-1)

    def run(self, noise=0.0):
        """Run the circuit once.

        noise = chance (0 to 1) that each qubit a gate touches gets flipped by mistake
        right after the gate. noise=0 means a perfect run.
        """
        state = np.zeros(2 ** self.n)
        state[0] = 1                           # start with everything at 0
        for op in self.ops:
            state = self._matrix_for(op) @ state
            if noise > 0:
                for q in op[1:]:               # the qubits this gate touched
                    if np.random.random() < noise:
                        state = self._flip(state, q)
        return state

    def labels(self):
        return [format(i, f"0{self.n}b") for i in range(2 ** self.n)]

    def probabilities(self):
        """The perfect (no noise) chances of each result."""
        return dict(zip(self.labels(), np.abs(self.run()) ** 2))

    def measure(self, shots=1000, noise=0.0):
        """Run and look `shots` times. With noise, every shot is its own run with
        its own random mistakes."""
        labels = self.labels()
        counts = dict.fromkeys(labels, 0)
        if noise == 0:
            p = np.abs(self.run()) ** 2
            for r in np.random.choice(labels, size=shots, p=p / p.sum()):
                counts[r] += 1
        else:
            for _ in range(shots):
                p = np.abs(self.run(noise)) ** 2
                counts[np.random.choice(labels, p=p / p.sum())] += 1
        return {l: c for l, c in counts.items() if c > 0}

    def error(self, noise, shots=1000):
        """How far noisy results are from perfect ones: 0 = identical, 1 = completely off.
        (It is the share of results that landed in the 'wrong' places.)"""
        ideal = self.probabilities()
        counts = self.measure(shots, noise)
        return 0.5 * sum(abs(counts.get(l, 0) / shots - ideal[l]) for l in ideal)


if __name__ == "__main__":
    bell = Circuit(2).h(0).cnot(0, 1)
    print("Perfect:      ", bell.measure(1000))
    print("Noise = 10%:  ", bell.measure(1000, noise=0.10))