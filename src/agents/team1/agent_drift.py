from .agent_items import AgentItems
import numpy as np

#Agent qui derape quand la courbe est serree (virage serre)
class AgentDrift(AgentItems)  :
    def __init__(self, env, path_lookahead = 3):
        super().__init__(env,path_lookahead)
        self.is_drifting = False   

    def drift_control(self, obs, action) :
        virage_serre = self.analyse(obs)
        speed = np.linalg.norm(obs["velocity"])
        msa = obs["max_steer_angle"]

        #condition pour deraper 
        drift_condition = ( virage_serre 
                            and speed > 7   #la vitesse est assez grande
                            and abs(action["steer"]) > 0.4  
                            and msa < self.msapetit        
                            and sefl.target_obstacle is None   #Si il y a des items, on ne derape pas
                            )

        if drift_condition == True:  # si sa condi satisfait
            self.is_drifting = True
        elif speed < 4:  #si la vitesse ne satisfait pas
            self.is_drifting = False

        action["drift"] = self.is_drifting

        if self.is_drifting:
            action["acceleration"] *= 0.8 # ralentir le kart pour deraper

        return action

    def choose_action(self, obs) :
        action = super().choose_action(obs)
        action = self.drift_control(obs, action)
        return action
