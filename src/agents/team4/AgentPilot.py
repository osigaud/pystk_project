from .steering import Steering
from .speed import SpeedController
from .AgentItems import AgentItems
from .AgentNitro import AgentNitro


class AgentPilot:

    def __init__(self, config,config_steering,config_speed,config_items,config_nitro,path_lookahead):
        
        
        self.c = config
        self.steering = Steering(config_steering)
        self.speedcontroller = SpeedController(config_speed)
        self.expert_items = AgentItems(config_items,config_steering)
        self.path_lookahead = path_lookahead
        self.expert_nitro = AgentNitro(config_nitro)


    def reset(self):
        
        self.steering.reset()
        self.speedcontroller.reset()
        self.expert_items.reset()
        self.expert_nitro.reset()

    
    def get_steering(self,obs):
        
        points = obs.get("paths_start",[])
        target = points[self.path_lookahead] # On récupère le x-ème point de la liste defini par la variable de classe
        gx = target[0] # On récupère x, le décalage latéral
        gz = target[2] # On récupère z, la profondeur
        gain_volant = self.c.default_gain
        steering = self.steering.manage_pure_pursuit(gx,gz,gain_volant)

        return steering

    def choose_action(self,obs : dict) -> dict:

        points = obs.get("paths_start",[]) # On récupère la liste des points

        if obs['distance_down_track'] <= self.c.seuil_distance:
            action = {
            "acceleration": 1.0,
            "steer": 0.0,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue":False,
            "fire": False,
            }
            return action
        
        if len(points) <= self.c.seuil_lenpoints: # Si la longueur de la liste est inferieur à 2, on accèlère à fond (ligne d'arrivée proche)
            action = {
                "acceleration": 1.0,
                "steer": 0.0,
                "brake": False,
                "drift": False,
                "nitro": True,
                "rescue":False,
                "fire": False,
            }
            return action
        

        steering = self.get_steering(obs)
        acceleration, brake = self.speedcontroller.manage_speed(obs) # Appel à la fonction gerer_vitesse
        nitro = self.expert_nitro.manage_nitro(obs,steering) # Appel à la fonction manage_nitro

        epsilon = self.c.epsilon
        road_straight = abs(points[2][0]) < self.c.seuil_road_straight
        if road_straight and abs(steering) <= epsilon:
            steering = 0.0

        fire, steering = self.expert_items.use_items(obs, steering)
        
        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": brake,
            "drift": False,
            "nitro": nitro,
            "rescue":False,
            "fire": fire,
        }
        return action