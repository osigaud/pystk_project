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




    def hit_karts(self,obs):
        if self.attack_rival and not self.item_present(obs) and self.anticipe_kart.detectVirage(obs) <= 0.2 :
         
            karts_pos = obs.get('karts_position',[]) # positions des autres karts dans le référentiel du kart
            pos = karts_pos[0]
            x,z = pos[0],pos[2]
         
            center_path = obs.get("center_path", [])
            centre = np.array(center_path[0])
            distance_centre = np.linalg.norm(pos - centre)
            if abs(distance_centre) > 0.2:
                return None


            acceleration = 1
            target_angle = np.arctan2(x,z)




            nodes_path=obs.get("paths_start", [])


            if len(nodes_path) > 3:
                target_node = nodes_path[3]
                angle_target = np.arctan2(target_node[0], target_node[2])
                steering = np.clip(angle_target * 2, -1, 1)
            else:
                steering = 0
            
            correction_piste = self.steering.correction_centrePiste(obs)
            final_steering = np.clip(target_angle + correction_piste + steering, -1, 1)




            return {
                "acceleration": acceleration,
                "steer": final_steering,
                "brake": True, # brake=True active la marche arrière dans STK
                "drift": False,
                "nitro": False,
                "rescue": False,
                "fire": False,
            }      
        return None
        


