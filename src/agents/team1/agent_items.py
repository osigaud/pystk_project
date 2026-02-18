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
            case 0 | 10 : 
            #NOTHING ou ANVIL
                return action

            case 1 : 
            #BUBBLEGUM : à compléter
                return action

            case 2 : 
            #CAKE : à compléter
                premier_kart = obs["karts_position"][0]
                if premier_kart[2]<0:
                    action["fire"] = 0
                    return action 
                for kart in obs["karts_position"]:
                    if kart[2]>=0 and kart[2]<60:
                       action["fire"] = 1
                       return action
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
                premier_kart = obs["karts_position"][0]
                if premier_kart[2] > 0:
                    action["fire"] = 1
                return action

            case 9 : 
            #PARACHUTE : à compléter
                premier_kart = obs["karts_position"][0]
                if premier_kart[2] > 0:
                    action["fire"] = 1
                return action


        return action

        


    def use_nitro(self, obs, act):
        nit = obs["energy"]
        virage_serre = False
        if nit > 0.05 :
            act["nitro"] = True
        return act 

    def choose_action(self, obs) : 
        """
        Paramètres : obs
        Renvoie : action (dict), dictionnaire d'actions corrigé
        """
        action = super().choose_action(obs)
    
        action = self.observation_item(obs, action)
        
        action = self.use_nitro(obs, action)
        return action
    
