from .steering import Steering
from omegaconf import DictConfig

class AgentEdge:
    """
    Module Agent Expert Edge : Empêche la sortie de piste en surveillant la distance par rapport au centre.
    """
    def __init__(self,config : DictConfig ,config_pilote : DictConfig):

        """Initialise les variables d'instances de l'agent expert"""
     
        self.conf = config
        """@private"""
        self.pilotage = Steering(config_pilote)
        """@private"""

    def reset(self) -> None:

        """Réinitialise les variables d'instances de l'agent expert"""
        
        self.pilotage.reset()

    def choose_action(self, obs : dict, gx : float, gz : float) -> tuple[bool,dict]:
        """
        Analyse la position latérale et corrige si nécessaire

        Args:

            obs(dict) : Les données de télémétrie fournies par le simulateur.
            gx(float) : Décalage latéral de la cible.
            gz(float) : Profondeur de la cible.

        Returns:

            bool : Variable affirmant ou non la nécessite de se réaxer.
            dict : Dictionnaire d'actions à réaliser pour se réaxer.

        """
        # Récupération des données de piste
        cpd_raw = obs.get("center_path_distance", 0.0)
        center_path_distance = cpd_raw[0]
        
        pw_raw = obs.get("paths_width", [10.0, 0.0, 0.0])
        limit_path = pw_raw[0] / 2
        limit_path = limit_path[0]
        
        # Calcul de la marge de sécurité (Distance bord <-> Kart)
        marge_securite = limit_path - abs(center_path_distance)
        #print((limit_path - abs(center_path_distance))[0])
        
        # Vérification de la sortie de piste imminente
        if self.conf.epsilon_limite_min <= marge_securite <= self.conf.epsilon_limite_max :

            #print(f"Limite de sortie = {marge_securite}")
            
            #print(gx)
            #print(center_path_distance)
            
            # ATTENTION LOGIQUE INVERSEE POUR CENTER PATH, si > 0 l'agent se situe à droite de la piste
            """if center_path_distance > 0:
                print("Esquive Vers la gauche")
                gx -= self.conf.decalage_lateral
            else:
                print("Esquive Vers la droite")
                gx += self.conf.decalage_lateral"""
            
            # On réduit l'accélération pour reprendre de l'adhérence
            new_accel = self.conf.new_accel

            steer = self.pilotage.manage_pure_pursuit(gx,gz,self.conf.gain)

            action = {
            "acceleration": new_accel,
            "steer": steer,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue":False,
            "fire": False,
            } 
            
            return True, action

        # Pas de danger, on laisse le pilote principal gérer
        return False, {}