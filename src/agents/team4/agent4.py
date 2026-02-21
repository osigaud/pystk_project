from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent
from .steering import Steering
from .rescue import RescueManager
from .speed import SpeedController
from .nitro import Nitro
from .drift import Drift
from .banana_detection import Banana
from .esquive_adv import EsquiveAdv



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
        self.esquive_adv = EsquiveAdv()
        self.banana_dodge = Banana()
        self.dodge_side = 0
        self.dodge_timer = 0
        self.last_banana_z = float("inf")
        
    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []
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
            
        is_dodging = False
        
        if self.dodge_timer >0:
            self.dodge_timer -= 1 # On decremente le compteur
            is_dodging = True # Variable representant l'etat "est en train d'esquiver"

            esquive = 3.0 # Constante permettant l'esquive

            gx += esquive * self.dodge_side # On ajoute l'esquive à x
        else:
            danger_adv, a_x, a_z = self.esquive_adv.esquive_adv(obs)
            
            if danger_adv:
                if a_x >= 0:
                    gx -= 2.0 # On se décale à gauche 
                    gx += 2.0 # On se décale à droite

            
        steering = self.steering.manage_pure_pursuit(gx,gz,7.0) # Appel à la fonction pure_pursuit en condition normale (pas de danger detecté)
        
        epsilon = 0.05
        
        road_straight = abs(points[2][0]) < 0.8

        # Pour eviter les vibrations, si on est sur une ligne droite, on met le steering à 0
        if road_straight and abs(steering) <= epsilon:
            steering = 0.0
        
        distance = float(obs.get("distance_down_track", [0.0])[0])
        vel = obs.get("velocity", [0.0, 0.0, 0.0])
        speed = float(vel[2])
        energy = float(obs.get("energy", [0.0])[0])
    
        brake = False
        acceleration, brake = self.SpeedController.manage_speed(steering,speed,drift) # Appel à la fonction gerer_vitesse
        #print("speed_out:", self.SpeedController.manage_speed(steering, obs))
        
        nitro = False
        nitro = self.nitro.manage_nitro(steering,energy,obs) # Appel à la fonction gerer_nitro
       
        if(self.rescue.is_stuck(distance,speed)): # Si on est bloque, on appelle la fonction rescue
            return self.rescue.sortir_du_mur(steering)

        # Au depart on avance tout droit pour eviter de se cogner contre les adversaires
        if obs['distance_down_track'] <= 2:
            steering = 0.0
            acceleration = 1.0
             
        if is_dodging: # Si on est en train d'esquiver
            
            drift = False       # Pas de drift
            nitro = False       # Pas de nitroer
            
        fire_items = False
        karts_pos = obs.get("karts_position",[])
        #attachment_id = obs.get("attachment",0)
        if len(karts_pos)>0:
            for ennemis in karts_pos:
                e_x = ennemis[0]
                e_z = ennemis[2]
                seuil = 1 + (e_z/15.0)      # item comme la balle de bowling pour lancer le mieux possible sur l'adversaire selon la distance qui nous le sépare
                if 2.0 < e_z < 15.0 and abs(e_x) < seuil:
                    #print(attachment_id)
                    fire_items = True
                    break
                elif -15.0 < e_z < -2.0:
                    #print(attachment_id)
                    fire_items = True
                    break
        
        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": brake,
            "drift": False,
            "nitro": nitro,
            "rescue":False,
            "fire": fire_items,
        }
        return action
