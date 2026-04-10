import math
import numpy
from agents.kart_agent import KartAgent

class Steer(KartAgent):
    def __init__(self, env):
        super().__init__(env)
        self.prev_err = 0.0

    def reset(self):
        self.prev_err = 0.0

    def choose_action(self, obs):
    
        speed = math.sqrt(obs["velocity"][0]**2 + obs["velocity"][2]**2)
        idx = int(speed / 12.0) + 1 
        
        target_ctr_x = (obs["paths_start"][idx][0] + obs["paths_end"][idx][0]) / 2.0
        target_ctr_z = (obs["paths_start"][idx][2] + obs["paths_end"][idx][2]) / 2.0

        path_width = obs["paths_width"][idx]
        half_width = path_width[0] / 2.0

        items_type = obs["items_type"]
        items_pos = obs["items_position"]
        danger = False
        #bonus_available = False
        closest_bad_z = 20.0
        closest_bad_x = 0.0
        #closest_good_z = 10.0
        #closest_good_x = 0.0

        for i in range(len(items_type)):
            itype = items_type[i]
            item_x = items_pos[i][0]
            item_z = items_pos[i][2]

            if itype in [1, 4] and 0 < item_z < 20.0 and abs(item_x) < 2.0:
                if item_z < closest_bad_z:
                    closest_bad_z = item_z
                    closest_bad_x = item_x
                    danger = True
            #elif itype in [2, 3] and 0 < item_z < 10.0 and abs(item_x) < 1.5:
             #   if item_z < closest_good_z:
              #      closest_good_z = item_z
               #     closest_good_x = item_x
                #    bonus_available = True

        offset_force = 0.0
        if danger:
            avoid_force = (20.0 - closest_bad_z) * 0.8
            if abs(closest_bad_x) < 0.2:
                offset_force += avoid_force 
            else:
                if closest_bad_x > 0:
                    offset_force += -avoid_force 
                else:
                    offset_force += avoid_force 
 

        #elif bonus_available:
         #   offset_force = closest_good_x * 0.5 

        if danger:
        	safe_margin = 0.5   
        else:
        	safe_margin = 1.5
        offset_force = max(-half_width + safe_margin, min(offset_force, half_width - safe_margin))
        target_ctr_x += offset_force

        err = math.atan2(target_ctr_x, target_ctr_z)#angle entre x cible et z cible , 
        p_k = 0.8
        d_k = 1.5 
        drv = err - self.prev_err
        self.prev_err = err
        steer = max(-1.0, min(p_k * err + d_k * drv, 1.0))





        action = {
            "acceleration": 1.0,
            "steer": steer,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue": False,
            "fire": False
        } 
        return action
