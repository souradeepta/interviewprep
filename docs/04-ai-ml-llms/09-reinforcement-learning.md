# Reinforcement Learning — Learning from Rewards

**Level:** L4-L5
**Time to read:** ~20 min

RL agents learn optimal behavior through trial-and-error interaction with environments. Core to robotics, game AI, recommendation systems, and LLM alignment (RLHF).

---

## ⚖️ RL Algorithm Trade-offs

| Algorithm | Sample Efficiency | Stability | Continuous Actions | Memory | Best For |
|-----------|------------------|-----------|-------------------|--------|---------|
| **Q-Learning** | Low | Medium | No | Low | Discrete action spaces |
| **DQN** | Medium | Medium | No | High (replay buffer) | Atari, discrete games |
| **PPO** | Medium | High | Yes | Medium | LLM fine-tuning, robotics |
| **SAC** | High | High | Yes | High | Continuous control |
| **DDPG** | High | Low | Yes | High | Robotics, physics |
| **RLHF** | Low | High | N/A | Very High | LLM alignment |

### On-Policy vs. Off-Policy

| Aspect | On-Policy (PPO, SARSA) | Off-Policy (DQN, SAC) |
|--------|------------------------|----------------------|
| Sample reuse | No (discard after update) | Yes (replay buffer) |
| Data efficiency | Low | High |
| Stability | High | Medium |
| Exploration | Built-in | Separate policy needed |

---

## 🏗️ Architecture Patterns

### Pattern 1: Agent-Environment Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                    RL Training Loop                              │
│                                                                  │
│   ┌──────────┐  action  ┌───────────────┐                       │
│   │          │ ───────► │               │                       │
│   │  Agent   │          │  Environment  │ state, reward, done   │
│   │ (Policy) │ ◄─────── │               │ ─────────────────►    │
│   └──────────┘          └───────────────┘                       │
│         │                                                        │
│         ▼                                                        │
│   Update Policy (gradient ascent on expected return)            │
└─────────────────────────────────────────────────────────────────┘

Reward signal drives learning:
  Immediate: r(s, a) at each step
  Delayed:   R = Σ γᵗ rₜ  (discounted sum of future rewards)
  γ ∈ [0,1]: discount factor (0 = myopic, 1 = farsighted)
```

### Pattern 2: PPO (Proximal Policy Optimization)

```
PPO Objective:
  L_CLIP(θ) = E[ min(r_t(θ) A_t, clip(r_t(θ), 1-ε, 1+ε) A_t) ]

Where:
  r_t(θ) = π_θ(a|s) / π_θ_old(a|s)  ← probability ratio
  A_t    = Advantage estimate (how much better than baseline)
  ε      = 0.2 (clip range — prevents too-large policy updates)

Intuition: Take gradient steps, but don't let policy change too much.
Clip prevents training instability from large updates.
```

### Pattern 3: RLHF (Reinforcement Learning from Human Feedback)

```
Phase 1: Supervised Fine-tuning (SFT)
  LLM → fine-tune on expert demonstrations
  Result: SFT model

Phase 2: Reward Model (RM) Training
  Human raters: rank model outputs (A > B)
  Train RM to predict human preference score
  RM(prompt, response) → scalar reward

Phase 3: PPO Fine-tuning
  SFT model + PPO + RM reward signal
  Maximize: E[RM(prompt, response)]
  Constraint: KL divergence from SFT model (prevent reward hacking)

KL penalty: r_total = RM(x, y) - β × KL(π_θ || π_SFT)
β controls how far from SFT we're allowed to go
```

---

## 📊 Q-Learning and DQN

```python
import random
import math
from collections import deque
from typing import Tuple, List, Optional

# ── Environment: Simple Grid World ────────────────────────────────────────────

class GridWorld:
    """4×4 grid: start at (0,0), goal at (3,3), walls at some cells."""

    ACTIONS = {0: (-1,0), 1: (1,0), 2: (0,-1), 3: (0,1)}  # up, down, left, right
    WALLS = {(1,1), (1,2), (2,1)}

    def __init__(self, size: int = 4):
        self.size = size
        self.state = (0, 0)

    def reset(self) -> Tuple[int, int]:
        self.state = (0, 0)
        return self.state

    def step(self, action: int) -> Tuple[Tuple[int,int], float, bool]:
        r, c = self.state
        dr, dc = self.ACTIONS[action]
        nr, nc = r + dr, c + dc

        # Check bounds and walls
        if 0 <= nr < self.size and 0 <= nc < self.size and (nr, nc) not in self.WALLS:
            self.state = (nr, nc)

        if self.state == (self.size-1, self.size-1):
            return self.state, 10.0, True   # Goal reached
        return self.state, -0.1, False       # Step penalty


# ── Q-Learning Agent ──────────────────────────────────────────────────────────

class QLearningAgent:
    """Tabular Q-learning for small discrete state/action spaces."""

    def __init__(
        self,
        n_states: int,
        n_actions: int,
        alpha: float = 0.1,    # Learning rate
        gamma: float = 0.95,   # Discount factor
        epsilon: float = 1.0,  # Initial exploration rate
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.995,
    ):
        self.n_actions = n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        # Q-table: state_id → [Q(s,a) for each action]
        self.Q = {}

    def _state_to_id(self, state) -> int:
        if isinstance(state, tuple):
            r, c = state
            return r * 4 + c  # Grid-specific
        return state

    def _get_q(self, state_id: int) -> List[float]:
        if state_id not in self.Q:
            self.Q[state_id] = [0.0] * self.n_actions
        return self.Q[state_id]

    def choose_action(self, state) -> int:
        """ε-greedy: explore with prob ε, exploit otherwise."""
        if random.random() < self.epsilon:
            return random.randint(0, self.n_actions - 1)
        sid = self._state_to_id(state)
        return max(range(self.n_actions), key=lambda a: self._get_q(sid)[a])

    def update(self, state, action: int, reward: float, next_state, done: bool):
        """Q-learning update: Q(s,a) ← Q(s,a) + α[r + γ max_a' Q(s',a') - Q(s,a)]"""
        sid = self._state_to_id(state)
        next_sid = self._state_to_id(next_state)

        current_q = self._get_q(sid)[action]
        if done:
            target = reward
        else:
            target = reward + self.gamma * max(self._get_q(next_sid))

        td_error = target - current_q
        self._get_q(sid)[action] += self.alpha * td_error

        # Decay exploration
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def train(self, env: GridWorld, episodes: int = 500) -> List[float]:
        rewards_history = []
        for ep in range(episodes):
            state = env.reset()
            total_reward = 0
            for _ in range(100):  # max steps per episode
                action = self.choose_action(state)
                next_state, reward, done = env.step(action)
                self.update(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                if done:
                    break
            rewards_history.append(total_reward)
        return rewards_history


# Demo
env = GridWorld()
agent = QLearningAgent(n_states=16, n_actions=4)
history = agent.train(env, episodes=300)

# Show learning progress
early = sum(history[:50]) / 50
late  = sum(history[-50:]) / 50
print(f"Q-Learning results:")
print(f"  Early episodes (avg reward): {early:.2f}")
print(f"  Late episodes (avg reward):  {late:.2f}")
print(f"  Improvement: {late - early:+.2f}")
print(f"  Q-table entries: {len(agent.Q)}")
```

---

## 🤖 PPO Sketch (Policy Gradient)

```python
import math

class PPOBuffer:
    """Collects trajectories for PPO update."""

    def __init__(self, gamma: float = 0.99, lam: float = 0.95):
        self.gamma = gamma
        self.lam = lam
        self.states, self.actions, self.rewards = [], [], []
        self.values, self.log_probs, self.dones = [], [], []

    def store(self, state, action, reward, value, log_prob, done):
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
        self.dones.append(done)

    def compute_advantages(self) -> List[float]:
        """GAE (Generalized Advantage Estimation)."""
        advantages = []
        gae = 0.0
        for t in reversed(range(len(self.rewards))):
            next_value = 0 if self.dones[t] else (self.values[t+1] if t+1 < len(self.values) else 0)
            delta = self.rewards[t] + self.gamma * next_value - self.values[t]
            gae = delta + self.gamma * self.lam * (0 if self.dones[t] else gae)
            advantages.insert(0, gae)
        return advantages

    def clear(self):
        self.__init__(self.gamma, self.lam)


def ppo_clip_loss(
    log_prob_new: float,
    log_prob_old: float,
    advantage: float,
    epsilon: float = 0.2,
) -> float:
    """PPO clipped surrogate objective (single sample)."""
    ratio = math.exp(log_prob_new - log_prob_old)  # π_new / π_old
    unclipped = ratio * advantage
    clipped = max(min(ratio, 1 + epsilon), 1 - epsilon) * advantage
    return -min(unclipped, clipped)   # Negative because we minimize


# Demonstrate clip behavior
print("\nPPO Clip Loss Examples:")
for ratio in [0.8, 1.0, 1.2, 1.5, 2.0]:
    log_ratio = math.log(ratio)
    advantage = 1.0  # Positive advantage
    loss = ppo_clip_loss(log_ratio, 0.0, advantage)
    print(f"  ratio={ratio:.1f}, loss={loss:.3f}")
```

---

## ❓ Interview Q&A

**Q1: What is the exploration-exploitation trade-off in RL?**

A: Agent must balance:
- **Exploration**: Try unknown actions to discover better strategies (necessary to escape local optima)
- **Exploitation**: Use currently best-known action (maximizes short-term reward)

ε-greedy: with prob ε pick random action, else pick best known. Anneal ε from 1.0 → 0.01 over training. UCB (Upper Confidence Bound) is mathematically principled: `Q(s,a) + c√(log t / N(s,a))` — favors under-explored actions.

**Q2: Why does RLHF work for aligning LLMs?**

A: LLMs trained on next-token prediction learn to be fluent but not necessarily helpful or safe. RLHF adds a human preference signal:
1. Reward model learns from human comparisons (A > B)
2. PPO fine-tunes the LLM to maximize reward model score
3. KL penalty `β KL(π || π_SFT)` prevents drifting too far from the original SFT model (reward hacking)

Result: Model learns to produce outputs humans actually prefer, not just high-probability next tokens.

**Q3: What's the difference between model-based and model-free RL?**

A: Model-free (DQN, PPO): Agent learns directly from environment interactions. No explicit world model. Simpler but sample-inefficient.

Model-based (AlphaZero, Dreamer): Agent learns an internal world model (predicts next state, reward). Can plan ahead using the model (Monte Carlo Tree Search). Sample-efficient but model errors compound.

**Q4: How does PPO differ from vanilla policy gradient?**

A: Vanilla PG updates in direction of `∇log π(a|s) × R(t)` — no constraint on update size. Large gradients cause catastrophic policy collapse.

PPO clips the probability ratio to `[1-ε, 1+ε]`. This prevents the new policy from being too different from the old one, stabilizing training. PPO also uses multiple mini-batch gradient steps per collected trajectory (vanilla PG discards after one step).

**Q5: How would you use RL for recommendation system optimization?**

A: Model as MDP: state = user history/context, action = item to recommend, reward = click/purchase/dwell-time.

Challenges:
1. **Exploration**: Must recommend suboptimal items sometimes to discover user preferences
2. **Offline evaluation**: Can't A/B test every policy; use off-policy evaluation (IPS estimator)
3. **Delayed rewards**: Purchase may happen hours after recommendation
4. **Sparse rewards**: Most recommendations don't lead to purchase

In practice: Use Bandit algorithms (Thompson Sampling, LinUCB) for simpler cases; full RL (PPO + replay) for long-horizon user journey optimization.

---

## 🧪 Practical Exercises

### Exercise 1: Multi-Armed Bandit (Easy)

**Problem:** N slot machines with unknown payout rates. Maximize total reward.

```python
import random
import math

class EpsilonGreedyBandit:
    def __init__(self, n_arms: int, epsilon: float = 0.1):
        self.n_arms = n_arms
        self.epsilon = epsilon
        self.counts = [0] * n_arms
        self.values = [0.0] * n_arms

    def choose(self) -> int:
        if random.random() < self.epsilon:
            return random.randint(0, self.n_arms - 1)
        return max(range(self.n_arms), key=lambda a: self.values[a])

    def update(self, arm: int, reward: float):
        self.counts[arm] += 1
        n = self.counts[arm]
        self.values[arm] += (reward - self.values[arm]) / n  # Running average


class UCBBandit:
    def __init__(self, n_arms: int, c: float = 2.0):
        self.n_arms = n_arms
        self.c = c
        self.counts = [0] * n_arms
        self.values = [0.0] * n_arms
        self.t = 0

    def choose(self) -> int:
        self.t += 1
        for a in range(self.n_arms):
            if self.counts[a] == 0:
                return a  # Try each arm at least once

        ucb = [
            self.values[a] + self.c * math.sqrt(math.log(self.t) / self.counts[a])
            for a in range(self.n_arms)
        ]
        return max(range(self.n_arms), key=lambda a: ucb[a])

    def update(self, arm: int, reward: float):
        self.counts[arm] += 1
        self.values[arm] += (reward - self.values[arm]) / self.counts[arm]


# True payout rates (unknown to agents)
true_rates = [0.1, 0.3, 0.5, 0.7, 0.9]

def simulate(agent, rounds: int = 1000) -> float:
    total = 0.0
    for _ in range(rounds):
        arm = agent.choose()
        reward = float(random.random() < true_rates[arm])
        agent.update(arm, reward)
        total += reward
    return total

eps_reward = simulate(EpsilonGreedyBandit(5, epsilon=0.1))
ucb_reward = simulate(UCBBandit(5, c=2.0))
optimal = 1000 * 0.9  # Always pick best arm

print(f"ε-greedy reward: {eps_reward:.0f} / {optimal:.0f} ({eps_reward/optimal*100:.1f}%)")
print(f"UCB reward:      {ucb_reward:.0f} / {optimal:.0f} ({ucb_reward/optimal*100:.1f}%)")
```

---

**Last updated:** 2026-05-22
