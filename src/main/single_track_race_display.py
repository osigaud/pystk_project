"""
MultiAgent race

All initial agents are RandomAgent
The simulation runs on the "black_forest" track with MAX_TEAMS karts.
"""

import sys, os
import numpy as np
from pathlib import Path

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
from pystk2_gymnasium.definitions import CameraMode

MAX_TEAMS = 7
MAX_STEPS = 1000
NB_RACES = 1

# Make AgentSpec hashable.
def agent_spec_hash(self):
    return hash((self.name, self.rank_start, self.use_ai, self.camera_mode))
AgentSpec.__hash__ = agent_spec_hash

# Create agents specifications.
agents_specs = [
    AgentSpec(name=f"Team{i+1}", rank_start=i, use_ai=False, camera_mode=CameraMode.ON) for i in range(MAX_TEAMS)
]

def create_race():
    # Create the multi-agent environment for N karts.
    env = STKRaceMultiEnv(agents=agents_specs, track="olivermath", render_mode="human", num_kart=MAX_TEAMS)

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
        agents_specs[i].name = agents[i].name
        agents_specs[i].kart = agents[i].name
    return env, agents, names


def single_race(env, agents, names):
    obs, _ = env.reset()
    done = False
    steps = 0
    nb_finished = 0
    first = True
    while not done and steps < MAX_STEPS:
        actions = {}
        env.world_update()
        for i in range(MAX_TEAMS):
            str = f"{i}"
            try:
                actions[str] = agents[i].choose_action(obs[str])
            except Exception as e:
                print(f" {names[i]} error: {e}")
                actions[str] = default_action

            # check if agents have finished the race
            kart = env.world.karts[i]
            if kart.has_finished_race and not agents[i].isEnd:
                print(f"{names[i]} has finished the race at step: {steps}")
                nb_finished += 1
                agents[i].isEnd = True
                if first:
                    print(f"{names[i]} is first")
                first = False

        obs, _, _, _, info = env.step(actions)

        # prepare data to display leaderboard
        pos = np.zeros(MAX_TEAMS)
        dist = np.zeros(MAX_TEAMS)
        steps = steps + 1
        done = (nb_finished == MAX_TEAMS)

def main_loop():
    #unsatisfactory: first call just to init the names
    env, agents, names = create_race()
    env, agents, names = create_race()
    single_race(env, agents, names)
    env.close()
        
if __name__ == "__main__":
    main_loop()

