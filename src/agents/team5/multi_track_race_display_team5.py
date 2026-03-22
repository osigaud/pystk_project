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
from omegaconf import OmegaConf

# Permet la parallélisation des courses.
from concurrent.futures import ProcessPoolExecutor, as_completed


SRC_DIR = Path(__file__).resolve().parents[2]
MAIN_DIR = SRC_DIR / "main"

os.chdir(MAIN_DIR)
sys.path.append(str(SRC_DIR))

# Append the "src" folder to sys.path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "src")))

from agents.team1.agent1 import Agent1
from agents.team2.agent2 import Agent2
from agents.team3.agent3 import Agent3
from agents.team4.agent4 import Agent4
from agents.team5.agent5 import Agent5
from pystk2_gymnasium.envs import STKRaceMultiEnv, AgentSpec
from pystk2_gymnasium.definitions import CameraMode

MAX_TEAMS = 5
NB_RACES = 1   # Nombre de courses à chaque fois qu'on lance multi_track_race_team5
MAX_STEPS = 1300

# Get the current timestamp
current_timestamp = datetime.now()

# Format it into a human-readable string
formatted_timestamp = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")

@dataclass
class Scores:
    def __init__(self):
        self.dict = {}
    
    def init(self, name):
        self.dict[name] = [[], [], []]

    def append(self, name, pos, pos_std, steps):
        self.dict[name][0].append(pos)
        self.dict[name][1].append(pos_std)
        self.dict[name][2].append(steps)

    def display(self):
        print(self.dict)

    def display_mean(self):
        for k in self.dict:
            print(f"{k}: {np.array(self.dict[k][0]).mean()}, {np.array(self.dict[k][1]).mean()}, {np.array(self.dict[k][2]).mean()}, {np.array(self.dict[k][2]).std()}")

    def display_html(self, fp):
        for k in self.dict:
            fp.write(f"""<tr><td>{k}</td>""")
            fp.write(
                    f"""<td>{np.array(self.dict[k][0]).mean():.2f}</td>"""
                    f"""<td>{np.array(self.dict[k][1]).mean():.2f}</td>"""
                    f"""<td>{np.array(self.dict[k][2]).mean():.2f}</td>"""
                    f"""<td>{np.array(self.dict[k][2]).std():.2f}</td>"""
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

def create_race(cfg=None):
    # Create the multi-agent environment for N karts.
    if NB_RACES==1:
        env = STKRaceMultiEnv(agents=agents_specs, track="xr591", render_mode="human", num_kart=MAX_TEAMS)  # render_mode = None = Aucune fenêtre graphique
    else:
        env = STKRaceMultiEnv(agents=agents_specs, render_mode="human", num_kart=MAX_TEAMS)

    # Instantiate the agents.

    agents = []
    names = []

    agents.append(Agent1(env, path_lookahead=3))
    agents.append(Agent2(env, path_lookahead=3))
    agents.append(Agent3(env, path_lookahead=3))
    agents.append(Agent4(env, path_lookahead=3))
    agents.append(Agent5(env, path_lookahead=3, cfg=None))   # On donne le fichier de configuration chargé en mémoire à notre Agent5
    np.random.shuffle(agents)

    for i in range(MAX_TEAMS):
        names.append(agents[i].name)
        agents_specs[i].name = agents[i].name
        agents_specs[i].kart = agents[i].name
    return env, agents, names


def single_race(cfg=None):
    env, agents, names = create_race(cfg)
    obs, _ = env.reset()
    done = False
    steps = 0
    nb_finished = 0
    positions = []

    for i in range(MAX_TEAMS):
        agents[i].steps = MAX_STEPS

    while not done and steps < MAX_STEPS:
        actions = {}
        env.world_update()

        for i in range(MAX_TEAMS):
            key = f"{i}"
            try:
                actions[key] = agents[i].choose_action(obs[key])
            except Exception as e:
                print(f"Team {i+1} error: {e}")
                actions[key] = default_action

            kart = env.world.karts[i]
            if kart.has_finished_race and not agents[i].isEnd:
                print(f"{names[i]} has finished the race at step {steps}")
                nb_finished += 1
                agents[i].isEnd = True
                agents[i].steps = steps

        obs, _, _, _, info = env.step(actions)

        pos = np.zeros(MAX_TEAMS)
        for i in range(MAX_TEAMS):
            key = f"{i}"
            pos[i] = info["infos"][key]["position"]

        steps += 1
        done = (nb_finished == MAX_TEAMS)
        positions.append(pos)

    pos_avg = np.array(positions).mean(axis=0)
    pos_std = np.array(positions).std(axis=0)

    race_data = []
    for i in range(MAX_TEAMS):
        if not agents[i].isEnd:
            race_data.append((names[i], 5, 5, MAX_STEPS))
        else:
            race_data.append((names[i], pos_avg[i], pos_std[i], agents[i].steps))

    env.close()
    print("race duration:", steps)
    return race_data

def single_race_worker(cfg_dict):
    cfg = OmegaConf.create(cfg_dict) if cfg_dict is not None else None
    return single_race(cfg)

def main_loop(cfg=None, nb_courses = NB_RACES, race_jobs=1):
    scores = Scores()

    env, agents, names = create_race(cfg)
    env.close()

    for name in names:
        scores.init(name)

    if race_jobs == 1:

        # On utilise le nb course passé en paramètres
        for j in range(nb_courses):
            print(f"race : {j}")
            race_data = single_race(cfg)
            for name, pos, pos_std, steps in race_data:
                scores.append(name, pos, pos_std, steps)
    else:
        cfg_dict = OmegaConf.to_container(cfg, resolve=True) if cfg is not None else None

        # On crée un pool de processus en parallèle
        with ProcessPoolExecutor(max_workers=race_jobs) as executor:

            # Chaque tâche correspond à UNE course parmis toutes les NB_RACES courses d'une recherche
            futures = [
                executor.submit(single_race_worker, cfg_dict)
                for _ in range(nb_courses)  # On utilise le nb course passé en paramètres
            ]

            # "as_completed" permet de traiter les courses dès qu'elles se terminent
            for j, future in enumerate(as_completed(futures)):
                print(f"race terminée : {j}")
                race_data = future.result()
                for name, pos, pos_std, steps in race_data:
                    scores.append(name, pos, pos_std, steps)

    print("final scores:")
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
      <th id="position">Avg. steps</th>
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
    input_config = input("Voulez vous utiliser le fichier config_opti.yaml ? [o/n] : ")

    if input_config == 'o':
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config_opti.yaml")
        cfg = OmegaConf.load(config_path)
        print("Le kart utilise le fichier config_opti.yaml\n")
        scores = main_loop(cfg=cfg)

    else : 
        # Si cfg=None alors on utilise le fichier config.yaml classique. Voir le __init__() de agent5.py
        print("Le kart utilise le fichier config.yaml\n")
        scores = main_loop(cfg=None)
    output_html(Path("../../docs/index.html"), scores)
