import numpy as np

from utils.track_utils import compute_curvature, compute_slope

from omegaconf import OmegaConf

cfg = OmegaConf.load("../agents/team3/config.yml")


class Pilot():
    
    def choose_action(self, obs):

        target = obs["paths_end"][0] #return a vector [x,y,z]
        x = target[0] #Extracting the x

        # vitesse / accélération / nitro
        energy = obs["energy"][0]
        nitro = False
        if abs(x)/20 > cfg.steering.sharp_turn_threshold and obs["distance_down_track"] > 5.0:
            acceleration = cfg.acceleration.sharp_turn
            brake = True
        elif energy > cfg.nitro.min_energy and abs(x)/20 < cfg.steering.straight_threshold:
            acceleration = 1
            brake = False
            nitro = True
        else:
            acceleration = 1
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
