"""
MultiAgent race

All initial agents are RandomAgent
The simulation runs on the "black_forest" track with MAX_TEAMS karts.
"""
import sys, os
import numpy as np
from datetime import datetime
from pathlib import Path

# Append the "src" folder to sys.path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "src")))

from agents.team1.agent1 import Agent1
from agents.team2.agent2 import Agent2
from agents.team3.agent3 import Agent3
from agents.team4.agent4 import Agent4
from agents.team5.agent5 import Agent5
from agents.hidden.median_agent import MedianAgent
from agents.hidden.euler_agent import EulerAgent
from agents.hidden.items_agent import ItemsAgent
from pystk2_gymnasium.envs import STKRaceMultiEnv, AgentSpec
from pystk2_gymnasium.definitions import CameraMode

from scores import Scores, output_html

MAX_TEAMS = 5
MAPS = ['abyss', 'black_forest', 'candela_city', 'cocoa_temple', 'cornfield_crossing', 'fortmagma', 'gran_paradiso_island', 'hacienda', 'lighthouse', 'mines', 'minigolf', 'olivermath', 'ravenbridge_mansion', 'sandtrack', 'scotland', 'snowmountain', 'snowtuxpeak', 'stk_enterprise', 'volcano_island', 'xr591', 'zengarden']
MAX_STEPS = 2000
NB_REPEAT = 2

# Get the current timestamp
current_timestamp = datetime.now()

# Format it into a human-readable string
formatted_timestamp = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")

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
    return hash((self.name, self.rank_start, self.use_ai, self.camera_mode))
AgentSpec.__hash__ = agent_spec_hash

# Create agents specifications.
agents_specs = [
    AgentSpec(name=f"Team{i+1}", rank_start=i, use_ai=False, camera_mode=CameraMode.ON) for i in range(MAX_TEAMS)
]

def create_race(map=None):
    env = STKRaceMultiEnv(agents=agents_specs, track=map, num_kart=MAX_TEAMS) #, render_mode="human"

    # Instantiate the agents.

    agents = []
    names = []

    agents.append(Agent1(env, path_lookahead=3))
    agents.append(Agent2(env, path_lookahead=3))
    agents.append(Agent3(env, path_lookahead=3))
    agents.append(Agent4(env, path_lookahead=3))
    agents.append(Agent5(env, path_lookahead=3))
    np.random.shuffle(agents)

    for i in range(MAX_TEAMS):
        names.append(agents[i].name)
        agents_specs[i].name = agents[i].name
        agents_specs[i].kart = agents[i].name
    return env, agents, names


def single_race(env, agents, names, scores):
    obs, _ = env.reset()
    done = False
    steps = 0
    nb_finished = 0
    positions = []
    first = True
    wins = np.zeros(MAX_TEAMS)
    blocked = np.zeros(MAX_TEAMS)
    for i in range(MAX_TEAMS):
        agents[i].steps = MAX_STEPS
    while not done and steps < MAX_STEPS:
        actions = {}
        env.world_update()
        for i in range(MAX_TEAMS):
            str = f"{i}"
            try:
                actions[str] = agents[i].choose_action(obs[str])
            except Exception as e:
                print(f"{names[i]} error: {e}")
                actions[str] = default_action

            # check if agents have finished the race
            kart = env.world.karts[i]
            if kart.has_finished_race and not agents[i].isEnd:
                print(f"{names[i]} has finished the race at step {steps}")
                nb_finished += 1
                agents[i].isEnd = True
                agents[i].steps = steps
                if first:
                    wins[i] = 1
                    print(f"{names[i]} is first")
                first = False

        obs, _, _, _, info = env.step(actions)

        # prepare data to display leaderboard
        pos = np.zeros(MAX_TEAMS)
        for i in range(MAX_TEAMS):
            str = f"{i}"
            pos[i] = info['infos'][str]['position']
        steps = steps + 1
        done = (nb_finished == MAX_TEAMS)
        positions.append(pos)
    pos_avg = np.array(positions).mean(axis=0)
    pos_std = np.array(positions).std(axis=0)
    for i in range(MAX_TEAMS):
        if agents[i].steps == MAX_STEPS:
            blocked[i] = 1
            print(f"{names[i]} is blocked")
    for i in range(MAX_TEAMS):
        scores.append(names[i], pos_avg[i], pos_std[i], agents[i].steps, wins[i], blocked[i])
        agents[i].isEnd = False
    print("race duration:", steps)

def main_loop():
    scores = Scores()
    #unsatisfactory: first call just to init the names
    env, agents, names = create_race()
    for i in range(MAX_TEAMS):
        scores.init(names[i])

    for _ in range(NB_REPEAT):
        for j in range(len(MAPS)):
            track = MAPS[j]
            print(f"race : {j} track : {track}")
            env, agents, names = create_race(track)
            single_race(env, agents, names, scores)
            env.close()

    return scores
        
if __name__ == "__main__":
    scores = main_loop()
    output_html(Path("../../docs/index.html"), scores)
