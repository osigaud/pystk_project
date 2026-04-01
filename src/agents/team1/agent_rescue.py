from agents.kart_agent import KartAgent
import numpy as np

class AgentRescue(KartAgent) : 

    """Agent de secours chargé de détecter et faire reculer un kart qui est bloqué.
    
    Attributes:
        last_distance (float ou None): Dernière distance mesurée le long de la piste.
        block_counter (int): Nombre de frames consécutives sans progression significative.
        unblock_steps (int): Nombre d’actions restantes dans la séquence de déblocage.
        is_braking (bool): Indique si une phase de déblocage est en cours.
    """

    #Prendre le cas en compte où on est étourdi par un item dans is_blocked
    def __init__(self, env, conf, agent): 
        super().__init__(env)
        self.conf = conf
        self.agent = agent

        self.last_distance = None
        self.block_counter = 0
        self.unblock_steps = 0
        self.is_braking = False

    def is_blocked(self, obs):
        
        """Détecte si le kart est bloqué et met à jour le compteur interne.

        on se considère comme bloqué si la progression (`distance_down_track`) varie très peu pendant plusieurs frames, que le kart n’est pas en saut,
        et qu’il n’est pas affecté par certains items (ex: étourdissement).

        Args:
            obs (dict): Observations de l’environnement contenant notamment :
                - distance_down_track
                - jumping
                - attachment
        """

        distance_down_track = obs["distance_down_track"][0]
        attachment = obs["attachment"]
        if self.last_distance is None :
            self.last_distance = distance_down_track

        if abs(distance_down_track - self.last_distance) < self.conf.min_progress_threshold and distance_down_track > 5 and (obs["jumping"] == 0) :
            self.block_counter += 1
        else:
            self.block_counter = 0
            self.last_distance = distance_down_track

    def unblock_action(self, act):

        """Applique un recul pour tenter de débloquer le kart.

        Pendant un nombre limité de frames (`unblock_steps`), l’agent force
        une action de recul afin de sortir d’une situation de blocage.

        Args:
            act (dict): Action courante.

        Returns:
            dict: Action modifiée si une phase de déblocage est active,
                  sinon l’action originale.
        """

        if self.unblock_steps > 0 : 
            self.unblock_steps -= 1
            return {
                "acceleration" : 0, 
                "steer" : 0, 
                "brake" : True,
                "drift" : False,
                "nitro" : False,
                "rescue" : False,
                "fire" : False,
            }
        else : 
            self.is_braking = False
            return act

    def call_bird(self, obs) :

        """Observe si on tombe de la piste. Si oui, appelle l'oiseau de secours. Sinon, ne fait rien.

        Args: 
            obs (dict): Observations de l'environnement.

        Returns:
            boolean: True ou False selon si on a besoin d'un sauvetage ou non.
        """
        is_jumping = obs["jumping"]
        if is_jumping : 
            next_node_y = obs["paths_end"][0][self.conf.y]
            if next_node_y >= 2 : 
                return True
        return False
    
    def choose_action(self, obs):

        """Choisit une action et déclenche un déblocage ou un sauvetage si nécessaire.

        Étapes :
        1) Vérifie si le kart est bloqué.
        2) Récupère l’action normale (centre + obstacles).
        3) Si blocage est prolongé, lance un recul.
        4) Observe si besoin d'un sauvetage et agit en conséquence.

        Args:
            obs (dict): Observations de l’environnement.

        Returns:
            dict: Action finale appliquée au kart.
        """

        self.is_blocked(obs)
        action = self.agent.choose_action(obs)
                
        if self.block_counter > self.conf.block_counter_threshold :
            self.is_braking = True
            self.unblock_steps = self.conf.unblock_steps_default
        if self.is_braking : 
            action = self.unblock_action(action)
        action["rescue"] = self.call_bird(obs)
        return action
