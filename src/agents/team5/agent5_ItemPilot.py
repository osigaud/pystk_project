import numpy as np
from agents.kart_agent import KartAgent


class Agent5Item(KartAgent):
    def __init__(self, env, pilot_agent, conf, path_lookahead=3):
        super().__init__(env)
        self.conf = conf
        self.pilot = pilot_agent
        self.name = "Donkey Drift"
        	
		
		
		
		
		
		
		
    def reset(self):
       	self.pilot.reset()
       	
    def choose_action(self, obs):
        # On récupère l'action calculée par le Mid Pilot
        action = self.pilot.choose_action(obs)
        return action
