from agents.kart_agent import KartAgent
import numpy as np

class AgentRescue(KartAgent) : 
    #Prendre le cas en compte où on est étourdi par un item dans is_blocked
    def __init__(self, env, conf, agent): 
        super().__init__(env)
        self.conf = conf
        self.agent = agent

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

        if abs(distance_down_track - self.last_distance) < self.conf.min_progress_threshold and distance_down_track > 5 and (obs["jumping"] == 0) :
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
        action = self.agent.choose_action(obs)
                
        if self.block_counter > self.conf.block_counter_threshold :
            self.is_braking = True
            self.unblock_steps = self.conf.unblock_steps_default
        if self.is_braking : 
            action = self.unblock_action(action)
        return action
