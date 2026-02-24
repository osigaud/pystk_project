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
        
        action["fire"] = False        

        match current_item : 
            case 0 | 10 : 
            #NOTHING ou ANVIL
                return action

            case 1 : 
            #BUBBLEGUM : à compléter
                action ["fire"] = True
                return action

            case 2 : 
            #CAKE : à compléter
                premier_kart = obs["karts_position"][0]
                if premier_kart[2]<0:
                    action["fire"] = False
                    return action 
                for kart in obs["karts_position"]:
                    if kart[2]>=0 and kart[2]<60:
                       action["fire"] = True
                       return action
                return action
            
            case 3 : 
            #BOWLING : à compléter
                premier_kart = obs["karts_position"][0]
                if premier_kart[2]<0:
                    action["fire"] = False
                if self.target_item != None : 
                    action ["fire"] = True
                for kart in obs["karts_position"]:
                    if kart[2]>=0 and kart[2]<=25:         #optimiser valeurs
                        if abs(kart[0]) <= 3:
                            action["fire"] = True                
                return action

            case 4 : 
            #ZIPPER : à compléter
                if virage_serre = false and self.target_obstacle = None:
                    action["fire"] = True               
                return action

            case 5 : 
            #PLUNGER : à compléter
                premier_kart = obs["karts_position"][0]
                if premier_kart[2]<0:
                    action["fire"] = False
                for kart in obs["karts_position"]:
                    if kart[2]>=0 and kart[2]<25:
                        if abs(kart[0]) <= 3:
                            action["fire"] = True 
                return action

            case 6 : 
            #SWITCH : à compléter
                if self.target_item != None:
                    action["fire"] = False
                else: 
                    action["fire"] = True
                return action

            case 7 : 
            #SWATTER : à compléter
                for kart in obs["karts_position"]:
                    if abs(kart[2])<=10 and abs(kart[0])<=10 and abs(kart[1])<=5:
                        action["fire"] = True
                return action

            case 8 : 
            #RUBBERBALL : à compléter
                premier_kart = obs["karts_position"][0]
                if premier_kart[2] > 0:
                    action["fire"] = True
                return action

            case 9 : 
            #PARACHUTE : à compléter
                premier_kart = obs["karts_position"][0]
                if premier_kart[2] > 0:
                    action["fire"] = True
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
    
