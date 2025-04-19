import numpy as np
import pandas as pd
from bifurcation import f, g, runge_kutta, fault_jacobian

L_eq = 5
R_eq = 5
V_ref = 12
v_bus = 12
i_s = 2
C = 238
P = 5.8
R = 106
delta_t = 1.0
stability = True

def compute_r_eq():
    r_eq = np.arange(0.1, 10.1, 0.1)
    l_eq = 5
    v_ref = 12
    v_bus = 12
    i_s = 2
    C = 238
    P = 5.8
    R = 106

    derivative_voltage, derivative_current, req_values = [], [], []

    for r in r_eq:
        i_s, v_bus = runge_kutta(i_s, v_bus, l_eq, v_ref, r, C, R, P)
        dvbus = g(i_s, v_bus, C, R, P)
        dis = f(i_s, v_bus, l_eq, v_ref, r)
        derivative_voltage.append(dvbus)
        derivative_current.append(dis)
        req_values.append(r)

    df = pd.DataFrame({"v_prime": derivative_voltage, "i_prime": derivative_current, "req": req_values})
    print(df)
    print("Covariance btwn vbus and req:", df["v_prime"].cov(df["req"]))
    print("Covariance btwn is and req:", df["i_prime"].cov(df["req"]))


def compute_l_eq():
    l_eq = np.arange(1, 10.1, 0.1)
    r_eq, v_ref, v_bus, i_s = 5, 12, 12, 2

    derivative_voltage, derivative_current, leq_values = [], [], []

    for l in l_eq:
        i_s, v_bus = runge_kutta(i_s, v_bus, l, v_ref, r_eq, C, R, P)
        dvbus = g(i_s, v_bus, C, R, P)
        dis = f(i_s, v_bus, l, v_ref, r_eq)
        derivative_voltage.append(dvbus)
        derivative_current.append(dis)
        leq_values.append(l)

    df = pd.DataFrame({"v_prime": derivative_voltage, "i_prime": derivative_current, "leq": leq_values})
    print(df)
    print("Covariance btwn vbus and leq:", df["v_prime"].cov(df["leq"]))
    print("Covariance btwn is and leq:", df["i_prime"].cov(df["leq"]))


def compute_v_ref():
    v_ref_vals = np.arange(1, 12.1, 0.1)
    r_eq, l_eq, v_bus, i_s = 5, 5, 12, 2

    derivative_voltage, derivative_current, vref_values = [], [], []

    for v in v_ref_vals:
        i_s, v_bus = runge_kutta(i_s, v_bus, l_eq, v, r_eq, C, R, P)
        dvbus = g(i_s, v_bus, C, R, P)
        dis = f(i_s, v_bus, l_eq, v, r_eq)
        derivative_voltage.append(dvbus)
        derivative_current.append(dis)
        vref_values.append(v)

    df = pd.DataFrame({"v_prime": derivative_voltage, "i_prime": derivative_current, "vref": vref_values})
    print(df)
    print("Covariance btwn vbus and vref:", df["v_prime"].cov(df["vref"]))
    print("Covariance btwn is and vref:", df["i_prime"].cov(df["vref"]))


def compute_bus_voltage():
    v_bus_vals = np.arange(1, 12.1, 0.1)
    r_eq, l_eq, v_ref, i_s = 5, 5, 12, 2

    derivative_voltage, derivative_current, vbus_values = [], [], []

    for v in v_bus_vals:
        i_s, _v = runge_kutta(i_s, v, l_eq, v_ref, r_eq, C, R, P)
        dvbus = g(i_s, v, C, R, P)
        dis = f(i_s, v, l_eq, v_ref, r_eq)
        derivative_voltage.append(dvbus)
        derivative_current.append(dis)
        vbus_values.append(v)

    df = pd.DataFrame({"v_prime": derivative_voltage, "i_prime": derivative_current, "busv": vbus_values})
    print(df)
    print("Covariance btwn vbus and busv:", df["v_prime"].cov(df["busv"]))
    print("Covariance btwn is and busv:", df["i_prime"].cov(df["busv"]))


def compute_current():
    i_s_vals = np.arange(0, 5.1, 0.1)
    r_eq, l_eq, v_ref, v_bus = 5, 5, 12, 12

    derivative_voltage, derivative_current, is_values = [], [], []

    for i in i_s_vals:
        _i, v_bus = runge_kutta(i, v_bus, l_eq, v_ref, r_eq, C, R, P)
        dvbus = g(i, v_bus, C, R, P)
        dis = f(i, v_bus, l_eq, v_ref, r_eq)
        derivative_voltage.append(dvbus)
        derivative_current.append(dis)
        is_values.append(i)

    df = pd.DataFrame({"v_prime": derivative_voltage, "i_prime": derivative_current, "curr": is_values})
    print(df)
    print("Covariance btwn vbus and curr:", df["v_prime"].cov(df["curr"]))
    print("Covariance btwn is and curr:", df["i_prime"].cov(df["curr"]))


def compute_capacitance():
    c_vals = np.arange(1, 1000.1, 0.1)
    i_s, r_eq, l_eq, v_ref, v_bus = 2, 5, 5, 12, 12

    derivative_voltage, derivative_current, c_values = [], [], []

    for c in c_vals:
        i_s, v_bus = runge_kutta(i_s, v_bus, l_eq, v_ref, r_eq, c, R, P)
        dvbus = g(i_s, v_bus, c, R, P)
        dis = f(i_s, v_bus, l_eq, v_ref, r_eq)
        derivative_voltage.append(dvbus)
        derivative_current.append(dis)
        c_values.append(c)

    df = pd.DataFrame({"v_prime": derivative_voltage, "i_prime": derivative_current, "cap": c_values})
    print(df)
    print("Covariance btwn vbus and cap:", df["v_prime"].cov(df["cap"]))
    print("Covariance btwn is and cap:", df["i_prime"].cov(df["cap"]))


def compute_power():
    p_vals = np.arange(1, 10.1, 0.1)
    i_s, r_eq, l_eq, v_ref, v_bus = 2, 5, 5, 12, 12

    derivative_voltage, derivative_current, p_values = [], [], []

    for p in p_vals:
        i_s, v_bus = runge_kutta(i_s, v_bus, l_eq, v_ref, r_eq, C, R, p)
        dvbus = g(i_s, v_bus, C, R, p)
        dis = f(i_s, v_bus, l_eq, v_ref, r_eq)
        derivative_voltage.append(dvbus)
        derivative_current.append(dis)
        p_values.append(p)

    df = pd.DataFrame({"v_prime": derivative_voltage, "i_prime": derivative_current, "pow": p_values})
    print(df)
    print("Covariance btwn vbus and pow:", df["v_prime"].cov(df["pow"]))
    print("Covariance btwn is and pow:", df["i_prime"].cov(df["pow"]))


def compute_resistance():
    r_vals = np.arange(10, 200.1, 0.1)
    i_s, r_eq, l_eq, v_ref, v_bus = 2, 5, 5, 12, 12

    derivative_voltage, derivative_current, r_values = [], [], []

    for r in r_vals:
        i_s, v_bus = runge_kutta(i_s, v_bus, l_eq, v_ref, r_eq, C, r, P)
        dvbus = g(i_s, v_bus, C, r, P)
        dis = f(i_s, v_bus, l_eq, v_ref, r_eq)
        derivative_voltage.append(dvbus)
        derivative_current.append(dis)
        r_values.append(r)

    df = pd.DataFrame({"v_prime": derivative_voltage, "i_prime": derivative_current, "res": r_values})
    print(df)
    print("Covariance btwn vbus and res:", df["v_prime"].cov(df["res"]))
    print("Covariance btwn is and res:", df["i_prime"].cov(df["res"]))


compute_r_eq()
compute_l_eq()
compute_v_ref()
compute_bus_voltage()
compute_current()
compute_capacitance()
compute_power()
compute_resistance()
