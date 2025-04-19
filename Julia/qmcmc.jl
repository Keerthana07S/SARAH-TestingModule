using Pkg
using Statistics
using QSWalk
using LightGraphs
using LinearAlgebra
using Random
using Plots  

dim = 151 
midpoint = ceil(Int, dim / 2) 
w = 0.5 
timepoint = 100.0 

adjacency = adjacency_matrix(PathGraph(dim))

function energy(s::Vector{Int}, J::Matrix{Float64}, h::Vector{Float64})
    return -dot(s, J * s) - dot(h, s)  
end

s = rand([-1, 1], dim) 

J = Matrix(adjacency) .* (rand(dim, dim) .- 0.5)  
h = zeros(dim)  

function update_fault_params!(J::Matrix{Float64}, h::Vector{Float64}, V::Vector{Float64}, I::Vector{Float64}, V_threshold::Float64, I_threshold::Float64)
    mean_I = mean(I)
    for j in 1:dim
        if V[j] < V_threshold  
            h[j] -= 0.5
        end
        if abs(I[j] - mean_I) > I_threshold 
            h[j] -= 0.3
        end
        for k in neighbors(PathGraph(dim), j)
            if abs(V[j] - V[k]) > V_threshold / 2 
                J[j, k] *= 0.7
            end
        end
    end
end

function boltzmann_sample(J::Matrix{Float64}, h::Vector{Float64}, T::Float64, samples::Int=100)
    sampled_states = [rand([-1, 1], dim) for _ in 1:samples] 
    energies = [energy(s, J, h) for s in sampled_states]
    probs = exp.(-energies ./ T)  
    probs ./= sum(probs)  

    best_state = sampled_states[argmin(energies)]
    return best_state
end

function qmcmc_step(s::Vector{Int}, J::Matrix{Float64}, h::Vector{Float64}, T::Float64)
    return boltzmann_sample(J, h, T, 100) 
end

function evolve_qmcmc(s::Vector{Int}, J::Matrix{Float64}, h::Vector{Float64}, V::Vector{Float64}, I::Vector{Float64}, V_threshold::Float64, I_threshold::Float64, T::Float64, steps::Int)
    fault_counter = zeros(dim)  

    for _ in 1:steps
        update_fault_params!(J, h, V, I, V_threshold, I_threshold)  
        s = qmcmc_step(s, J, h, T)  
        
        fault_counter .+= (s .== -1)
    end

    fault_prob = fault_counter ./ steps
    return s, fault_prob
end

V = rand(dim) * 50 
I = rand(dim) * 5   

V_threshold = 20.0  
I_threshold = 1.0  

final_state, fault_prob = evolve_qmcmc(s, J, h, V, I, V_threshold, I_threshold, 0.1, 1000)

faulty_nodes = findall(x -> x == -1, final_state)
println("Faulty nodes identified: ", faulty_nodes)

plot(1:dim, fault_prob, lw=2, label="Fault Probability", color=:blue)
scatter!(1:dim, fault_prob, marker=:circle, color=:red, label="Nodes")
xlabel!("Node Index")
ylabel!("Fault Probability")
title!("Fault Probability Wave")
savefig("fault_probability_wave3.svg")
