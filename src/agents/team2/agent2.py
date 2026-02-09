import numpy as np
import random

from agents.kart_agent import KartAgent


class Agent2(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "Team2"
        self.path_lookahead = path_lookahead
        self.stuck_steps = 0    
        self.recovery_steps = 0  


    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

        self.stuck_steps = 0
        self.recovery_steps = 0


    def endOfTrack(self):
        return self.isEnd


#def calculer_direction(self,obs ) : 
        #distance = obs['center_path'][0] # center_path designe le vecteur du centre de la route donc il contient 3 coordonnees l'un l'index gauche ou droite l'autre la hauteur et le dernier la distance devant nous le 0 donc c'est l'indice de ce quon a besoin poiur la distance 

        #angle = distance * 0.4 # si la distance est par exemple 2 metres  il va reagir que 40% de la distance 
        #if angle > 1:
            #angle = 1  # on s'assure que l'angle reste entre -1 et 1
        #elif angle < -1:
            #angle = -1
            
        #return angle        


    def choose_action(self, obs):

      if self.recovery_steps > 0:
            self.recovery_steps -= 1
            return {
                "acceleration": 0.0,
                "steer": 0.0,
                "brake": True,  
                "drift": False,
                "nitro": False,
                "rescue": False,
                "fire": False,
            }
      velocity = np.array(obs["velocity"])
      speed = np.linalg.norm(velocity)
      phase = obs.get["phase"]
      nodes_path = obs["paths_start"]
      if phase > 2:  
            if speed < 0.2:  
                self.stuck_steps += 1
            else:
                self.stuck_steps = 0
      if self.stuck_steps > 7:
            self.recovery_steps = 15
            self.stuck_steps = 0

      if len(nodes_path) > self.path_lookahead:
            target_node = nodes_path[self.path_lookahead]
            angle = np.arctan2(target_node[0], target_node[2])
            steering = np.clip(angle * 2, -1, 1)
      else:
            steering = 0
           
           
      #print(f"angle actuel: {angle: .3f} rad, {np.degrees(angle):.1f}")
       

      action = {
            "acceleration": 0.7,
            "steer": steering,
            "brake": False, 
            "drift": False,
            "nitro":False,
            "rescue":False,
            "fire": False
            }

        #if target_item_distance== 10:
            #if obs['target_item_type'] in bad_type:
                #if target_item_angle >5: # obstacle a droite
                    #action["steer"]= - 0.5 # on tourne a gauche
                    #action["nitro"]=False
                    #action["acceleration"]= action["acceleration"] - 0.5 #val a determiner
                #elif target_item_angle ==0 : # obstacle a droite
                    #action["steer"]= - 0.5 # on tourne a gauche ou droite
                    #action["nitro"]=False
                    #action["acceleration"]= action["acceleration"] - 0.5 #val a determiner
                #elif target_item_angle <-5: # obstacle a gauche 
                    #action["steer"]= 0.5 # on tourne a droite
                    #action["nitro"]=False
                    #action["acceleration"]= action["acceleration"] - 0.5 #val a determiner

            #elif target_item_type in good_type:
                #if target_item_angle <-5: # a gauche 
                    #action["steer"]= - 0.5 # on tourne a gauche
                    #action["nitro"]=True
                    #action["acceleration"]= action["acceleration"] + 0.5 #val a determiner
                #elif target_item_angle >5: #a droite
                    #action["steer"]= 0.5 # on tourne a droite
                    #action["nitro"]=True
                    #action["acceleration"]= action["acceleration"] + 0.5 #val a determiner
      return action
