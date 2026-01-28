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
        self.times_blocked = 0

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
        	acceleration = 0.9
        	brake = False
        speed = obs["velocity"][2]
        if (speed < 0.20 and obs["distance_down_track"] > 5.0):
        	self.times_blocked = self.times_blocked + 1
        	if (self.times_blocked > 10):
        		acceleration = 0.0
        		brake = True
        		x = -x
        if (self.times_blocked == 18):
        	self.times_blocked = 0
        action = {
            "acceleration": acceleration,
            "steer": x,
            "brake": brake,
            "drift": False,
            "nitro": False,
            "rescue": False,
            "fire": False,
        }
        return action
    def dodge(self,obs):
        danger_dist = 6.5
        dodge_strength = 0.8
        dodge = 0.0
        eps=0.05
        slow_down = False       
        path_width = obs["paths_width"][0]
        lane_width = path_width/2
        
        for i in range (len(obs["items_position"])):
            pos=obs["items_position"][i]
            it_type=obs["items_type"][i]
            x=pos[0]
            z=pos[2]
            if it_type==1: #banana
                if z>0 and z < danger_dist :    #item is in front and is dangerously close
                    if abs(x) < lane_width:    #item is in the current lane
                        if abs(x)<eps:    #item directly in front
                             center_x = obs["center_path"][0]
                             if center_x > 0 :
                                 dodge = -dodge_strength     #steer right
                             else: 
                                 dodge = dodge_strength    #steer left
                        elif x>0:    #item to the left
                            dodge = -dodge_strength     #steering negative/turning right
                        else :     #item to the right
                            dodge = dodge_strength    #steering positive/turning left
                        slow_down=True  
                        break
        return dodge,slow_down
