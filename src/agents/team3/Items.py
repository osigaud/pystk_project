import math
import numpy as np

from agents.team3.Pilot import Pilot

class Items():
    def choose_action(self, obs):
        action = Pilot.choose_action(self, obs)

    	
		# On récupère la position des karts grâce à sa variable d'observation
        powerup_type = obs["powerup_type"]
        
        action["fire"] = False
        enemy_positions = obs["karts_position"]
        
        # On regarde ici si les karts adverses sont devant nous
        # Ou derrière nous
        # S'ils le sont et qu'on a récolté un bon item alors on tire sur eux
        for i in range(len(enemy_positions)):
            ex, _, ez = enemy_positions[i]
            if (5.0 < ez < 50.0) and powerup_type not in [2, 10]:
                angle_to_enemy = abs(np.arctan2(ex, ez))
                if (angle_to_enemy < 1): 
                    action["fire"] = True
                    break
            elif (-20.0 < ez < -2.0):
                angle_to_enemy_behind = abs(np.arctan2(ex, abs(ez)))
                if (angle_to_enemy_behind < 1) and powerup_type in [2, 10]:
                    action["fire"] = True
                    break

        return action