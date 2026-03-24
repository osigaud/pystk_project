import math
import numpy
from agents.kart_agent import KartAgent

class Rescue(KartAgent):
    def __init__(self, env, pilot):
        super().__init__(env)
        self.pilot = pilot
        self.time_blocked = 0

    def reset(self):
        self.pilot.reset()
        self.time_blocked = 0

    def choose_action(self, obs):
        action = self.pilot.choose_action(obs)
        
        speed = math.sqrt(obs["velocity"][0]**2 + obs["velocity"][2]**2)

        rescue = False
        if speed < 1.0:
            self.time_blocked += 1
        else:
            self.time_blocked = 0
		# Si on est bloqué trop longtemps alors
		# Le kart est secouru par l'oiseau bleue
		# A revoir ! Car ne fonctionne plus correctement
        if self.time_blocked >= 35:
            rescue = True
            self.time_blocked = 0

        action["rescue"] = rescue
        return action
