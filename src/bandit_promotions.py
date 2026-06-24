# src/bandit_promotions.py
# Enhancement 14 - Multi-Armed Bandit for Promotion Selection
# Uses Epsilon-Greedy algorithm to learn which promotions
# work best through exploration and exploitation.

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


# ── PROMOTION ARMS ────────────────────────────────────────────
PROMOTION_ARMS = {
    0: {'name': 'Free Delivery',        'true_reward': 0.28},
    1: {'name': '10% Off Produce',      'true_reward': 0.22},
    2: {'name': 'Buy 2 Get 1 Snacks',   'true_reward': 0.18},
    3: {'name': 'Organic Discovery',    'true_reward': 0.20},
    4: {'name': 'Loyalty Reward',       'true_reward': 0.15},
    5: {'name': 'Reactivation Offer',   'true_reward': 0.32},
    6: {'name': 'Dairy Bundle',         'true_reward': 0.17},
}

N_ARMS = len(PROMOTION_ARMS)


class EpsilonGreedyBandit:
    """
    Epsilon-Greedy Multi-Armed Bandit for promotion selection.

    With probability epsilon: explore (try a random promotion)
    With probability 1-epsilon: exploit (use the best known promotion)

    The bandit learns which promotions work best over time
    by observing which ones lead to actual orders.

    Parameters
    ----------
    n_arms  : number of promotion options
    epsilon : exploration rate (0.1 = 10% explore, 90% exploit)
    """

    def __init__(self, n_arms: int = N_ARMS, epsilon: float = 0.1):
        self.n_arms  = n_arms
        self.epsilon = epsilon
        self.counts  = np.zeros(n_arms)   # times each arm was pulled
        self.values  = np.zeros(n_arms)   # estimated reward per arm
        self.history = []

    def select_arm(self) -> int:
        """Select which promotion to show (epsilon-greedy policy)."""
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_arms)  # explore
        else:
            return np.argmax(self.values)           # exploit

    def update(self, arm: int, reward: float):
        """Update the estimated reward for a given arm."""
        self.counts[arm] += 1
        n = self.counts[arm]
        # Incremental mean update
        self.values[arm] += (reward - self.values[arm]) / n
        self.history.append({
            'arm':       arm,
            'reward':    reward,
            'estimated': self.values[arm],
        })

    def get_best_arm(self) -> tuple:
        """Return the current best arm and its estimated reward."""
        best = np.argmax(self.values)
        return best, self.values[best]

    def get_summary(self) -> pd.DataFrame:
        """Return a summary of all arms and their learned values."""
        rows = []
        for i in range(self.n_arms):
            rows.append({
                'arm_id':          i,
                'promotion':       PROMOTION_ARMS[i]['name'],
                'true_reward':     PROMOTION_ARMS[i]['true_reward'],
                'estimated_reward':round(self.values[i], 4),
                'times_selected':  int(self.counts[i]),
                'error':           round(
                    abs(self.values[i] -
                        PROMOTION_ARMS[i]['true_reward']), 4
                ),
            })
        return pd.DataFrame(rows).sort_values(
            'estimated_reward', ascending=False
        )


def simulate_reward(arm: int, noise: float = 0.05) -> float:
    """
    Simulate whether a promotion led to an order (reward = 1)
    or not (reward = 0).

    True reward rates come from PROMOTION_ARMS.
    Small random noise is added to simulate real-world variability.
    """
    true_rate  = PROMOTION_ARMS[arm]['true_reward']
    noisy_rate = np.clip(true_rate + np.random.normal(0, noise), 0, 1)
    return float(np.random.random() < noisy_rate)


def run_bandit_simulation(n_rounds: int = 10000,
                           epsilon: float = 0.1,
                           random_state: int = 42) -> tuple:
    """
    Run the full bandit simulation.

    Parameters
    ----------
    n_rounds     : total number of promotion assignments to simulate
    epsilon      : exploration rate
    random_state : for reproducibility

    Returns
    -------
    bandit       : trained EpsilonGreedyBandit
    results_df   : round-by-round simulation results
    regret_df    : cumulative regret over time
    """
    np.random.seed(random_state)

    bandit  = EpsilonGreedyBandit(n_arms=N_ARMS, epsilon=epsilon)
    results = []

    # Optimal arm (highest true reward)
    optimal_arm    = max(PROMOTION_ARMS,
                         key=lambda k: PROMOTION_ARMS[k]['true_reward'])
    optimal_reward = PROMOTION_ARMS[optimal_arm]['true_reward']

    cumulative_reward  = 0
    cumulative_regret  = 0

    for round_num in range(1, n_rounds + 1):
        arm    = bandit.select_arm()
        reward = simulate_reward(arm)
        bandit.update(arm, reward)

        regret              = optimal_reward - PROMOTION_ARMS[arm]['true_reward']
        cumulative_reward  += reward
        cumulative_regret  += regret

        if round_num % 500 == 0 or round_num <= 10:
            best_arm, best_val = bandit.get_best_arm()
            results.append({
                'round':              round_num,
                'arm_selected':       arm,
                'reward':             reward,
                'cumulative_reward':  cumulative_reward,
                'cumulative_regret':  cumulative_regret,
                'best_arm_so_far':    best_arm,
                'best_estimated_val': round(best_val, 4),
                'epsilon':            epsilon,
            })

    results_df = pd.DataFrame(results)

    return bandit, results_df


def compare_epsilons(n_rounds: int = 5000) -> pd.DataFrame:
    """
    Compare different epsilon values to find the optimal
    exploration rate for this promotion problem.
    """
    epsilons = [0.01, 0.05, 0.10, 0.20, 0.50]
    comparison = []

    for eps in epsilons:
        bandit, results = run_bandit_simulation(
            n_rounds=n_rounds, epsilon=eps, random_state=42
        )
        final_regret = results['cumulative_regret'].iloc[-1]
        final_reward = results['cumulative_reward'].iloc[-1]
        best_arm, _  = bandit.get_best_arm()

        comparison.append({
            'epsilon':         eps,
            'final_regret':    round(final_regret, 2),
            'final_reward':    round(final_reward, 2),
            'best_arm_found':  PROMOTION_ARMS[best_arm]['name'],
            'correct':         best_arm == 5,  # Reactivation is best
        })

    return pd.DataFrame(comparison)