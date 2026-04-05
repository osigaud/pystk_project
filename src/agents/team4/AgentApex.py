from .steering import Steering
from omegaconf import DictConfig
from utils.track_utils import compute_curvature
import numpy as np

class AgentApex:
    """
    Expert Corde : Applique la trajectoire Racing Line (Out-In-Out)
    basée sur la courbure de la piste.
    """
    def __init__(self, config : DictConfig, config_steering: DictConfig, path_lookahead : int) -> None:
        
        """Initialise les variables d'instances de l'agent expert"""
        
        self.config = config
        """@private"""
        self.pilotage = Steering(config_steering)
        """@private"""
        self.path_lookahead = path_lookahead
        """@private"""
        self.state = "IDLE"  # Etats : IDLE, PREPA (Out), APEX (In)
        """@private"""
        self.side = 0        # -1 pour Gauche, 1 pour Droite
        """@private"""
        self.timer = 0       # Sécurité pour ne pas rester bloqué dans un état
        """@private"""
    
    def reset(self) -> None:
        
        """Réinitialise les variables d'instances de l'agent expert"""
        
        self.state = "IDLE"
        self.side = 0
        self.timer = 0
        self.pilotage.reset()

    def choose_action(self, obs: dict, acceleration: float) -> tuple[bool, dict]:

        """
        
        Gère la logique de prise de corde selon le modèle OUT-IN-OUT

        Args:
                
            obs(dict) : Les données de télémétrie fournies par le simulateur.
            acceleration(float) : Accéleration de l'agent.

        Returns:
            
            bool : Permet de confirmer le démarrage de la machine à etats pour prendre les cordes.
            dict : Le dictionnaire d'actions à réaliser pour prendre une corde.
        
        """
        
        # Récupération des points
        points = obs.get('paths_start', [])
        if len(points) < 10:
            return False, {}

        # Anticipation d'un virage et virage actuel
        curv_now = np.clip(compute_curvature(points[0:3]), -5.0, 5.0)
        curv_far  = np.clip(compute_curvature(points[5:10]), -5.0, 5.0)
        #print(f"curv_now={curv_now:.4f} curv_far={curv_far:.4f}")
        
        #Calcul de la limite avec une marge
        pw = obs.get('paths_width', [10.0])[0]
        limite_securite = ((pw / 2) * self.config.marge_secu)[0] 
        
        # Récupération du décalage latéral et de la profondeur
        target = points[self.path_lookahead] 
        gx, gz = target[0], target[2]

        # --Gestion des Etats--
        
        # Initialisation : Si inactif et un virage assez serre
        if self.state == "IDLE" and abs(curv_far) > self.config.seuil_prepa:
            self.state = "PREPA"
            # Si angle < 0, virage à droite, donc on prend l'extérieur gauche et vice-versa
            self.side = -1 if curv_far < 0 else 1
            self.timer = self.config.timer_prepa 

        # Preparation : Prise de l'exterieur
        if self.state == "PREPA":
            # On applique notre decalage
            gx += limite_securite * self.side
            #print(f"--- PREPA : Extérieur {'Gauche' if self.side < 0 else 'Droit'}")
            
            # Si le timer est fini ou l'angle actuel est assez fort, on déclenche la prise de la corde
            if abs(curv_now) > self.config.seuil_apex or self.timer <= 0:
                self.state = "APEX"
                self.side = -self.side # Inversion pour aller à l'intérieur
                self.timer = self.config.timer_apex
            self.timer -= 1

        # Finalisation : Prise de la corde
        elif self.state == "APEX":
            
            # Application du décalage
            gx+= (limite_securite * self.side)/self.config.reduction_decalage
            
            #print(f"--- APEX : Intérieur {'Gauche' if self.side < 0 else 'Droit'}")
            
            # Si le virage ou le timer est termine, on donne la main au pilote de base
            if abs(curv_now) < self.config.seuil_idle or self.timer <= 0:
                self.state = "IDLE"
                return False, {}
            self.timer -= 1

        # Actions à faire si nous ne sommes pas dans l'étape d'initialisation
        if self.state != "IDLE":
            # Appel de la fonction steering
            steering = self.pilotage.manage_pure_pursuit(gx, gz, self.config.gain)
            action = {
                "acceleration": acceleration,
                "steer": steering,
                "brake": False, "drift": False, "nitro": False, "rescue": False, "fire": False
            }
            return True, action

        return False, {}