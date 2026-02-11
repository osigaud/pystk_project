import numpy as np
from agents.kart_agent import KartAgent

class Agent3(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.obs = None
        self.isEnd = False
        self.name = "Team L'Eclair"
        self.time_blocked = 0

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = [] 

    def endOfTrack(self):
        return self.isEnd
    
    def choose_action(self, obs):
        target = np.array(obs["paths_start"][self.path_lookahead]) 
        x = target[0]
        z = target[2]
        steer = (x / z) * 1.5
        speed = (((obs["velocity"][0])**2) + ((obs["velocity"][2])**2))**0.5
        brake = False
        nitro = False
        fire = False
        if abs(steer) > 1.0:
            acceleration = 0.3
        else:
            acceleration = 1.0
        if abs(steer) < 0.1 and speed < 20:
            nitro = True
        if (speed < 2.0):
            self.time_blocked += 1 
            if (self.time_blocked > 10):
                acceleration = 0.0
                brake = True
                steer = -steer
        if (self.time_blocked == 20):
            self.time_blocked = 0 
        if (x<1.0):
        	fire = True
        action = {
            "acceleration": acceleration,
            "steer": steer,
            "brake": brake,
            "drift": False,
            "nitro": nitro,
            "rescue": False,
            "fire": fire,
        }
        return action
