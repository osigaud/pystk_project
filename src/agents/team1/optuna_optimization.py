import optuna

import sys, os
import numpy as np
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

# Append the "src" folder to sys.path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..", "src"))) #Changement du path ici pour que ce soit adapté

from agents.team1.agent1 import Agent1
from agents.team1.agentwrappers import AgentCenter
from agents.team1.agentwrappers import AgentCenter2

from pystk2_gymnasium.envs import STKRaceMultiEnv, AgentSpec
from pystk2_gymnasium.definitions import CameraMode

MAX_TEAMS = 3
NB_RACES = 1

# Get the current timestamp
current_timestamp = datetime.now()
# Format it into a human-readable string
formatted_timestamp = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")

@dataclass
class Scores:
    def __init__(self):
        self.dict = {}
    
    def init(self, name):
        self.dict[name] = [[], []]

    def append(self, name, pos, std):
        self.dict[name][0].append(pos)
        self.dict[name][1].append(std)

    def display(self):
        print(self.dict)

    def display_mean(self):
        for k in self.dict:
            print(f"{k}: {np.array(self.dict[k][0]).mean()}, {np.array(self.dict[k][1]).mean()}")

    def display_html(self, fp):
        for k in self.dict:
            fp.write(f"""<tr><td>{k}</td>""")
            fp.write(
                    f"""<td>{np.array(self.dict[k][0]).mean():.2f}</td>"""
                    f"""<td>{np.array(self.dict[k][1]).mean():.2f}</td>"""
                    "</tr>"
                )
            

default_action = {
            "acceleration": 0.0,
            "steer": 0.0,
            "brake": False,
            "drift": False, 
            "nitro": False, 
            "rescue":False, 
            "fire": False, 
        }


# Make AgentSpec hashable.
def agent_spec_hash(self):
    return hash((self.name, self.rank_start, self.use_ai, self.camera_mode))
AgentSpec.__hash__ = agent_spec_hash

# Create agents specifications.
agents_specs = [
    AgentSpec(name=f"Team{i+1}", rank_start=i, use_ai=False, camera_mode=CameraMode.ON) for i in range(MAX_TEAMS)
]

def create_race(distance, ajustement):
    # Create the multi-agent environment for N karts.
    if NB_RACES==1:
        env = STKRaceMultiEnv(agents=agents_specs, track="cornfield_crossing", num_kart=MAX_TEAMS) #track="xr591"
    else:
        env = STKRaceMultiEnv(agents=agents_specs, render_mode="human", num_kart=MAX_TEAMS)

    # Instantiate the agents.

    agents = []
    names = []

    agents.append(Agent1(env, path_lookahead=3, dist=distance, ajust=ajustement))
    agents.append(AgentCenter2(env, path_lookahead=3))  
    agents.append(AgentCenter2(env, path_lookahead=3))

    for i in range(MAX_TEAMS):
        names.append(agents[i].name)
    return env, agents, names

def single_race(env, agents, names, scores):
    obs, _ = env.reset()
    done = False
    steps = 0
    positions = []
    while not done and steps < 1500:
        actions = {}
        for i in range(MAX_TEAMS):
            str = f"{i}"
            try:
                actions[str] = agents[i].choose_action(obs[str])

            except Exception as e:
                print(f"Team {i+1} error: {e}")
                actions[str] = default_action
        obs, _, terminated, truncated, info = env.step(actions)
        pos = np.zeros(MAX_TEAMS)
        dist = np.zeros(MAX_TEAMS)
        for i in range(MAX_TEAMS):
            str = f"{i}"
            pos[i] = info['infos'][str]['position']
            dist[i] = info['infos'][str]['distance']
        # print(f"{names}{dist}")
        steps = steps + 1
        done = terminated or truncated
        positions.append(pos)
    avg_pos = np.array(positions).mean(axis=0)
    std_pos = np.array(positions).std(axis=0)
    for i in range(MAX_TEAMS):
        scores.append(names[i], avg_pos[i], std_pos[i])

"""
def main_loop():
    scores = Scores()
    #unsatisfactory: first call just to init the names
    env, agents, names = create_race()
    for i in range(MAX_TEAMS):
        scores.init(names[i])

    for j in range(NB_RACES):
        print(f"race : {j}")
        env, agents, names = create_race()
        single_race(env, agents, names, scores)

        env.close()

    print("final scores:")
    scores.display()
    scores.display_mean()
    return scores
"""

def run_once(dist, ajust):

    env, agents, names = create_race(dist, ajust)
    obs, _ = env.reset()
    done = False
    steps = 0

    max_distance = 0

    while not done and steps < 1500:
        actions = {}
        for i in range(MAX_TEAMS):
            actions[str(i)] = agents[i].choose_action(obs[str(i)])

        obs, _, terminated, truncated, info = env.step(actions)
        done = terminated or truncated
        steps += 1

        distance_i = info['infos']["0"]['distance']
        max_distance = max(max_distance, distance_i)

    env.close()

    if not terminated: #si le kart ne termine pas la course
        return 4000

    
    return steps

def objective(trial):

    dist = trial.suggest_float("dist", 0.2, 1.5)
    ajust = trial.suggest_float("ajust", 0.08, 0.9)

    score = run_once(dist, ajust)

    return score  # plus petit = meilleure position

study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials= 3000)

print(study.best_params)

"""
if __name__ == "__main__":
    scores = main_loop()
"""
