"""
MultiAgent race

All initial agents are RandomAgent
The simulation runs on the "black_forest" track with MAX_TEAMS karts.
"""

import sys, os
import numpy as np
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass


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

def create_race():
    # Create the multi-agent environment for N karts.
    if NB_RACES==1:
        env = STKRaceMultiEnv(agents=agents_specs, track="abyss", render_mode="human", num_kart=MAX_TEAMS)
    else:
        env = STKRaceMultiEnv(agents=agents_specs, render_mode="human", num_kart=MAX_TEAMS)

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


def single_race(env, agents, names, scores):
    obs, _ = env.reset()
    done = False
    steps = 0
    positions = []
    while not done and steps < MAX_STEPS:
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
        steps = steps + 1
        done = terminated or truncated
        positions.append(pos)
    avg_pos = np.array(positions).mean(axis=0)
    std_pos = np.array(positions).std(axis=0)
    for i in range(MAX_TEAMS):
        scores.append(names[i], avg_pos[i], std_pos[i])

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
    # scores.display()
    # scores.display_mean()
    return scores


def output_html(output: Path, scores: Scores):
    # Use https://github.com/tofsjonas/sortable?tab=readme-ov-file#1-link-to-jsdelivr
    with output.open("wt") as fp:
        fp.write(
            f"""<html><head>
<title>STK Race results</title>
<link href="https://cdn.jsdelivr.net/gh/tofsjonas/sortable@latest/dist/sortable.min.css" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/gh/tofsjonas/sortable@latest/dist/sortable.min.js"></script>
<body>
<h1>Team evaluation on SuperTuxKart</h1><div style="margin: 10px; font-weight: bold">Timestamp: {formatted_timestamp}</div>
<table class="sortable n-last asc">
  <thead>
    <tr>
      <th class="no-sort">Name</th>
      <th id="position">Avg. position</th>
      <th class="no-sort">±</th>
    </tr>
  </thead>
  <tbody>"""
        )

        scores.display_html(fp)
            
        fp.write(
            """<script>
  window.addEventListener('load', function () {
    const el = document.getElementById('position')
    if (el) {
      el.click()
    }
  })
</script>
"""
        )
        fp.write("""</body>""")

if __name__ == "__main__":
    scores = main_loop()
    output_html(Path("../../docs/index.html"), scores)
