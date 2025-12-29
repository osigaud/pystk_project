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


from agents.hidden.euler_agent import EulerAgent
from agents.hidden.items_agent import ItemsAgent
from agents.hidden.median_agent import MedianAgent
from agents.team2.agent2 import Agent2
from agents.team3.agent3 import Agent3
from agents.team4.agent4 import Agent4
from agents.team5.agent5 import Agent5
from agents.team6.agent6 import Agent6
from agents.team7.agent7 import Agent7
from pystk2_gymnasium.envs import STKRaceMultiEnv, AgentSpec

MAX_TEAMS = 3


# Get the current timestamp
current_timestamp = datetime.now()

# Format it into a human-readable string
formatted_timestamp = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Scores:
    name: str
    position: float
    pos_std: float


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
env = STKRaceMultiEnv(agents=agents_specs, track="xr591", render_mode="human", num_kart=MAX_TEAMS)

# Instantiate the agents.

agents = []
names = []

base = MedianAgent(env, path_lookahead=3)
agents.append(base)
agents.append(EulerAgent(base))
agents.append(ItemsAgent(base))
np.random.shuffle(agents)

for i in range(MAX_TEAMS):
    names.append(agents[i].name)

def main():
    obs, _ = env.reset()
    done = False
    steps = 0
    positions = []
    while not done and steps < 1000:
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
        print(f"{names}{dist}")
        steps = steps + 1
        done = terminated or truncated
        positions.append(pos)
    average_pos = np.array(positions).mean(axis=0)
    std_pos = np.array(positions).std(axis=0)
    scores = []
    for i in range(MAX_TEAMS):
        scores.append(Scores(names[i], average_pos[i], std_pos[i]))
    env.close()
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

        for i in range(MAX_TEAMS):
            fp.write(f"""<tr><td>{scores[i].name}</td>""")
            fp.write(
                    f"""<td>{scores[i].position:.2f}</td>"""
                    f"""<td>{scores[i].pos_std:.2f}</td>"""
                    "</tr>"
                )
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
    scores = main()
    output_html(Path("./results.html"), scores)
