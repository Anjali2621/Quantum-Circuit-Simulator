import numpy as np
from quantum import Circuit


def chances(c):
    return {k: round(float(v), 3) for k, v in c.probabilities().items() if v > 1e-9}


def test_x_flips():
    assert chances(Circuit(1).x(0)) == {"1": 1.0}


def test_h_makes_fifty_fifty():
    assert chances(Circuit(1).h(0)) == {"0": 0.5, "1": 0.5}


def test_h_twice_returns_to_zero():
    assert chances(Circuit(1).h(0).h(0)) == {"0": 1.0}


def test_h_z_h_acts_like_x():          # the minus sign in Z changes the cancelling
    assert chances(Circuit(1).h(0).z(0).h(0)) == {"1": 1.0}


def test_bell_state():
    assert chances(Circuit(2).h(0).cnot(0, 1)) == {"00": 0.5, "11": 0.5}


def test_cnot_other_direction():
    assert chances(Circuit(2).x(1).cnot(1, 0)) == {"11": 1.0}


def test_three_qubits_all_agree():
    assert chances(Circuit(3).h(0).cnot(0, 1).cnot(1, 2)) == {"000": 0.5, "111": 0.5}


def test_probabilities_add_to_one():
    c = Circuit(4).h(0).h(1).cnot(0, 2).z(3).h(3)
    assert abs(sum(c.probabilities().values()) - 1) < 1e-9


def test_zero_noise_is_perfect():
    np.random.seed(1)
    res = Circuit(2).h(0).cnot(0, 1).measure(500, noise=0)
    assert set(res) == {"00", "11"}


def test_noise_creates_wrong_results():
    np.random.seed(1)
    res = Circuit(2).h(0).cnot(0, 1).measure(1000, noise=0.2)
    assert "01" in res or "10" in res


def test_more_noise_means_more_error():
    np.random.seed(1)
    c = Circuit(2).h(0).cnot(0, 1)
    assert c.error(0.02, 2000) < c.error(0.2, 2000)