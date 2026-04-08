from agents.kart_agent import KartAgent
import numpy as np

class AgentCenter(KartAgent):

    """Agent de base chargé de maintenir le kart au centre de la piste.
    
    Attributes :
    -dist (float): Distance seuil acceptée avant de considérer que l'on dévie du centre
    -ajust (float): Valeur d'ajustement pour corriger la trajectoire
    """


    def __init__(self, env, conf, path_lookahead=3):
        super().__init__(env)
        self.conf = conf
        self.dist = self.conf.dist
        self.ajust = self.conf.ajust
        self.path_lookahead = path_lookahead


    

    def observation_next_item(self, obs, action) : 
        """Analyse les items visibles (bonus/obstacles) et corrige l'action soit en s'en approchant ou soit en esquivant.

        1. repère les indices des items bonus et obstacles via `obs["items_type"]`
        2. applique d'abord l'évitement des obstacles
        3. puis (si possible) l'alignement vers un bonus

        Args:
            obs (dict): Observations de l’environnement. Clés utilisées typiquement :
                - items_type (list[int] | list[str]): type de chaque item détecté.
                - items_position (list[array]): vecteur position de chaque item (x, y, z) dans le repère du kart.
            action (dict): Dictionnaire d'action courant (au minimum "steer").

        Returns:
            dict: Action corrigée après prise en compte des bonus et obstacles.
        """
        for i in range(len(obs["items_type"])) :
            vecteur_item = obs["items_position"][i]
            type_item = obs["items_type"][i]
            if (2 < vecteur_item[self.conf.z] < 15) and (abs(vecteur_item[self.conf.y]) < 1) :
                if (abs(vecteur_item[self.conf.x]) < 1.5) and type_item in self.conf.obstacles : 
                    action = self.dodge_obstacle(obs, action, i)
                    return action
                #elif (abs(vecteur_item[self.conf.x]) < 3) and type_item in self.conf.bonus: 
                    #action = self.take_bonus(obs, action, i)
        return action

    def dodge_obstacle(self, obs, action, index) : 
        """Évite un obstacle donné (sauf si un shield est actif).

        Conserve une cible (`target_obstacle`) pour éviter de changer
        d'obstacle ciblé à chaque frame. Si l'obstacle n'est plus pertinent
        (trop proche, hors zone, ou autre), la cible est remise a None.

        Args:
            obs (dict): Observations (utilise `items_position`, `attachment`, `attachment_time_left`).
            action (dict): Action courante (modifie "steer").
            index (int): Index de l'obstacle dans `obs["items_type"]` / `obs["items_position"]`.

        Returns:
            dict: Action corrigée (steer modifié pour dévier de l'obstacle).
        """
        vecteur_item = obs["items_position"][index]
        next_node = obs["paths_end"][self.path_lookahead]
        sign_next_node = -1 if next_node[self.conf.x] < 0 else 1
        if abs(next_node[self.conf.x]) > 10 : #si on est sur un virage
            action["steer"] += 1 * sign_next_node
        else :
            if vecteur_item[self.conf.x] >= 0 : 
                action["steer" ] -= 1
            else : 
                action["steer"] += 1
        action["steer"] = np.clip(action["steer"], -1, 1) 
        return action

    def take_bonus(self, obs, action, index) :
        """Se dirige vers un bonus (item) s'il n'y a pas d'autre priorité et s'il est pertinent de le récupérer.

        Même principe que dodge obstacles on conserve une cible pour éviter de changer de direction à chaque frame.

        Args:
            obs (dict): Observations (utilise `items_position`, `paths_end`).
            action (dict): Action courante (modifie "steer").
            index (int): Index du bonus dans `obs["items_type"]` / `obs["items_position"]`.

        Returns:
            dict: Action corrigée (steer orienté vers l'item si conditions remplies).
        """
        vecteur_item = obs["items_position"][index]
        next_node = obs["paths_end"][self.path_lookahead]
        #si l'item n'est pas dans le même sens que le prochain virage
        if vecteur_item[self.conf.x] * next_node[self.conf.x] < 0 : 
            return action
        
        steer = vecteur_item[self.conf.x]
        steer = np.clip(steer, -1, 1)
        action["steer"] = steer
        return action




    def path_ajust(self, obs, action):
        """
        Ajuste la direction du kart pour suivre le centre de la piste.

        Args:
            act (dict): Dictionnaire des actions du kart (ex: {"steer": float}).
            obs (dict): Observations de l’environnement contenant notamment
                    "paths_end" et "center_path_distance".

        Returns:
            dict: Dictionnaire des actions corrigé avec une valeur de
                "steer" comprise entre -1 et 1.
        """
        steer = action["steer"]
        center = obs["paths_end"][2]
        if (center[self.conf.z] > 20 and abs(obs["center_path_distance"]) < 3) : 
            steer = 0
        elif abs(center[self.conf.x]) > self.dist : 
            steer += self.ajust * center[0]
        action["steer"] = np.clip(steer, -1, 1)
        return action
    
    def choose_action(self, obs):
        """
        Applique une correction de trajectoire.

        Args:
            obs (dict): Observations de l’environnement.

        Returns:
            dict: Dictionnaire d’action corrigé.
    """
        action = {
            "acceleration": 0,
            "steer": 0,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue": False,
            "fire": False,
        }
        action = self.path_ajust(obs, action)
        action = self.observation_next_item(obs, action)
        return action
