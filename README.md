# Go Engines Study: Baseline MCTS, ELF OpenGo and KataGo

This repository contains:

- A clean 19×19 Go rules implementation (Tromp–Taylor scoring).
- A pure CPU baseline MCTS engine (no neural network, student-laptop friendly).
- Engine adapters for:
  - ELF OpenGo (via the compiled inference module, if available).
  - KataGo (via GTP, with support for strong/weak model matchups).
- Unified engine interface and scripts to run:
  - Human vs AI.
  - Baseline vs Baseline.
  - KataGo strong vs KataGo weak.
  - KataGo vs Baseline.

The main goal is to support both **research-grade experiments on GPU** and **teaching-friendly CPU configurations**.

See `task1_training_pipeline.md` for a structured description of the training pipeline (Task 1) and the code in `scripts/` for Tasks 2 and 3.
