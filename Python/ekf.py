import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import normaltest
from bifurcation import f, g, runge_kutta, fault_jacobian

i_s = 2.0
v_bus = 12.0

A = np.array([
    [1.0, 0.0],
    [0.0, 1.0]
])

x_i = np.array([i_s, v_bus])

B = np.array([
    [0.07790571296205358, -476.73291832983836, 0.06451957436481184, -2.1030957120413913,
     -2.203787730050049, -0.023300191156435873, 0.0007169397964113035, -0.004180565548674369],
    [-0.0028702910932419654, 0.6927547150205023, 0.008879631830097259, 0.011704044977636538,
     0.009279933443372732, 0.1123438976754724, -0.003659937896493428, 0.020843190291931803]
])

B = B / np.max(np.abs(B)) 

u_i = np.array([
    45,   #R_eq
    5,    #L_eq
    12,   #V_ref
    v_bus,
    i_s,
    238,  #C
    5.8,  #P
    106   #R
])


H = np.array([
    [1.0, 0.0],
    [0.0, 1.0]
])

n = 100
residuals = []
X = []
Y = np.ones((100, 1))

def f(i_s, v_bus, L_eq, V_ref, R_eq):
    return (1 / L_eq) * (V_ref - v_bus - (R_eq * i_s))

def g(i_s, v_bus, C, R, P):
    return (1 / C) * (i_s - (v_bus / R) - (P / v_bus))

def runge_kutta(i_s, v_bus, L_eq, V_ref, R_eq, C, R, P, delta_t=1.0):
    ki_is = f(i_s, v_bus, L_eq, V_ref, R_eq)
    ki_vs = g(i_s, v_bus, C, R, P)

    kii_is = f(i_s + (delta_t / 2) * ki_is, v_bus + (delta_t / 2) * ki_vs, L_eq, V_ref, R_eq)
    kii_vs = g(i_s + (delta_t / 2) * ki_is, v_bus + (delta_t / 2) * ki_vs, C, R, P)

    kiii_is = f(i_s + (delta_t / 2) * kii_is, v_bus + (delta_t / 2) * kii_vs, L_eq, V_ref, R_eq)
    kiii_vs = g(i_s + (delta_t / 2) * kii_is, v_bus + (delta_t / 2) * kii_vs, C, R, P)

    kiv_is = f(i_s + delta_t * kiii_is, v_bus + delta_t * kiii_vs, L_eq, V_ref, R_eq)
    kiv_vs = g(i_s + delta_t * kiii_is, v_bus + delta_t * kiii_vs, C, R, P)

    i_s += (delta_t / 6) * (ki_is + 2 * kii_is + 2 * kiii_is + kiv_is)
    v_bus += (delta_t / 6) * (ki_vs + 2 * kii_vs + 2 * kiii_vs + kiv_vs)

    return i_s, v_bus

def predicted_state(x_i, u, R_eq):
    if R_eq < 10:
        Q = np.diag([0.01, 0.01])
    else:
        Q = np.diag([0.5, 0.5])
    noise = np.random.randn(2) * np.diag(Q)
    x_f = A @ x_i + B @ u + noise
    return x_f

def residual_calculation(x_i, x_ii):
    z_f = H @ x_ii
    z_i = H @ x_i
    return z_f - z_i

for t in range(n):
    i_s, v_bus = runge_kutta(i_s, v_bus, u_i[1], u_i[2], u_i[0], u_i[5], u_i[7], u_i[6])
    x_ii = predicted_state(x_i, u_i, u_i[0])
    V_i = residual_calculation(x_i, x_ii)
    X.append(v_bus)
    residuals.append(np.mean(V_i))
    x_i = x_ii

variance = np.var(residuals)
print("Residual variance:", variance)
