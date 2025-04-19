include("bifurcation.jl")
using HypothesisTests, Plots, StatsBase
using LinearAlgebra

# Our givens
i_s = 2.0
v_bus = 12.0

# Initial state matrix
global A = [(1)  (0) ;  
            (0)  (1)] 
global x_i = [i_s ; v_bus]

# Control input covariance matrix (normalized)
global B = [(0.07790571296205358) (-476.73291832983836) (0.06451957436481184) (-2.1030957120413913) (-2.203787730050049) (-0.023300191156435873) (0.0007169397964113035) (-0.004180565548674369) ; 
            (-0.0028702910932419654) (0.6927547150205023) (0.008879631830097259) (0.011704044977636538) (0.009279933443372732) (0.1123438976754724) (-0.003659937896493428) (0.020843190291931803)]
global B = B ./ maximum(abs.(B)) # Normalize B

# Control inputs
global u_i =[R_eq;
            L_eq;
            V_ref;
            v_bus;
            i_s;
            C;
            P;
            R]

# Measurement matrix
global H = [(1)  (0) ;  
            (0)  (1)]

# Number of iterations
global n = 100
residuals = Float64[]

# Regressors for White Test
X = []
Y = ones(100, 1)

function predicted_state(x_i::Vector{Float64}, u::Vector{Float64}, R_eq)
    global Q
    if R_eq < 10
        Q = [0.01 0; 0 0.01]
    else
        Q = [0.5 0; 0 0.5]
    end
    x_f = A * x_i + B * u + randn(2) .* diag(Q)
    return x_f
end

# Residual calculation
function residual_calculation(x_i, x_ii)
    z_f = H*x_ii
    z_i = H*x_i
    V_i = z_f - z_i
    return V_i 
end

# Run the simulation
for t in 1:n
    global i_s, v_bus = runge_kutta(i_s, v_bus, L_eq, V_ref, R_eq, C, R, P)
    x_ii = predicted_state(x_i, u_i, R_eq)
    V_i = residual_calculation(x_i, x_ii)
    push!(X, v_bus)
    push!(residuals, mean(V_i))
    global variance = var(residuals)
    global x_i = x_ii
end

print(variance)
