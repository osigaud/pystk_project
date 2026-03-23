from agents.kart_agent import KartAgent
import numpy as np

from agents.team1.agent_speed import AgentSpeed

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

    def is_bonus_close(self, obs) :
        """Renvoie True si on est très proche d'une boîte cadeau, False sinon"""
        next_item = obs["items_position"][0]
        if obs["items_type"][0] == 0 : #BONUS BOX
            if abs(next_item[self.conf.x]) < 2 and next_item[self.conf.z] < 3 and abs(next_item[self.conf.y]) < 3 :
                return True
        return False
    
    def observation_item(self, obs, action) : 
        """Détermine si l'objet que nous avons doit être utilisé.

        - certains objets sont utilisés immédiatement,
        - d'autres seulement si un adversaire est devant,
        - d'autres encore si un adversaire est suffisamment proche dans un rayon autour du kart.

        Args:
            obs (dict): Observations de l'environnement. Clés utilisées :
                - powerup_type : objet actuellement détenu
                - karts_position : positions relatives des autres karts
            action (dict): Action courante à modifier.

        Returns:
            dict: Action corrigée avec la clé `fire` mise à jour.
        """
        current_item = obs["powerup_type"]        
        action["fire"] = False        

        if current_item == BUBBLEGUM :
            action["fire"] = True
            return action

        if current_item == CAKE :
            premier_kart = obs["karts_position"][0]
            if premier_kart[self.conf.z]<0:
                action["fire"] = False
                return action 
            for kart in obs["karts_position"]:
                if kart[self.conf.z] >= 0 and kart[self.conf.z] < 80:
                   action["fire"] = True
                   return action
            return action
            
        if current_item == BOWLING :
            premier_kart = obs["karts_position"][0]
            if premier_kart[self.conf.z]<0:
                action["fire"] = False
            if self.is_bonus_close(obs) : 
                action ["fire"] = True
            for kart in obs["karts_position"]:
                if kart[self.conf.z]>=0 and kart[self.conf.z]<=25:         #optimiser valeurs
                    if abs(kart[self.conf.x]) <= 3:
                        action["fire"] = True                
            return action

        if current_item == ZIPPER : 
            #if virage_serre = false and self.target_obstacle = None:
            action["fire"] = True         	      
            return action

        if current_item == PLUNGER :
            premier_kart = obs["karts_position"][0]
            if premier_kart[self.conf.z]<0:
                action["fire"] = False
            for kart in obs["karts_position"]:
                if kart[self.conf.z]>=0 and kart[self.conf.z] < 50:
                    if abs(kart[self.conf.x]) <= 3:
                        action["fire"] = True 
            return action

        if current_item == SWITCH :
            if self.is_bonus_close(obs):
                action["fire"] = False
            else: 
                action["fire"] = True
            return action

        if current_item == SWATTER :
            for kart in obs["karts_position"]:
                if abs(kart[self.conf.z]) <= 9 and abs(kart[self.conf.x]) <= 9 and abs(kart[self.conf.y])<=5:
                    action["fire"] = True
            return action

        if current_item == RUBBERBALL :
            premier_kart = obs["karts_position"][0]
            if premier_kart[self.conf.z] > 0:
                action["fire"] = True
            return action

        if current_item == PARACHUTE :
            premier_kart = obs["karts_position"][0]
            if premier_kart[self.conf.z] > 0:
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
        virage_serre = AgentSpeed.detecter_virage(self.conf, obs)
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
