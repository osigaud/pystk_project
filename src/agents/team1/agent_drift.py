from agents.kart_agent import KartAgent
import numpy as np

#Agent qui derape quand la courbe est serree (virage serre)
class AgentDrift(KartAgent)  :

    """Agent qui active le drift dans les virages serrés.
    
    Attributes:
        is_drifting (bool): Indique si le kart est actuellement en drift.
    """

    def __init__(self, env, conf, agent, ):
        super().__init__(env)
        self.conf = conf
        self.agent = agent

        self.is_drifting = False   

    def drift_control(self, obs, action) :

        """Active ou désactive le drift selon la situation.

        Conditions d’activation :
        - Virage serré détecté via `analyse`
        - |steer| >= 0.5
        - vitesse > 6

        Args:
            obs (dict): Observations contenant notamment `velocity`.
            action (dict): Action courante (modifie la clé "drift").

        Returns:
            dict: Action avec le champ "drift" mis à True ou False.
        """

        virage_serre = self.analyse(obs)
        speed = np.linalg.norm(obs["velocity"])
        msa = obs["max_steer_angle"]     

        #condition pour deraper 
        drift_condition = ( virage_serre 
                            and speed > self.conf.speed_threshold   #la vitesse est assez grande
                            and abs(action["steer"]) > self.conf.steer_threshold  
                            and msa < self.conf.max_steer_angle_petit       
                            and self.target_obstacle is None   #Si il y a des items, on ne derape pas
                            )

        if drift_condition == True:                # si sa condi satisfait
            self.is_drifting = True
        elif speed < self.conf.stop_drift_speed:   # si la vitesse ne satisfait pas
            self.is_drifting = False

        action["drift"] = self.is_drifting

        if self.is_drifting:
            action["acceleration"] -= self.conf.frein_virage     # ralentir le kart pour deraper
            action["acceleration"] = np.clip(action["acceleration"], 0.1, 1)
        
        
        return action

    def choose_action(self, obs) :
        action = super().choose_action(obs)
        action = self.drift_control(obs, action)
        return action
