from agents.kart_agent import KartAgent
import numpy as np
BUBBLEGUM = 1
CAKE = 2
BOWLING = 3
ZIPPER = 4
PLUNGER = 5
SWITCH = 6
SWATTER = 7
RUBBERBALL = 8
PARACHUTE = 9


class AgentItems(KartAgent) : 

    """Agent qui gère l'utilisation des objets et du nitro."""

    def __init__(self, env, conf, agent) :
        super().__init__(env)
        self.conf = conf
        self.agent = agent 
    
    def observation_item(self, obs, action) : 
        """Détermine si l'objet que nous avons doit être utilisé.

        - certains objets sont utilisés immédiatement,
        - d'autres seulement si un adversaire est devant,
        - d'autres encore si un adversaire est suffisamment proche dans un rayon autour du kart.

        Args:
            obs (dict): Observations de l'environnement. Clés utilisées :
                - powerup : objet actuellement détenu
                - karts_position : positions relatives des autres karts
            action (dict): Action courante à modifier.

        Returns:
            dict: Action corrigée avec la clé `fire` mise à jour.
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

        """Active le nitro si le niveau d'énergie est suffisant.

        Vérifie la quantité d'énergie disponivble dans
        `obs["energy"]`. Si elle dépasse un certain seuil, l'action
        `nitro` est activée.

        Args:
            obs (dict): Observations de l'environnement. Clé utilisée :
                - energy : quantité d'énergie disponible
            act (dict): Action courante à modifier.

        Returns:
            dict: Action corrigée avec la clé `nitro` éventuellement activée.
        """

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
    
