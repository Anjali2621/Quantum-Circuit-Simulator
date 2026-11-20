"""Plot: how much do results go wrong as noise goes up?"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from quantum import Circuit

np.random.seed(0)
levels = np.linspace(0, 0.3, 13)

circuits = {
    "Bell state (2 qubits, 2 gates)": Circuit(2).h(0).cnot(0, 1),
    "3 qubits all agree (3 gates)": Circuit(3).h(0).cnot(0, 1).cnot(1, 2),
    "5 qubits all agree (5 gates)": Circuit(5).h(0).cnot(0, 1).cnot(1, 2).cnot(2, 3).cnot(3, 4),
}

for name, c in circuits.items():
    plt.plot(levels * 100, [c.error(p, 800) for p in levels], marker="o", label=name)

plt.xlabel("Noise level (% chance of a mistake after each gate)")
plt.ylabel("Error (0 = perfect, 1 = completely wrong)")
plt.title("More noise and longer circuits give worse results")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("noise_error.png", dpi=130)
print("saved noise_error.png")