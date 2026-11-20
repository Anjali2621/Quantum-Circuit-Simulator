from streamlit.testing.v1 import AppTest


def test_app_loads_and_preset_works():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    assert not at.exception
    next(b for b in at.button if b.label == "Bell state").click()
    at.run()
    assert not at.exception
    assert at.session_state.ops == [("H", 0), ("CNOT", 0, 1)]
    assert at.session_state.n_qubits == 2


def test_add_gate_and_noise():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    next(b for b in at.button if b.label == "Add gate").click()
    at.run()
    assert at.session_state.ops == [("H", 0)]
    at.sidebar.slider[1].set_value(15)
    at.run()
    assert not at.exception