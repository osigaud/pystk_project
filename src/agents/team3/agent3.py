import numpy as np

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent

# imports nécessaires pour le bon fonctionnement de fichier yml
from pathlib import Path
from omegaconf import OmegaConf

# cherche le dossier parent et ensuite concatener pour obtenir le chemin complet
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.yml"

# charge le fichier yml
cfg = OmegaConf.load(CONFIG_PATH)


class Agent3(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "TEAM L'ÉCLAIR"
        self.time_blocked = 0

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = [] 

    def endOfTrack(self):
        return self.isEnd
    
    def choose_action(self, obs):
        target = obs["paths_end"][0] #return a vector [x,y,z]
        x = target[0] #Extracting the x

        # # items
        # items_pos = obs["items_position"]
        # items_type = obs["items_type"]
        # closest_dist = np.inf
        # bonus_x = None
        
        # for pos, typ in zip(items_pos, items_type):
        #     if typ in cfg.track_items.collectible_types:
        #         dist_z = pos[2]
        #         dist_x = pos[0]
        #         if 0 < dist_z < cfg.track_items.detection_distance and abs(dist_x) < cfg.steering.max_track_offset:
        #             if dist_z < closest_dist:
        #                 closest_dist = dist_z
        #                 bonus_x = dist_x

        # if bonus_x is not None:
        # 	x = bonus_x

        # vitesse / accélération / nitro
        energy = obs["energy"][0]
        nitro = False
        if abs(x) > cfg.steering.sharp_turn_threshold and obs["distance_down_track"] > 5.0:
            acceleration = cfg.acceleration.sharp_turn
            brake = True
        elif energy > cfg.nitro.min_energy and abs(x) < cfg.steering.straight_threshold:
            acceleration = cfg.acceleration.boost
            brake = False
            nitro = True
        else:
            acceleration = cfg.acceleration.normal
            brake = False

        # anti-blocage
        speed = obs["velocity"][2]
        if speed < cfg.speed.slow_speed_threshold and obs["distance_down_track"] > 5.0:
            self.time_blocked += 1
            if self.time_blocked > cfg.speed.unblock_time:
                acceleration = 0.0
                brake = True
                x = -x

        if self.time_blocked >= cfg.speed.reset_block_time:
            self.time_blocked = 0

        # évitement items dangereux
        next_item = obs["items_position"][0]
        item_x_axis = next_item[0]
        item_z_axis = next_item[2]
        item = obs["items_type"][0]

        if item == cfg.track_items.danger_type and item_z_axis < cfg.track_items.avoidance_distance and abs(item_x_axis) < cfg.track_items.avoidance_width:
            x = -cfg.steering.avoidance_offset if item_x_axis > 0 else cfg.steering.avoidance_offset

        boost = obs["attachment"]
        use_fire = False
        if boost is not None:
            if obs["items_type"][0] == cfg.fire.enemy_type and boost == cfg.fire.required_attachment:
                use_fire = True

        action = {
            "acceleration": acceleration,
            "steer": x,
            "brake": brake,
            "drift": False,
            "nitro": nitro,
            "rescue": False,
            "fire": use_fire,
        }
        return action
