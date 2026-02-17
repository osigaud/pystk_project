from .agent_obstacles import AgentObstacles

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

        if abs(distance_down_track - self.last_distance) < 0.1 and distance_down_track > 5 and (obs["jumping"] == 0) and not (attachment == 2) :
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
                
        if self.block_counter > 18 :
            self.is_braking = True
            self.unblock_steps = 4
        if self.is_braking : 
            action = self.unblock_action(action)
        return action
