from .agent_obstacles import AgentObstacles
import numpy as np

MIN_PROGRESS_THRESHOLD = 0.5
BLOCK_COUNTER_THRESHOLD = 18
UNBLOCK_STEPS_DEFAULT = 6

class AgentRescue(AgentObstacles) : 
    #Prendre le cas en compte où on est étourdi par un item dans is_blocked
    def __init__(self, env, path_lookahead=3): 
        super().__init__(env, path_lookahead)  
        self.last_distance = None
        self.block_counter = 0
        self.unblock_steps = 0
        self.is_braking = False

    def is_blocked(self, obs):
        """
        Paramètres : obs
        Incrémente self.block_counter si le kart n'a pas bougé
        """
        distance_down_track = obs["distance_down_track"][0]
        attachment = obs["attachment"]
        if self.last_distance is None :
            self.last_distance = distance_down_track

        if abs(distance_down_track - self.last_distance) < MIN_PROGRESS_THRESHOLD and distance_down_track > 5 and (obs["jumping"] == 0) :
            self.block_counter += 1
        else:
            self.block_counter = 0
            self.last_distance = distance_down_track

    def unblock_action(self, act):
        """
        Paramètres : act (dict)
        Renvoie : act (dict), modifié si on doit reculer
        """
        if self.unblock_steps > 0 : 
            self.unblock_steps -= 1
            return {
                "acceleration" : 0, 
                "steer" : 0, 
                "brake" : True,
                "drift" : False,
                "nitro" : False,
                "rescue" : False,
                "fire" : False,
            }
        else : 
            self.is_braking = False
            return act
    
    def choose_action(self, obs):
        """
        Paramètres : obs
        Renvoie : action (dict), le dictionnaire d'actions de notre kart
        """
        self.is_blocked(obs)
        action = super().choose_action(obs)
                
        if self.block_counter > BLOCK_COUNTER_THRESHOLD :
            self.is_braking = True
            self.unblock_steps = UNBLOCK_STEPS_DEFAULT
        if self.is_braking : 
            action = self.unblock_action(action)
        return action
