"""Draws a circuit as a picture: one line per qubit, gates as boxes."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle


def draw_circuit(n, ops):
    cols = max(len(ops), 1)
    fig, ax = plt.subplots(figsize=(max(4.5, 0.95 * cols + 1.8), 0.85 * n + 0.6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    y = lambda q: n - 1 - q                      # qubit 0 at the top
    for q in range(n):
        ax.plot([-0.6, cols - 0.4], [y(q), y(q)], color="#444", lw=1.2, zorder=1)
        ax.text(-0.85, y(q), f"q{q}", ha="right", va="center", fontsize=11)

    for i, (name, *qs) in enumerate(ops):
        if name == "CNOT":
            c, t = qs
            ax.plot([i, i], [y(c), y(t)], color="#333", lw=1.6, zorder=2)
            ax.add_patch(Circle((i, y(c)), 0.09, color="#333", zorder=3))
            ax.add_patch(Circle((i, y(t)), 0.2, fc="white", ec="#333", lw=1.6, zorder=3))
            ax.plot([i - 0.2, i + 0.2], [y(t), y(t)], color="#333", lw=1.6, zorder=4)
            ax.plot([i, i], [y(t) - 0.2, y(t) + 0.2], color="#333", lw=1.6, zorder=4)
        else:
            q = qs[0]
            ax.add_patch(Rectangle((i - 0.25, y(q) - 0.25), 0.5, 0.5,
                                   fc="#dbe9ff", ec="#2d5fa8", lw=1.4, zorder=3))
            ax.text(i, y(q), name, ha="center", va="center",
                    fontsize=12, fontweight="bold", color="#1b3d73", zorder=4)

    ax.set_xlim(-1.4, cols - 0.2)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    return fig