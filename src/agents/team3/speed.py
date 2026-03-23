import math
import numpy
from agents.kart_agent import KartAgent

class Speed(KartAgent):
    def __init__(self, env, pilot):
        super().__init__(env)
        self.pilot = pilot

    def reset(self):
        self.pilot.reset()

    def choose_action(self, obs):
        action = self.pilot.choose_action(obs)
        steer = action["steer"]
        
        # On utilise pythagore pour obtenir la vitesse sqrt(x²+z²)
        # On ignore la coordonnée y car elle est inutile dans notre cas
        speed = math.sqrt(obs["velocity"][0]**2 + obs["velocity"][2]**2)
        idx = int(speed / 8.0) + 1 
        
        # Récupération des coordonnées x et z
        # Puis calcul de l'angle
        target_ctr_x = (obs["paths_start"][idx][0] + obs["paths_end"][idx][0]) / 2.0
        target_ctr_z = (obs["paths_start"][idx][2] + obs["paths_end"][idx][2]) / 2.0
        err = math.atan2(target_ctr_x, target_ctr_z)
        
        half_width = obs["paths_width"][idx][0] / 2.0

        future_idx = idx + 5 
        future_ctr_x = (obs["paths_start"][future_idx][0] + obs["paths_end"][future_idx][0]) / 2.0
        future_ctr_z = (obs["paths_start"][future_idx][2] + obs["paths_end"][future_idx][2]) / 2.0
        future_err = math.atan2(future_ctr_x, future_ctr_z)

        is_track_wide_enough = half_width > 3.5 
        dist_center = abs(obs["center_path_distance"][0])
        is_safe_from_edge = dist_center < (half_width - 1.5)

        acceleration = 1.0
        brake = False
        drift = False
        nitro = False

        if is_track_wide_enough and is_safe_from_edge and abs(future_err) > 0.45 and speed > 13.0:
            drift = True
            steer = max(-1.0, min(steer * 1.3, 1.0))
            
        if drift and (abs(err) < 0.3 or dist_center > (half_width - 1.0)):
            drift = False

        if abs(future_err) > 0.65 and speed > 14.0 and not drift and not is_track_wide_enough:
            acceleration = 0.2
            brake = True
        elif abs(err) > 1.2 and speed > 10.0:
            acceleration = 0.0
            brake = True

        if abs(steer) < 0.3 and speed > 8.0 and is_safe_from_edge:
            nitro = True

        action["acceleration"] = acceleration
        action["brake"] = brake
        action["drift"] = drift
        action["nitro"] = nitro
        action["steer"] = steer

        return action
