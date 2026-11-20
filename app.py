import numpy as np
import pandas as pd
import streamlit as st

from quantum import Circuit
from diagram import draw_circuit

st.set_page_config(page_title="Quantum Circuit Simulator", layout="wide")

PRESETS = {
    "Coin flip": (1, [("H", 0)]),
    "Bell state": (2, [("H", 0), ("CNOT", 0, 1)]),
    "3 qubits agree": (3, [("H", 0), ("CNOT", 0, 1), ("CNOT", 1, 2)]),
    "H, Z, H": (1, [("H", 0), ("Z", 0), ("H", 0)]),
}

# ---- remembered values (they survive each button click) -------------------
st.session_state.setdefault("ops", [])
st.session_state.setdefault("n_qubits", 2)
st.session_state.setdefault("run_id", 0)


def load_preset(name):
    n, ops = PRESETS[name]
    st.session_state.n_qubits = n
    st.session_state.ops = list(ops)


def add_gate(op):
    st.session_state.ops.append(op)


def build(n, ops):
    c = Circuit(n)
    for name, *qs in ops:
        c.cnot(*qs) if name == "CNOT" else getattr(c, name.lower())(*qs)
    return c


@st.cache_data(show_spinner=False)
def simulate(n, ops, noise, shots, run_id):
    np.random.seed(run_id)                       # same inputs -> same picture
    c = build(n, ops)
    ideal = c.probabilities()
    counts = c.measure(shots, noise)
    error = 0.5 * sum(abs(counts.get(k, 0) / shots - ideal[k]) for k in ideal)
    return ideal, counts, error


@st.cache_data(show_spinner=False)
def noise_curve(n, ops):
    np.random.seed(0)
    c = build(n, ops)
    levels = np.linspace(0, 0.3, 13)
    return pd.DataFrame({"Noise (%)": levels * 100,
                         "Error": [c.error(p, 300) for p in levels]}).set_index("Noise (%)")


# ---- sidebar --------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    n = st.slider("Number of qubits", 1, 6, key="n_qubits")
    noise_pct = st.slider("Noise (%)", 0, 30, 0,
                          help="Chance that each qubit a gate touches gets flipped by mistake.")
    shots = st.slider("Measurements (shots)", 200, 3000, 1000, step=100)

# drop gates that point at qubits that no longer exist
st.session_state.ops = [op for op in st.session_state.ops if all(q < n for q in op[1:])]
ops = st.session_state.ops

# ---- main page ------------------------------------------------------------
st.title("Quantum Circuit Simulator")
st.caption("Built from scratch with NumPy. Place gates, run, and watch what noise does.")

st.subheader("1. Build a circuit")
st.write("**Start from an example:**")
cols = st.columns(len(PRESETS))
for col, name in zip(cols, PRESETS):
    col.button(name, on_click=load_preset, args=(name,), use_container_width=True)

st.write("**Or add gates yourself:**")
c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])
gate = c1.selectbox("Gate", ["H", "X", "Z", "CNOT"],
                    help="H = 50/50 mix, X = flip, Z = flip the sign, CNOT = flip 2nd if 1st is 1")
if gate == "CNOT":
    control = c2.selectbox("Control qubit", range(n))
    target = c3.selectbox("Target qubit", range(n), index=min(1, n - 1))
    ok = n >= 2 and control != target
    op = ("CNOT", control, target)
else:
    q = c2.selectbox("Qubit", range(n))
    ok, op = True, (gate, q)
c4.write("")
c4.write("")
c4.button("Add gate", on_click=add_gate, args=(op,), disabled=not ok, use_container_width=True)
if gate == "CNOT" and not ok:
    st.caption("CNOT needs two different qubits (so at least 2 qubits).")

b1, b2, _ = st.columns([1, 1, 4])
b1.button("Undo last", on_click=lambda: st.session_state.ops.pop() if st.session_state.ops else None,
          disabled=not ops, use_container_width=True)
b2.button("Clear", on_click=lambda: st.session_state.ops.clear(),
          disabled=not ops, use_container_width=True)

st.pyplot(draw_circuit(n, ops), use_container_width=False)

st.subheader("2. Results")
if not ops:
    st.info("Pick an example or add a gate to see results. With no gates, every qubit stays at 0.")
else:
    ideal, counts, error = simulate(n, tuple(map(tuple, ops)), noise_pct / 100, shots,
                                    st.session_state.run_id)
    left, right = st.columns([3, 1])
    df = pd.DataFrame({
        "Perfect (no noise)": ideal,
        f"Measured ({shots} shots, {noise_pct}% noise)": {k: counts.get(k, 0) / shots for k in ideal},
    })
    left.bar_chart(df, y_label="Chance of this result", x_label="Result (qubit 0 on the left)")
    right.metric("Error", f"{error:.2f}", help="0 = same as perfect, 1 = completely different")
    right.button("Run again", on_click=lambda: st.session_state.update(run_id=st.session_state.run_id + 1),
                 use_container_width=True)
    right.caption("Move the noise slider in the sidebar and watch the extra bars appear.")

    with st.expander("See how error grows with noise for this circuit"):
        st.line_chart(noise_curve(n, tuple(map(tuple, ops))), y_label="Error")

with st.expander("What am I looking at?"):
    st.markdown("""
- A **qubit** is a list of numbers that gives the chances of seeing 0 or 1.
- A **gate** changes those numbers. **H** makes a 50/50 mix, **X** flips, **Z** flips a sign, **CNOT** flips the second qubit if the first is 1.
- **Measuring** means looking: you always see one result, chosen at random using those chances.
- **Noise** means each gate can make a small mistake, so results that should never appear start to show up.
- **Limits:** this runs on your computer, so it stops at 6 qubits here (every extra qubit doubles the numbers to track). The noise model is simple random flips, not real hardware.
""")