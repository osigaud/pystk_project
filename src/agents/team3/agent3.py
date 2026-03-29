import math
import numpy
from agents.kart_agent import KartAgent

#On importe les fichiers wrappers steer, speed, fire et rescue
from .steer import Steer
from .speed import Speed
from .fire import Fire
from .rescue import Rescue

# kart_skin = ['adiumy', 'sara_the_racer', 'amanda', 'tux', 'beastie', 'emule', 'gavroche', 'gnu', 'hexley', 'kiki', 'konqi', 'nolok', 'pidgin', 'puffy', 'sara_the_wizard', 'suzanne', 'wilber', 'xue']

class Agent3(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.name = "Team L'eclair"
        self.isEnd = False
        self.path_lookahead = path_lookahead
        
        """
        Les wrappers :
        - Steer qui contrôle le pilotage du kart 
        ainsi que les esquives de peaux de bananes et des bubbles gums
        - Speed qui contrôle la vitesse du kart, les noeuds
        ainsi que l'usage du drift et du nitro
        - Fire permet d'utiliser les items collectés
        notre agent utilise l'angle afin de viser le kart adverse devant nous
        - Rescue permet de secourir notre kart si le kart est bloqué dans un mur
        """
        
        self.base_pilot = Steer(env)
        self.speed_pilot = Speed(env, self.base_pilot)
        self.fire_pilot = Fire(env, self.speed_pilot)
        self.rescue = Rescue(env, self.fire_pilot)
        self.skin = 'adiumy'
        
    def reset(self):
        self.obs, _ = self.env.reset()
        self.rescue.reset()
    
    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        return self.rescue.choose_action(obs)
