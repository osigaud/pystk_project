from agents.kart_agent import KartAgent
import numpy as np

class AgentSpeed(KartAgent):
    
    """Agent qui adapte la vitesse en fonction de la forme de la piste dans les prochaines secondes (ligne droite ou virage?).

    Cet agent hérite de AgentCenter (qui gère le maintien au centre de la piste)
    et ajoute un comportement de gestion de l'accélération selon les
    segments de piste devant le kart (ligne droite vs virage serré).

    Attributes:
        ecartpetit (float): Seuil en dessous duquel on considère que l'écart de direction
            est faible (ligne droite).
        ecartgrand (float): Seuil à partir duquel l'écart est grand (virage serré).
        msapetit (float): Seuil bas sur obs["max_steer_angle"] pour moduler l'accélération.
        msagrand (float): Seuil haut sur obs["max_steer_angle"] pour moduler l'accélération.
    """

    def __init__(self, env, conf, agent, path_lookahead=3):
        super().__init__(env)
        self.conf = conf
        self.agent = agent
        self.path_lookahead = path_lookahead
        
    def detecter_virage(self, obs):

        """Analyse la piste devant le kart et classe la situation selon si c'est un virage ou non.

        La méthode inspecte jusqu'à `path_lookahead`(on choisi 3) segments (paths_start/end) et
        estime un "écart" entre la direction des segments et le vecteur `obs["front"]`.
        Si un segment proche correspond à un écart élevé, on detecte un virage serré.

        Args:
            obs (dict): Observations de l’environnement. Clés typiques utilisées :
                - paths_start (list/array): points de début des segments.
                - paths_end (list/array): points de fin des segments.
                - front (array): direction actuelle du kart (vecteur).
                - paths_distance (list): distances latérales  associees aux segments.

        Returns:
            bool : virage_serre
        """

        virage_serre = False
        nbsegments = min(self.path_lookahead, len(obs["paths_start"]))
        for i in range(nbsegments):
            direction_segment = obs["paths_end"][i] - obs["paths_start"][i]
            diff_direction = direction_segment - obs["front"]
            ecart_direction = float(np.linalg.norm(diff_direction))
            distance_segment = abs(obs["paths_distance"][i][0] - obs["paths_distance"][0][0])
                
            if ecart_direction >= self.conf.ecartgrand and distance_segment < self.conf.dist_segment:
                virage_serre = True
      
        return virage_serre
        
    def ajuster_acceleration(self, virage_serre, act, obs):

        """Modifie l'action `act` en fonction du contexte.

        Ajuste `act["acceleration"]` selon :
        - le type de trajectoire ("ligne droite" / "virage serre")
        - `obs["max_steer_angle"]` (indicateur de la difficulté du virage)
        - une pente éventuelle dans laquelle il faut accélerer(via segdirection[1])

        Args:
            virage serre (bool): Résultat de `analyse` ("ligne droite" ou "virage serre").
            act (dict): Action courante (doit contenir "acceleration").
            obs (dict): Observations (doit contenir "max_steer_angle", "paths_start/end"...).

        Returns:
            dict: Action corrigé (accélération bornée via `gap`).
        """

        act["acceleration"] = max(act["acceleration"], 1)
        max_steer_angle = obs["max_steer_angle"]

        # ligne droite
        if not virage_serre:
            act["acceleration"] = self.conf.accel_ligne_droite

            direction_segment = obs["paths_end"][0] - obs["paths_start"][0]
            if direction_segment[1] > 0.05:
                act["acceleration"] = np.clip(act["acceleration"], 0.1, 1)      #self.limit(act["acceleration"] + 0.2)
            return act

        # virage serré
        if max_steer_angle <= self.conf.max_steer_angle_petit:
            acceleration_freinee = act["acceleration"] - self.conf.frein_virage
            act["acceleration"] = np.clip(acceleration_freinee, 0.1, 1)

        elif max_steer_angle >= self.conf.max_steer_angle_grand:
            acceleration_boostee = act["acceleration"] + self.conf.accel_virage
            act["acceleration"] = np.clip(acceleration_boostee, 0.1, 1)

        direction_segment = obs["paths_end"][0] - obs["paths_start"][0]
        if direction_segment[1] > 0.05:
            act["acceleration"] = np.clip(act["acceleration"], 0.1, 1) 

        return act
  
    def choose_action(self, obs):
        act = self.agent.choose_action(obs)
        virage_serre = self.detecter_virage(obs)
        action_ajustee = self.ajuster_acceleration(virage_serre, act, obs)
        return action_ajustee

