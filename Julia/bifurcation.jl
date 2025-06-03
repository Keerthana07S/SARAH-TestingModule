#author: keerthana srinivasan 
#date of completion: 04/18/2025
#description: using the bifurcation method, we can detect system instability on our electrical power subsystems through leveraging the determinant and trace of a certain jacobian

using LinearAlgebra #for matrix and numerical operations 

#givens 
L_eq = 5 #quivalent inductance 
R_eq = 5 #equivalent resistance 
V_ref = 12 #reference voltage 
v_bus = 12 #bus voltage 
i_s = 2 #bus current 
C = 238 #capacitance 
P = 5.8 #power 
R = 106 #resistance 
delta_t = 1.0 #change in time 

#function f() finds the change in bus current over time.
function f(i_s, v_bus, L_eq, V_ref, R_eq)
    return di_ds = (1/L_eq)*(V_ref - v_bus - (R_eq*i_s))
end

#function g() finds the change in bus voltage over time 
function g(i_s, v_bus, C, R, P)
    return dvbus_ds = (1/C)*(i_s-(v_bus/R)-(P/v_bus))
end

#the runge kutta function finds the bus current and voltage over various time steps through integration over time steps. 
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

#you can use a jacobian to find system instability. you can do this through finding the determinant and trace of the jacobian.
function fault_jacobian(v_bus, L_eq, R_eq, C, R, P)
    J = [(-R_eq/L_eq)  (-1/L_eq); (1/C)  (1/C) * ((P/(v_bus)^2) - (1/R))]
    
    println("Jacobian Matrix: ", J)
    println(size(J))
    
    det_J = det(J)
    trace_J = tr(J)
    println("Trace: ", trace_J)
    println("Determinant: ", det_J)

    #conditions for determinant and trace of the jacobian
    if det_J > 0 && trace_J < 0
        stability = true
    end
        
    if det_J < 0
        stability = false
    end

    println("System Stability: ", stability)
end

#get your results!
runge_kutta(i_s, v_bus, L_eq, V_ref, R_eq, C, R, P)
fault_jacobian(v_bus, L_eq, R_eq, C, R, P)
