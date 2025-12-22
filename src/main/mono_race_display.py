"""
MultiAgent race

All initial agents are RandomAgent
The simulation runs on the "black_forest" track with 7 karts.
"""

import sys, os
import numpy as np

MAX_TEAMS = 7

# Append the "src" folder to sys.path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "src")))

from agents.team1.agent1 import Agent1
from agents.team2.agent2 import Agent2
from agents.team3.agent3 import Agent3
from agents.team4.agent4 import Agent4
from agents.team5.agent5 import Agent5
from agents.team6.agent6 import Agent6
from agents.team7.agent7 import Agent7
from pystk2_gymnasium.envs import STKRaceMultiEnv, AgentSpec

default_action = {
            "acceleration": 0.0,
            "steer": 0.0,
            "brake": False, # bool(random.getrandbits(1)),
            "drift": False, # bool(random.getrandbits(1)),
            "nitro": False, # bool(random.getrandbits(1)),
            "rescue":False, # bool(random.getrandbits(1)),
            "fire": False, # bool(random.getrandbits(1)),
        }

# Make AgentSpec hashable.
def agent_spec_hash(self):
    return hash((self.rank_start, self.use_ai, self.name, self.camera_mode))
AgentSpec.__hash__ = agent_spec_hash

# Create agents specifications.
agents_specs = [
    AgentSpec(name=f"Team{i+1}", rank_start=i, use_ai=False) for i in range(MAX_TEAMS)
]

# Create the multi-agent environment for N karts.
env = STKRaceMultiEnv(agents=agents_specs, track="xr591", render_mode="human", num_kart=7)

# Instantiate the agents.

agents = []
names = []

agents.append(Agent1(env, path_lookahead=3))
agents.append(Agent2(env, path_lookahead=3))
agents.append(Agent3(env, path_lookahead=3))
agents.append(Agent4(env, path_lookahead=3))
agents.append(Agent5(env, path_lookahead=3))
agents.append(Agent6(env, path_lookahead=3))
agents.append(Agent7(env, path_lookahead=3))
np.random.shuffle(agents)

for i in range(MAX_TEAMS):
    names.append(agents[i].name)

def main():
    obs, _ = env.reset()
    done = False
    steps = 0
    positions = []
    while not done and steps < 100:
        actions = {}
        for i in range(MAX_TEAMS):
            str = f"{i}"
            try:
                actions[str] = agents[i].choose_action(obs[str])
            except Exception as e:
                print(f"Team {i+1} error: {e}")
                actions[str] = default_action
        obs, _, terminated, truncated, info = env.step(actions)
        #print(f"{info['infos']}")
        pos = np.zeros(MAX_TEAMS)
        dist = np.zeros(MAX_TEAMS)
        for i in range(MAX_TEAMS):
            str = f"{i}"
            pos[i] = info['infos'][str]['position']
            dist[i] = info['infos'][str]['distance']
        # print(f"{names}{pos}")
        steps = steps + 1
        done = terminated or truncated
        positions.append(pos)
    average_pos = np.array(positions).mean(axis=0)
    std_pos = np.array(positions).std(axis=0)
    for i in range(MAX_TEAMS):
        print(f"{names[i]} avg:{average_pos[i]} std:{std_pos[i]}")
    env.close()

if __name__ == "__main__":
    main()
