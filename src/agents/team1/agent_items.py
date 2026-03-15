from agents.kart_agent import KartAgent
import numpy as np
case 1 : BUBBLEMGUM
case 2 : CAKE
case 3 : BOWLING
case 4 : ZIPPER
case 5 : PLUNGER
case 6 : SWITCH
case 7 : SWATTER
case 8 : RUBBERBALL
case 9 : PARACHUTE


class AgentItems(KartAgent) : 
    def __init__(self, env, conf, agent) :
        super().__init__(env)
        self.conf = conf
        self.agent = agent 
    
    def observation_item(self, obs, action) : 
        """
        Paramètres : obs, action (dict)
        Renvoie : action (dict), dictionnaire d'actions corrigé après prise en compte des objets tenus
        """
        current_item = obs["powerup"]        
        action["fire"] = False        

        if current_item == BUBBLEGUM :
            #BUBBLEGUM : à compléter
            action["fire"] = True
            return action

        if current_item == CAKE :
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
            
        if current_item == BOWLING :
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

        if current_item == ZIPPER : 
            #ZIPPER : à compléter
            #if virage_serre = false and self.target_obstacle = None:
            action["fire"] = True         	      
            return action

        if current_item == PLUNGER :
            #PLUNGER : à compléter
            premier_kart = obs["karts_position"][0]
            if premier_kart[2]<0:
                action["fire"] = False
            for kart in obs["karts_position"]:
                if kart[2]>=0 and kart[2]<25:
                    if abs(kart[0]) <= 3:
                        action["fire"] = True 
            return action

        if current_item == SWITCH :
            #SWITCH : à compléter
            if self.target_item != None:
                action["fire"] = False
            else: 
                action["fire"] = True
            return action

        if current_item == SWATTER :
            #SWATTER : à compléter
            for kart in obs["karts_position"]:
                if abs(kart[2])<=10 and abs(kart[0])<=10 and abs(kart[1])<=5:
                    action["fire"] = True
            return action

        if current_item == RUBBERBALL :
            #RUBBERBALL : à compléter
            premier_kart = obs["karts_position"][0]
            if premier_kart[2] > 0:
                action["fire"] = True
            return action

        if current_item == PARACHUTE :
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
        action = self.agent.choose_action(obs)
        action = self.observation_item(obs, action)
        action = self.use_nitro(obs, action)
        return action
    
