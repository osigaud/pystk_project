import numpy as np

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent

class Agent3(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "TEAM L'ÉCLAIR"
        self.time_blocked = 0

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []


        

    def endOfTrack(self):
        return self.isEnd
    
    def choose_action(self, obs):
        target = obs["paths_end"][0] #return a vector [x,y,z]
        x = target[0] #Extracting the x
        if (abs(x) > 0.5 and obs["distance_down_track"] > 5.0):
        	acceleration = 0.15
        	brake = True
        else:
        	acceleration = 0.75
        	brake = False
        speed = obs["velocity"][2]
        if (speed < 0.20 and obs["distance_down_track"] > 5.0):
        	self.time_blocked = self.time_blocked + 1
        	if (self.time_blocked > 10):
        		acceleration = 0.0
        		brake = True
        		x = -x
                
        if (self.times_blocked == 18):
        	self.times_blocked = 0


        next_item = obs["items_position"][0]
        item_x_axis = next_item[0]
        item_z_axis = next_item[2]
        item = obs["items_type"][0]
        if (item == 1 and item_z_axis < 15 and abs(item_x_axis) < 5.0):
            if (item_x_axis > 0):
                x = -0.3
            else:
                x = 0.3  

       

        boost=obs["attachment"]
        use_fire=False;
        print(obs["items_type"]) #items_type


        #code hakim fonctionne pas totalement(les attachements sactive juste avant de toucher une banane)
        #if boost !=None:
        #    if (boost in [0,1,2,3]): # detecte les attachements 
        #        use_fire=True;


        #code dylan qui fonctionne mieux mais que je (hakim) comprend pas la logique
        if boost !=None:
            use_fire = False
            if (obs["items_type"][0] == 0 and boost == 9): #extracting the next attachement on the track 
                use_fire = True
    



        action = {
            "acceleration": acceleration,
            "steer": x,
            "brake": brake,
            "drift": False,
            "nitro": False,
            "rescue": False,
            "fire": use_fire,
        }
        return action
