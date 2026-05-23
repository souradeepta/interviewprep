# Reinforcement Learning — Learning from Rewards

How agents learn by interacting with environments.

---

## 🎮 Core Concepts

### Agent-Environment Loop

```
Agent → Action → Environment
  ↑                    ↓
  ←—— Reward, State ———
```

### Key Components

**State (s):** Agent's current situation
```
Maze: Current position
Game: Board configuration
Robot: Sensor readings
```

**Action (a):** What agent can do
```
Maze: Move up, down, left, right
Game: Move piece, attack, defend
Robot: Motor commands
```

**Reward (r):** Feedback from environment
```
Maze: -1 per step, +10 reaching goal
Game: +1 for winning, -1 for losing
Robot: +1 for stable, -100 for falling
```

**Policy (π):** Agent's strategy
```
Deterministic: a = π(s)
Stochastic: P(a|s) = π(a|s)
```

---

## 📊 Value-Based Methods

### Q-Learning

Learn value of actions:
```
Q(s,a) = Expected return for action a in state s

Update:
Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') - Q(s,a)]
                   └─────────────────────────┘
                   Temporal difference error

Key: Off-policy (learn from any action)
```

### Deep Q-Networks (DQN)

Use neural network for Q-values:
```
Input: State (pixels in Atari)
Network: Conv → Dense → Output (Q-values per action)

Experience replay: Store (s,a,r,s') and sample batches
Target network: Separate network for stability
```

---

## 🎯 Policy-Based Methods

### Policy Gradient

Directly learn policy π(a|s):
```
Objective: Maximize expected return
∇J = E[∇log π(a|s) · R(t)]

Update weights in direction of good actions
```

### Actor-Critic

Combine value and policy learning:
```
Actor: Policy π(a|s) (choose actions)
Critic: Value V(s) (evaluate state)

Update actor using critic's evaluation
```

---

## 🎓 Interview Q&A

**Q: What's the difference between on-policy and off-policy?**
A: On-policy (SARSA): Learn from actions you're taking. Off-policy (Q-learning): Learn from best actions, even if you're exploring.

**Q: Why use experience replay in DQN?**
A: Decorrelates data (sequential experiences are correlated). Batch updates are more stable. Allows reusing data.

**Q: What's the exploration-exploitation trade-off?**
A: Exploration: Try new actions. Exploitation: Use known good actions. Balance needed or agent gets stuck in local optima.

---

**Last updated:** 2026-05-22
