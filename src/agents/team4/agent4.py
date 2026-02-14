import numpy as np
import random

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent
from .steering import Steering
from .rescue import RescueManager
from .speed import SpeedController
from .nitro import Nitro
from .drift import Drift
from .banana_detection import Banana


class Agent4(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "The Winners"
        self.steering = Steering()
        self.rescue = RescueManager()
        self.SpeedController=SpeedController()
        self.nitro = Nitro()
        self.drift = Drift()
        self.drift_cd = -1
        self.banana_dodge = Banana()
        self.dodge_side = 0
        self.dodge_timer = 0
        self.last_banana_z = float("inf")
        
    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []
        self.drift_cd = -1
        self.dodge_timer = 0
        self.dodge_side = 0
        self.last_banana_z = float("inf")
        self.rescue = RescueManager()

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        
        points = obs.get("paths_start",[]) # On récupère la liste des points
        
        if len(points) <= 2: # Si la longueur de la liste est inferieur à 2, on accèlère à fond (ligne d'arrivée proche)
            return {
                "acceleration": 1.0,
                "steer": 0.0,
                "brake": False,
                "drift": False,
                "nitro": False,
                "rescue":False,
                "fire": False,
            }
        
        target = points[2] # On récupère le deuxième point de la liste
        gx = target[0] # On récupère x, le décalage latéral
        gz = target[2] # On récupère z, la profondeur

        danger, b_x, b_z = self.banana_dodge.banana_detection(obs) # Appel de la fonction de detection

        if danger:

            #print("Danger "+str(b_x)) # Pour Debug, A retirer apres Test

            # Si la banane est à notre droite on va à gauche et vice-versa
            if b_x >=0:
                new_side = -1
            else:
                new_side = 1

            # Utilisation d'un compteur pour maintenir le cap d'esquive sur x frames
            if self.dodge_timer == 0:
                self.dodge_timer = 4
                self.dodge_side = new_side
                self.last_banana_z = b_z
            else:
                if new_side != self.dodge_side and b_z < self.last_banana_z:
                    self.dodge_side = new_side
                    self.dodge_timer = 4
                    self.last_banana_z = b_z
        
        is_dodging = False
        
        if self.dodge_timer >0:
            self.dodge_timer -= 1 # On decremente le compteur
            is_dodging = True # Variable representant l'etat "est en train d'esquiver"

            esquive = 3.0 # Constante permettant l'esquive

            gx += esquive * self.dodge_side # On ajoute l'esquive à x

            
        steering = self.steering.manage_pure_pursuit(gx,gz,6.0) # Appel à la fonction pure_pursuit en condition normale (pas de danger detecté)
        
        epsilon = 0.05
        
        road_straight = abs(points[2][0]) < 0.8

        # Pour eviter les vibrations, si on est sur une ligne droite, on met le steering à 0
        if road_straight and abs(steering) <= epsilon:
            steering = 0.0
        
        # Au depart on avance tout droit pour eviter de se cogner contre les adversaires
        if obs['distance_down_track'] <= 2:
            steering = 0.0

        distance = float(obs.get("distance_down_track", [0.0])[0])
        vel = obs.get("velocity", [0.0, 0.0, 0.0])
        speed = float(vel[2])
        energy = float(obs.get("energy", [0.0])[0])
        drift = False
        """
        if not danger and not is_dodging:    
            should_drift,drift_steer = self.drift.manage_drift(steering,distance)
            if should_drift and self.drift_cd == -1:
                self.drift_cd = 8
                drift = True
                
            elif self.drift_cd > 0:
                self.drift_cd -= 1
                drift = True
            else:
                self.drift_cd = -1
                drift = False
        else :
            drift = False
            self.drift_cd = -1"""
        
        
        brake = False
        acceleration, brake = self.SpeedController.manage_speed(steering,obs) # Appel à la fonction gerer_vitesse
        #print("speed_out:", self.SpeedController.manage_speed(steering, obs))
        
        nitro = False
        nitro = self.nitro.manage_nitro(steering,energy,obs) # Appel à la fonction gerer_nitro
        """if (drift == True):
            nitro = False"""


        if(self.rescue.is_stuck(distance,speed)): # Si on est bloque, on appelle la fonction rescue
            return self.rescue.sortir_du_mur(steering) 
        
        if is_dodging: # Si on est en train d'esquiver
            
            drift = False       # Pas de drift
            nitro = False       # Pas de nitro
        
        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": brake,
            "drift": drift,
            "nitro": nitro,
            "rescue":False,
            "fire": False,
        }
        return action
