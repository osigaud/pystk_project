import math
import numpy as np

from agents.team3.Items import Items

class Rescue():
    def choose_action(self, obs):
        action = Items.choose_action(self, obs)

        # La vitesse ici est représenter par Pythagore
        speed = math.sqrt(obs["velocity"][0]**2 + obs["velocity"][2]**2)

		# Si jamais on est bloqué (vitesse faible, on essaie d'accélérer,
		# Qu'on ne freine pas et qu'on est pas au début de la piste)
		# Alors on se fait secourir plutôt que de faire marche arrière
		# Car c'est plus rapide
        action["rescue"] = False
            
        if ((speed < 1.5) and (action["acceleration"] > 0.5) and (action["brake"] == False) and (obs["distance_down_track"] > 5.0)):
            self.stuck_timer += 1

        if self.stuck_timer > 10:
           if self.stuck_timer < 25:
                self.stuck_timer += 1
           else:
                action["rescue"] = True
                self.stuck_timer = 0
            
           action["acceleration"] = 0
           action["steer"] = -action["steer"]
           action["brake"] = True

        
        return action