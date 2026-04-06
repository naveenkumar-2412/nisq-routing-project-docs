# Problem Statement: Adaptive Qubit Routing on NISQ

## Title

Adaptive Qubit Routing for Error-Aware Compilation on NISQ Hardware

## Real-world problem

Current quantum processors expose sparse connectivity and noisy two-qubit operations. A logical quantum circuit often cannot be executed directly and must be transformed by inserting SWAP gates and remapping qubits. Poor routing decisions increase circuit depth and error probability, reducing experiment success.

This is a real compiler optimization task used in practical NISQ workloads in chemistry, optimization, and quantum machine learning.

## Objective

Build an OpenEnv reinforcement-learning environment where an agent learns routing decisions that:

1. Minimize additional depth from SWAP insertion
2. Avoid high-error edges when possible
3. Complete all required logical two-qubit interactions under a step budget
4. Maximize estimated circuit success probability

## Inputs and outputs

Inputs to the environment include:

- Hardware coupling graph and edge error rates
- Logical circuit interaction list (gate sequence)
- Initial logical-to-physical qubit mapping
- Episode-level seed for reproducibility

Outputs from the agent include:

- SWAP insertion decisions
- Gate execution scheduling decisions
- Optional terminate action

## Why RL is suitable

The problem is sequential, combinatorial, and path-dependent. Early routing choices constrain future feasibility and quality, which matches RL assumptions around delayed credit assignment and long-horizon optimization.

## Users and stakeholders

- Quantum compiler researchers
- Hardware-aware transpilation teams
- RL researchers working on constrained planning
- Benchmark maintainers evaluating LLM agent tool use

## Success criteria

A successful environment and baseline solution must satisfy:

1. OpenEnv interface compliance
2. At least three deterministic tasks with increasing difficulty
3. Per-task deterministic graders returning scores in [0.0, 1.0]
4. Meaningful dense rewards, not terminal-only rewards
5. Reproducible baseline inference execution

## Non-goals

- Full pulse-level control and calibration
- Fault-tolerant quantum compilation
- Claiming hardware-validated physical fidelity beyond modeled estimates
