# Task 1 – Training Pipeline Analysis (ELF / AlphaGo Zero / KataGo)

This document summarizes the major stages of the training pipeline used in ELF OpenGo, AlphaGo Zero, and KataGo, focusing on the parts that are most relevant for teaching and for extending the course code.

## 1. Feature Encoding

- Convert raw Go board states into multi-plane tensors.
- Planes typically include:
  - Current player's stones.
  - Opponent stones.
  - Liberties, captures, ko information.
  - Historical moves (temporal context).

Key difference across systems:

- **AlphaGo Zero**: ~17 feature planes, minimal design.
- **ELF OpenGo**: ~49 planes, adds richer tactical information.
- **KataGo**: 60–80+ planes, includes ownership and score-related features for more stable learning.

## 2. Neural Network Forward Pass

The network takes the encoded feature planes and outputs:

- **Policy head**: a probability distribution over all legal moves.
- **Value head**: a scalar estimating win probability from the current position.

KataGo extends this with:

- Ownership prediction.
- Score estimation and score variance.

These extra heads help stabilize training and improve convergence.

## 3. MCTS Search Loop

For each move during self-play:

1. **Selection**  
   Descend the tree using a PUCT-style formula combining:
   - Q value (mean value of the node).
   - Prior probability from the policy head.
   - Visit statistics.

2. **Expansion**  
   When a leaf is reached, run a single NN inference to obtain:
   - Policy priors for children.
   - Value estimate for backpropagation.

3. **Evaluation / Rollout**  
   AlphaGo Zero and ELF mainly rely on the value network.  
   KataGo uses its richer heads to better normalize value estimates.

4. **Backpropagation**  
   The value estimate is backed up along the path, updating visit counts and Q values.

## 4. Self-Play Game Generation

During self-play:

- For each position:
  - Save `(state, policy_target, value_target)` tuples.
  - Optionally log SGF files for later analysis or visualization.
- Policy target is generated from MCTS visit counts.
- Value target is based on the final game result (+1 / -1).

## 5. Loss Computation

Typical components:

- Policy loss (cross-entropy between predicted policy and MCTS-based targets).
- Value loss (mean squared error between predicted value and actual outcome).
- L2 regularization on weights.

KataGo adds extra terms for:

- Ownership loss.
- Score estimation loss.
- Stabilizing regularizers.

## 6. Training & Checkpointing

- Mini-batch SGD / Adam optimization on GPUs.
- Mixed precision for efficiency.
- Periodic evaluation:
  - New candidate model plays against the current best model.
  - An ELO-style system decides whether to promote the candidate.
- Checkpointing:
  - Save best model weights.
  - Optionally prune old checkpoints.

---

This high-level description is aligned with the course code and existing ELF/KataGo documentation, and it can be used as a teaching reference for students to understand the end-to-end training loop.
