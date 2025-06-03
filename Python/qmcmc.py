#author: keerthana srinivasan
#date of completion: 6/3/2025
#description: this code implements a quantum-enhanced MCMC that leverages batching to localize faults across 200 nodes  

"""
some of this code was  referenced from pafloxy and Dr. David Layden's research, but modified to fit the needs of this project. MIT License is attached separately.
moreover, many additions and modifications to the prior code were made so that up to 200 nodes can be searched using a classical computer.
note that the library "quMCMC" was obtained from pafloxy's Github and should be in a separate folder when running this code. 
"""

import numpy as np #for numerical and matrix operations
from typing import Optional, Union
from collections import Counter, defaultdict
from tqdm import tqdm
import time #track run time

#components of quantum enhanced markov chains
from quMCMC.qumcmc.basic_utils import MCMCChain, MCMCState
from quMCMC.qumcmc.energy_models import IsingEnergyFunction
from quMCMC.qumcmc.classical_mcmc_routines import test_accept, get_random_state
from quMCMC.qumcmc.mixers import CustomMixer

from qulacs import QuantumState, QuantumCircuit #simulate Trotter quantum circuit

GammaType = Union[float, tuple]  #gamma can be a single value or a tuple for sampling

#create a quantum circuit with n_spins qubits in a given bitstring state. 
def initialise_qc(n_spins: int, bitstring: str) -> QuantumCircuit:
    qc_in = QuantumCircuit(n_spins)
    #set each qubit to |1⟩ if corresponding bit is '1'; else leave in |0⟩
    for i, b in enumerate(reversed(bitstring)):
        if b == "1":
            qc_in.add_X_gate(i)
    return qc_in

"""create the Hamiltonian problem evolution layer.
this layer applies interactions for ising couplings (J) and local fields (h).""" 
def fn_qckt_problem_half(J: np.ndarray, h: np.ndarray, num_spins: int, gamma: float, alpha: float, delta_time=0.8) -> QuantumCircuit:
    qc = QuantumCircuit(num_spins)
    #scale the Ising interaction term using parameters; J is symmetric (undirected interactions)
    theta_J = 2 * -1 * (1 - gamma) * alpha * delta_time * J
    for j in range(num_spins - 1):
        for k in range(j + 1, num_spins):
            angle = -theta_J[j, k]
            if angle != 0:
                qc.add_multi_Pauli_rotation_gate([num_spins - 1 - j, num_spins - 1 - k], [3, 3], angle)
    #local field term; h[j] is the external field acting on each spin
    theta_h = 2 * -1 * (1 - gamma) * alpha * delta_time * h
    for j in range(num_spins):
        angle = -theta_h[j]
        if angle != 0:
            #apply ZZ interaction for J[j,k] ≠ 0
            qc.add_RZ_gate(num_spins - 1 - j, angle)
    return qc

#create the trotter circuit
def trotter(num_spins: int, qckt_1: QuantumCircuit, qckt_2: QuantumCircuit, num_trotter_steps: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_spins)
    #repeat alternating layers (mixer/problem) for Trotter approximation
    for _ in range(num_trotter_steps - 1):
        qc.merge_circuit(qckt_2)
        qc.merge_circuit(qckt_1)
    qc.merge_circuit(qckt_2) #end with mixer layer
    return qc


"""
run a quantum-enhanced MCMC step over a subset of the problem.
bit_init: starting bitstring.
Jsub, hsub: Ising interaction and local field for the subproblem.
n_hops: number of MCMC transitions.
gamma: quantum-classical tradeoff (can be sampled or fixed).
temperature: thermal parameter for classical acceptance.
delta_time: Trotterization parameter.
"""

#using this function, we can take a subset of the full p[roblem and run that as a batch. 
def run_batch_qmcmc(bit_init: str, Jsub: np.ndarray, hsub: np.ndarray, n_hops: int, gamma: GammaType, temperature: float, delta_time: float) -> Counter:
    num_spins = len(hsub)
    model = IsingEnergyFunction(Jsub, hsub)
    mixer = CustomMixer(num_spins, [(i, i + 1) for i in range(num_spins - 1)])
    gammafunc = (lambda: gamma) if isinstance(gamma, (int, float)) else (lambda: np.random.uniform(*gamma))

    state = MCMCState(bit_init, accepted=True)
    chain = MCMCChain([state], name="Batch")
    energy = model.get_energy(state.bitstring)
    
    #initialize state from bitstring
    for _ in range(n_hops):
        gamma_val = gammafunc()
        qc = initialise_qc(num_spins, state.bitstring)
        #build problem and mixer circuit, and compose into a full trotter circuit
        qc.merge_circuit(trotter(
            num_spins,
            fn_qckt_problem_half(Jsub, hsub, num_spins, gamma_val, model.alpha, delta_time),
            mixer.get_mixer_circuit(gamma_val, delta_time),
            int(np.floor(np.random.randint(2, 12) / delta_time))
        ))
        #simulate quantum circuit and sample new bitstring
        qst = QuantumState(num_spins)
        qst.set_zero_state()
        qc.update_quantum_state(qst)
        s_prime = f"{qst.sampling(1)[0]:0{num_spins}b}"
        #calculate energy of new state and accept or reject
        energy_prime = model.get_energy(s_prime)
        if test_accept(energy, energy_prime, temperature):
            state = MCMCState(s_prime, True)
            energy = energy_prime
        else:
            state = MCMCState(s_prime, False)
        chain.add_state(state)
    #return frequency of accepted states only
    return Counter([s.bitstring for s in chain.states if s.accepted])

#split full problem into overlapping subsets (for scaling to large n_nodes)
def make_batches(n_nodes: int, batch_size: int, overlap: int):
    return [list(range(i, min(i + batch_size, n_nodes))) for i in range(0, n_nodes, batch_size - overlap)]

"""
generate random Ising model with specified average connectivity and sparse source/load biases.
can be replaced with a domain-specific model (e.g., power grids, biological networks).
"""

#create a J and h matrix. for now, it is mostly random but can be manually created for a specific system.
def make_physics_J_h(num_nodes: int, avg_degree: int = 3, source_fraction: float = 0.05, load_fraction: float = 0.1, seed: int = 42):
    rng = np.random.default_rng(seed)
    J = np.zeros((num_nodes, num_nodes))
    #construct random symmetric adjacency matrix with random couplings
    for j in range(num_nodes):
        neighbors = rng.choice(num_nodes, avg_degree, replace=False)
        for k in neighbors:
            if k != j:
                val = rng.uniform(0.1, 1.0) * (1 if rng.random() < 0.7 else -1)
                J[j, k] = J[k, j] = val
    np.fill_diagonal(J, 0)
    #assign source and load nodes with external fields
    h = np.zeros(num_nodes)
    src = rng.choice(num_nodes, int(num_nodes * source_fraction), replace=False)
    load = rng.choice([i for i in range(num_nodes) if i not in src], int(num_nodes * load_fraction), replace=False)
    h[src] = rng.uniform(0.5, 2.0, len(src))
    h[load] = -rng.uniform(0.5, 2.0, len(load))
    return J, h

"""
main fault localization pipeline.
subdivides large network, runs quantum-enhanced sampling on each batch,
and aggregates results to produce node-level fault probabilities.
"""

#actually run fault localization on each batch, and blend the results by leveraging overlaps
def fault_localization_optimized():
    NODES = 200  #number of nodes in full graph
    BATCH_SIZE = 12  #size of each batch
    OVERLAP = 4  #how much overlap between batches
    N_HOPS = 200  #number of MCMC transitions per batch

    #define problem
    J, h = make_physics_J_h(NODES)
    batches = make_batches(NODES, BATCH_SIZE, OVERLAP)
    vote_counts, vote_totals = defaultdict(int), defaultdict(int)
    rng = np.random.default_rng(123)

    t0 = time.time() #start timer
    for batch in tqdm(batches, desc="Batches"):
        Jsub = J[np.ix_(batch, batch)]
        hsub = h[batch]
        init = "".join(rng.choice(['0', '1'], size=len(batch)))

        #run qmcmc on batch
        counts = run_batch_qmcmc(init, Jsub, hsub, N_HOPS, (0.2, 0.6), 1.0, 0.8)

        #accumulate per-node votes weighted by sampled state
        for bs, count in counts.items():
            for i, b in enumerate(bs):
                node = batch[i]
                vote_totals[node] += count
                vote_counts[node] += count * (b == '1')
    #track elapsed time
    elapsed = time.time() - t0

    #compute and rank fault probabilities
    fault_probs = {n: vote_counts[n] / vote_totals[n] for n in vote_totals}
    ranked = sorted(fault_probs.items(), key=lambda x: -x[1])

    print(f"\nFinished in {elapsed:.2f} seconds.\nTop 10 fault-candidate nodes and P(fault):")
    for node, prob in ranked[:10]:
        print(f"  Node {node:3d}: {prob:.3f}")

    print("\nFull distribution of fault probabilities:")
    for node, prob in sorted(fault_probs.items()):
        print(f"Node {node:3d}: {prob:.3f}")

if __name__ == '__main__':
    fault_localization_optimized()
