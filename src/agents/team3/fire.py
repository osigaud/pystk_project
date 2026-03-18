import math
import numpy
from agents.kart_agent import KartAgent

class Fire(KartAgent):
    def __init__(self, env, pilot):
        super().__init__(env)
        self.pilot = pilot

    def reset(self):
        self.pilot.reset()

    def choose_action(self, obs):
        action = self.pilot.choose_action(obs)
        fire = False
       
        # Notre kart utilise les items si et seulement si un kart est devant nous
        # Cette fois-ci on utilise l'angle pour mieux cibler les karts adverses et faire mouche
         
        if obs["powerup"] != 0: 
            karts = obs["karts_position"]
            for kart in karts:
                kart_x, kart_z = kart[0], kart[2]
                dist = math.sqrt(kart_x**2 + kart_z**2)
                angle = math.atan2(kart_x, kart_z)
                    
                if dist < 30.0 and abs(angle) < 0.2:
                    fire = True
                    #break

        action["fire"] = fire
        return action
