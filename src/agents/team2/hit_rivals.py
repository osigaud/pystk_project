import numpy as np
from .steering_piste import SteeringPiste
from .rival_attack import AttackRivals
from .anticipe_kart import AnticipeKart
from omegaconf import OmegaConf


cfg = OmegaConf.load("../agents/team2/configDemoPilote.yaml")


class HitRivals:
    def __init__(self):
        self.attack_rival = AttackRivals()
        self.anticipe_kart = AnticipeKart(cfg)
        self.steering = SteeringPiste(cfg)

    def item_present(self, obs):
        items_pos = obs.get('items_position', [])

        for pos in items_pos:
            pos = np.array(pos)
            dist = np.linalg.norm(pos)

            # item devant et proche
            if pos[2] > 0 and dist < 20:
                return True

        return False

    def hit_karts(self, obs):
        
        #conditions pour attaquer:
            #pas d'item en vu,pas de virage,adv loin du centre 
        if (not self.item_present(obs) and self.anticipe_kart.detectVirage(obs) <= 0.2):
            karts_pos = obs.get('karts_position', [])
            pos = np.array(karts_pos[1])
            x, z = pos[0], pos[2]

            center_path = obs.get("center_path", [])
            centre = np.array(center_path[0])
            distance_centre = np.linalg.norm(pos - centre)

            #ne pas attaquer si adversaire trop éloigné du centre
            if distance_centre > cfg.hit.dist_centre:
                return None

            acceleration = 1
            target_angle = np.arctan2(x, z)

            nodes_path = obs.get("paths_start", [])

            if len(nodes_path) > 3:
                target_node = nodes_path[3]
                angle_target = np.arctan2(target_node[0], target_node[2])
                steering = np.clip(angle_target * 2, -1, 1)
            else:
                steering = 0

            correction_piste = self.steering.correction_centrePiste(obs)

            final_steering = np.clip(target_angle + correction_piste +steering,-1, 1)
            #virage = self.anticipe_kart.detectVirage(obs)
            #drift = virage > cfg.ligne_droite
            return {
                "acceleration": acceleration,
                "steer": final_steering,
                "brake": False, 
                "drift": False,
                "nitro": False,
                "rescue": False,
                "fire": False,
            }

        return None