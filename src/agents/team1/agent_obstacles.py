from .agent_speed import AgentSpeed
import numpy as np
from .agent_base import BONUS, OBSTACLES

class AgentObstacles(AgentSpeed) : 

    def __init__(self, env, path_lookahead=3): 
        super().__init__(env, path_lookahead)
        self.target_obstacle = None
        self.target_item = None

    def observation_next_item(self, obs, action) : 
        """
        Paramètres : obs, action (dict)
        Renvoie : action (dict), le dictionnaire d'actions corrigé après avoir pris en compte les items sur la piste
        """
        tab_bonus = [i for i in range(len(obs["items_type"])) if obs["items_type"][i] in BONUS]
        tab_obstacles = [i for i in range(len(obs["items_type"])) if obs["items_type"][i] in OBSTACLES]

        """
        for i in range(len(obs["items_type"])) :
            nextitem_type = obs["items_type"][i]
            #if nextitem_vector[2] < 17 and nextitem_vector[2] > 3 and abs(nextitem_vector[1]) < 10 : 
            if nextitem_type in BONUS : 
                action = self.take_bonus(obs, action)
            elif nextitem_type in OBSTACLES : 
                return action
                action = self.dodge_obstacle(obs, action)
        """
        for index in tab_obstacles :
            action = self.dodge_obstacle(obs, action, index)

        for index in tab_bonus : 
            action = self.take_bonus(obs, action, index)
        return action

    def dodge_obstacle(self, obs, action, index) : 
        """
        Paramètres : obs, action (dict), index
        Renvoie : action (dict), après avoir pris en compte le prochain obstacle (sauf si on a un SHIELD équipé)
        """
        if self.target_obstacle is None : 
            self.target_obstacle = index

        item_vector = obs["items_position"][index]
        if -1 < item_vector[2] < 1 or not ((abs(item_vector[0]) < 3.5) and (0 < item_vector[2] < 20) and (abs(item_vector[1]) < 10)): 
            self.target_obstacle = None

        if (self.target_obstacle == index):
            if (obs["attachment"] == 6 and obs["attachment_time_left"] > 2) : 
                #6 : BUBBLEGUM_SHIELD
                #à tester ici quand on aura un shield activé
                return action
    
            if item_vector[0] >= 0 : 
                action["steer"] = action["steer"] - 1
            else : 
                action["steer"] = action["steer"] + 1
        return action

    def take_bonus(self, obs, action, index) :
        """
        Paramètres : obs, action (dict), index
        Renvoie : action (dict), après avoir pris en compte le prochain bonus pour se diriger vers celui-ci
        """
        if self.target_item is None : 
            self.target_item = index

        item_vector = obs["items_position"][index]
        if item_vector[2] < 3 or not((abs(item_vector[0]) < 3) and (3 < item_vector[2] < 16) and (abs(item_vector[1]) < 10)) : 
            self.target_item = None

        next_node = obs["paths_end"][self.path_lookahead]
        node_item_gap_vector = next_node - item_vector #vecteur pour mesurer l'écart entre l'item et le prochain noeud
        #si l'écart est trop grand, on ne détourne pas du chemin de base

        if (self.target_item == index) and (node_item_gap_vector[2] <= (next_node[2] - 1)) and (self.target_obstacle is None) :
            """
            next_node = obs["paths_end"][0]
            node_item_gap_vector = next_node - item_vector
            if 0 < node_item_gap_vector[2] < next_node[2] : #optimisation ici ? 
            if abs(item_vector[0] - action["steer"]) < 0.1 :
                return action
            else : 
            """
            action["steer"] = item_vector[0]
        return action
        
    def choose_action(self, obs) : 
        """
        Paramètres : obs
        Renvoie : action (dict), dictionnaire d'actions corrigé après prise en compte des obstacles et bonus
        """
        action = super().choose_action(obs)
        action = self.observation_next_item(obs, action)
        return action
