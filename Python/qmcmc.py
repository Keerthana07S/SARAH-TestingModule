# Some of this code was  referenced from pafloxy and Dr. David Layden's research, but modified to fit the needs of this project. MIT License is attached separately.
# Moreover, many additions and modifications to the prior code were made so that up to 200 nodes can be searched using a classical computer.
# Note that the library "quMCMC" was obtained from pafloxy's Github and should be in a separate folder when running this code. 
import numpy as np
from typing import Optional, Union
from collections import Counter, defaultdict
from tqdm import tqdm
import time

from quMCMC.qumcmc.basic_utils import MCMCChain, MCMCState
from quMCMC.qumcmc.energy_models import IsingEnergyFunction
from quMCMC.qumcmc.classical_mcmc_routines import test_accept, get_random_state
from quMCMC.qumcmc.mixers import CustomMixer
from qulacs import QuantumState, QuantumCircuit

GammaType = Union[float, tuple]

def initialise_qc(n_spins: int, bitstring: str) -> QuantumCircuit:
    qc_in = QuantumCircuit(n_spins)
    for i, b in enumerate(reversed(bitstring)):
        if b == "1":
            qc_in.add_X_gate(i)
    return qc_in

def fn_qckt_problem_half(J: np.ndarray, h: np.ndarray, num_spins: int, gamma: float, alpha: float, delta_time=0.8) -> QuantumCircuit:
    qc = QuantumCircuit(num_spins)
    theta_J = 2 * -1 * (1 - gamma) * alpha * delta_time * J
    for j in range(num_spins - 1):
        for k in range(j + 1, num_spins):
            angle = -theta_J[j, k]
            if angle != 0:
                qc.add_multi_Pauli_rotation_gate([num_spins - 1 - j, num_spins - 1 - k], [3, 3], angle)
    theta_h = 2 * -1 * (1 - gamma) * alpha * delta_time * h
    for j in range(num_spins):
        angle = -theta_h[j]
        if angle != 0:
            qc.add_RZ_gate(num_spins - 1 - j, angle)
    return qc

def trotter(num_spins: int, qckt_1: QuantumCircuit, qckt_2: QuantumCircuit, num_trotter_steps: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_spins)
    for _ in range(num_trotter_steps - 1):
        qc.merge_circuit(qckt_2)
        qc.merge_circuit(qckt_1)
    qc.merge_circuit(qckt_2)
    return qc

def run_batch_qmcmc(bit_init: str, Jsub: np.ndarray, hsub: np.ndarray, n_hops: int, gamma: GammaType, temperature: float, delta_time: float) -> Counter:
    num_spins = len(hsub)
    model = IsingEnergyFunction(Jsub, hsub)
    mixer = CustomMixer(num_spins, [(i, i + 1) for i in range(num_spins - 1)])
    gammafunc = (lambda: gamma) if isinstance(gamma, (int, float)) else (lambda: np.random.uniform(*gamma))

    state = MCMCState(bit_init, accepted=True)
    chain = MCMCChain([state], name="Batch")
    energy = model.get_energy(state.bitstring)

    for _ in range(n_hops):
        gamma_val = gammafunc()
        qc = initialise_qc(num_spins, state.bitstring)
        qc.merge_circuit(trotter(
            num_spins,
            fn_qckt_problem_half(Jsub, hsub, num_spins, gamma_val, model.alpha, delta_time),
            mixer.get_mixer_circuit(gamma_val, delta_time),
            int(np.floor(np.random.randint(2, 12) / delta_time))
        ))
        qst = QuantumState(num_spins)
        qst.set_zero_state()
        qc.update_quantum_state(qst)
        s_prime = f"{qst.sampling(1)[0]:0{num_spins}b}"
        energy_prime = model.get_energy(s_prime)
        if test_accept(energy, energy_prime, temperature):
            state = MCMCState(s_prime, True)
            energy = energy_prime
        else:
            state = MCMCState(s_prime, False)
        chain.add_state(state)
    return Counter([s.bitstring for s in chain.states if s.accepted])

def make_batches(n_nodes: int, batch_size: int, overlap: int):
    return [list(range(i, min(i + batch_size, n_nodes))) for i in range(0, n_nodes, batch_size - overlap)]

def make_physics_J_h(num_nodes: int, avg_degree: int = 3, source_fraction: float = 0.05, load_fraction: float = 0.1, seed: int = 42):
    rng = np.random.default_rng(seed)
    J = np.zeros((num_nodes, num_nodes))
    for j in range(num_nodes):
        neighbors = rng.choice(num_nodes, avg_degree, replace=False)
        for k in neighbors:
            if k != j:
                val = rng.uniform(0.1, 1.0) * (1 if rng.random() < 0.7 else -1)
                J[j, k] = J[k, j] = val
    np.fill_diagonal(J, 0)
    h = np.zeros(num_nodes)
    src = rng.choice(num_nodes, int(num_nodes * source_fraction), replace=False)
    load = rng.choice([i for i in range(num_nodes) if i not in src], int(num_nodes * load_fraction), replace=False)
    h[src] = rng.uniform(0.5, 2.0, len(src))
    h[load] = -rng.uniform(0.5, 2.0, len(load))
    return J, h

def fault_localization_optimized():
    NODES = 200
    BATCH_SIZE = 12
    OVERLAP = 4
    N_HOPS = 200

    J, h = make_physics_J_h(NODES)
    batches = make_batches(NODES, BATCH_SIZE, OVERLAP)
    vote_counts, vote_totals = defaultdict(int), defaultdict(int)
    rng = np.random.default_rng(123)

    t0 = time.time()
    for batch in tqdm(batches, desc="Batches"):
        Jsub = J[np.ix_(batch, batch)]
        hsub = h[batch]
        init = "".join(rng.choice(['0', '1'], size=len(batch)))
        counts = run_batch_qmcmc(init, Jsub, hsub, N_HOPS, (0.2, 0.6), 1.0, 0.8)
        
        for bs, count in counts.items():
            for i, b in enumerate(bs):
                node = batch[i]
                vote_totals[node] += count
                vote_counts[node] += count * (b == '1')
                
    elapsed = time.time() - t0

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
