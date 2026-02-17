from .agent_rescue import AgentRescue
import numpy as np

class AgentItems(AgentRescue) : 

    def __init__(self, env, path_lookahead=3) :
        super().__init__(env, path_lookahead) 

    def observation_item(self, obs, action) : 
        """
        Paramètres : obs, action (dict)
        Renvoie : action (dict), dictionnaire d'actions corrigé après prise en compte des objets tenus
        """
        current_item = obs["powerup"]

        match current_item : 
            case 0 or 10 : 
            #NOTHING ou ANVIL
                return action

            case 1 : 
            #BUBBLEGUM : à compléter
                return action

            case 2 : 
            #CAKE : à compléter
                return action
            
            case 3 : 
            #BOWLING : à compléter
                return action

            case 4 : 
            #ZIPPER : à compléter
                return action

            case 5 : 
            #PLUNGER : à compléter
                return action

            case 6 : 
            #SWITCH : à compléter
                return action

            case 7 : 
            #SWATTER : à compléter
                return action

            case 8 : 
            #RUBBERBALL : à compléter
                return action

            case 9 : 
            #PARACHUTE : à compléter
                return action

        return action

    def choose_action(self, obs) : 
        """
        Paramètres : obs
        Renvoie : action (dict), dictionnaire d'actions corrigé
        """
        action = super().choose_action(obs)
        action = observation_item(obs, action)
        return action
    
