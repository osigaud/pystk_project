import numpy as np
from agents.kart_agent import KartAgent

class Agent2(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.agent_positions = []
        self.obs = None
        self.name = "Team2"
        
        self.path_lookahead = path_lookahead
        self.stuck_steps = 0    
        self.recovery_steps = 0  
        
    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []
        
        self.stuck_steps = 0
        self.recovery_steps = 0

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
		
		

        velocity = np.array(obs["velocity"])) 
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
            
            
        print(f"angle actuel: {angle: .3f} rad, {np.degrees(angle):.1f}")
        
        action = {
            "acceleration": 0.7,   
            "steer": steering,      
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue": False,
            "fire": False,
        }
        return action
