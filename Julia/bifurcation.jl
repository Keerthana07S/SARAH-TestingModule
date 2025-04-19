using LinearAlgebra

L_eq = 5
R_eq = 5
V_ref = 12
v_bus = 12
i_s = 2
C = 238
P = 5.8
R = 106
delta_t = 1.0

function f(i_s, v_bus, L_eq, V_ref, R_eq)
    return di_ds = (1/L_eq)*(V_ref - v_bus - (R_eq*i_s))
end

function g(i_s, v_bus, C, R, P)
    return dvbus_ds = (1/C)*(i_s-(v_bus/R)-(P/v_bus))
end

function runge_kutta(i_s, v_bus, L_eq, V_ref, R_eq, C, R, P)
    ki_is = f(i_s, v_bus,L_eq, V_ref, R_eq)
    ki_vs = g(i_s, v_bus, C, R, P)
    kii_is = f(i_s+((delta_t/2)*ki_is), v_bus+((delta_t/2)*ki_vs), L_eq, V_ref, R_eq)
    kii_vs = g(i_s+((delta_t/2)*ki_is), v_bus+((delta_t/2)*ki_vs),C, R, P)
    kiii_is = f(i_s+((delta_t/2)*kii_is), v_bus+((delta_t/2)*kii_vs), L_eq, V_ref, R_eq)
    kiii_vs = g(i_s+((delta_t/2)*kii_is), v_bus+((delta_t/2)*kii_vs), C, R, P)
    kiv_is = f(i_s+((delta_t)*kiii_is), v_bus+((delta_t)*kiii_vs), L_eq, V_ref, R_eq)
    kiv_vs = g(i_s+((delta_t)*kiii_is), v_bus+((delta_t)*kiii_vs), C, R, P)

    global i_s = i_s + (delta_t/6)*(ki_is + (2*kii_is) + (2*kiii_is) + kiv_is)
    global v_bus = v_bus + (delta_t/6)*(ki_vs + (2*kii_vs) + (2*kiii_vs) + kiv_vs)

    return i_s, v_bus
end

function fault_jacobian(v_bus, L_eq, R_eq, C, R, P)
    J = [(-R_eq/L_eq)  (-1/L_eq); (1/C)  (1/C) * ((P/(v_bus)^2) - (1/R))]
    
    println("Jacobian Matrix: ", J)
    println(size(J))
    
    det_J = det(J)
    trace_J = tr(J)
    println("Trace: ", trace_J)
    println("Determinant: ", det_J)

    if det_J > 0 && trace_J < 0
        stability = true
    end
        
    if det_J < 0
        stability = false
    end

    println("System Stability: ", stability)
end

runge_kutta(i_s, v_bus, L_eq, V_ref, R_eq, C, R, P)
fault_jacobian(v_bus, L_eq, R_eq, C, R, P)
