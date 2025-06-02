#author: keerthana srinivasan
#date of completion: 6/2/2025
#description: this program uses the bifurcation method to detect instability on an electrical power system. 


import numpy as np #matrix and numerical operations

#note: the following givens can change depending on the electrical power subsystem
L_eq = 5 #equivalent inductance
R_eq = 45 #equivalent resistance
V_ref = 12 #reference voltage
v_bus = 12.0 #bus voltage
i_s = 2.0 #bus current
C = 238 #capacitance
P = 5.8 #power
R = 106 #overall resistance
delta_t = 1.0 #change in time

#change in bus current over time (derivative)
def f(i_s, v_bus, L_eq, V_ref, R_eq):
    return (1 / L_eq) * (V_ref - v_bus - (R_eq * i_s))

#change in bus voltage over time (derivative)
def g(i_s, v_bus, C, R, P):
    return (1 / C) * (i_s - (v_bus / R) - (P / v_bus))

#runge kutta for numerical integration over time steps. 
def runge_kutta(i_s, v_bus, L_eq, V_ref, R_eq, C, R, P):
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

#using the bifurcation method for detecting if instability in electrical power subsystem is present
def fault_jacobian(v_bus, L_eq, R_eq, C, R, P):
    J = np.array([
        [(-R_eq / L_eq), (-1 / L_eq)],
        [(1 / C), (1 / C) * ((P / (v_bus ** 2)) - (1 / R))]
    ])
    
    print("Jacobian Matrix:\n", J)
    print("Size:", J.shape)
    
    det_J = np.linalg.det(J)
    trace_J = np.trace(J)
    print("Trace:", trace_J)
    print("Determinant:", det_J)
    
    if det_J > 0 and trace_J < 0:
        stability = True
    elif det_J < 0:
        stability = False
    else:
        stability = None  
    
    print("System Stability:", stability)

#bus current and voltage (from runge kutta)
i_s, v_bus = runge_kutta(i_s, v_bus, L_eq, V_ref, R_eq, C, R, P)
#stability status
fault_jacobian(v_bus, L_eq, R_eq, C, R, P)
