"""
MultiAgent race

All agents are RandomAgent
The simulation runs on the "black_forest" track with 7 karts.
"""

import sys, os
import numpy as np

# Append the "src" folder to sys.path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "src")))

from customAgents.RandomAgent import RandomAgent
from pystk2_gymnasium.envs import STKRaceMultiEnv, AgentSpec

# Make AgentSpec hashable.
def agent_spec_hash(self):
    return hash((self.rank_start, self.use_ai, self.name, self.camera_mode))
AgentSpec.__hash__ = agent_spec_hash

# Create agents specifications.
agents_specs = [
    AgentSpec(name="Random1", rank_start=0, use_ai=False),
    AgentSpec(name="Random2", rank_start=1, use_ai=False),
    AgentSpec(name="Random3", rank_start=2, use_ai=False),
    AgentSpec(name="Random4", rank_start=3, use_ai=False),
    AgentSpec(name="Random5", rank_start=4, use_ai=False),
    AgentSpec(name="Random6", rank_start=5, use_ai=False),
    AgentSpec(name="Random7", rank_start=6, use_ai=False),
]

# Create the multi-agent environment for N karts.
env = STKRaceMultiEnv(agents=agents_specs, track="xr591", render_mode="human", num_kart=7)

# Instantiate the agents.

agent1 = RandomAgent(env, path_lookahead=3)
agent2 = RandomAgent(env, path_lookahead=3)
agent3 = RandomAgent(env, path_lookahead=3)
agent4 = RandomAgent(env, path_lookahead=3)
agent5 = RandomAgent(env, path_lookahead=3)
agent6 = RandomAgent(env, path_lookahead=3)
agent7 = RandomAgent(env, path_lookahead=3)

def main():
    obs, _ = env.reset()
    done = False
    while not done:
        actions = {}
        actions["0"] = agent1.choose_action(obs["0"])
        actions["1"] = agent2.choose_action(obs["1"])
        actions["2"] = agent3.choose_action(obs["2"])
        actions["3"] = agent4.choose_action(obs["3"])
        actions["4"] = agent5.choose_action(obs["4"])
        actions["5"] = agent6.choose_action(obs["5"])
        actions["6"] = agent7.choose_action(obs["6"])
        obs, reward, done, truncated, info = env.step(actions)
        if done or truncated:
            break
    env.close()

if __name__ == "__main__":
    main()
