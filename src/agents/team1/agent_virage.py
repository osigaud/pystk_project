# Attributs : self.intensite_precedente self.seuil_intensite self.seuil_delta
from agents.kart_agent import KartAgent
import numpy as np

class AgentVirage(KartAgent):

    def __init__(self, env, conf ):
        super().__init__(env)
        self.intensite_precedente = None
        self.conf = conf
        self.seuil_intensite = self.conf.seuil_intensite
        self.seuil_delta = self.conf.seuil_delta
        self.steer1 = self.conf.steer1
        self.steer2 = self.conf.steer2
        self.acceleration = self.conf.acceleration
        self.brake = self.conf.brake

    def calcul_vecteur(self, v1, v2):
        nv_x = v2[0] - v1[0]
        nv_z = v2[2] - v1[2]

        return np.array([nv_x, nv_z], dtype=float)


    def direction_virage(self, vecteur):
        if (vecteur[0] > 0):
            return 1
        elif (vecteur[0] < 0):
            return -1
        else:
            return 0
        

    def intensite_virage(self, v1, v2):
        v1 = np.array(v1, dtype=float)
        v2 = np.array(v2, dtype=float)

        epsilon = 0.0001
        prod_scal = np.dot(v1, v2)

        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        cos_angle = prod_scal / (norm_v1 * norm_v2 + epsilon)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)

        intensite = (1 - cos_angle) / 2
        return intensite


    def phase_virage(self, obs):

        v1 = self.calcul_vecteur(obs["paths_start"][1], obs["paths_end"][1])
        v2 = self.calcul_vecteur(obs["paths_start"][3], obs["paths_end"][3])

        intensite_actuelle = self.intensite_virage(v1, v2)

        if self.intensite_precedente is None:
            self.intensite_precedente = intensite_actuelle
            return 0

        if intensite_actuelle < self.seuil_intensite:
            phase = 0
        else:
            delta = intensite_actuelle - self.intensite_precedente

            if delta > self.seuil_delta:
                phase = 1
            elif delta < -self.seuil_delta:
                phase = 3
            else:
                phase = 2

        
        self.intensite_precedente = intensite_actuelle
        return phase


    def modif_accel(self, act, phase):

        if (phase == 1 or phase == 3):
            accel = act["acceleration"]
            accel += self.acceleration * self.intensite_precedente
            act["acceleration"] = np.clip(accel, 0, 1)

        return act

    def modif_steer(self, act, phase, direction):
        steer = act["steer"]
        if (phase == 1):
            steer += self.steer1 * direction * self.intensite_precedente
            
        elif (phase == 2):
            steer += self.steer2 * direction * self.intensite_precedente
        
        act["steer"] = np.clip(steer, -1, 1) 
        return act

    def modif_brake(self, act, phase):

        if (phase == 2):
            brake = act["brake"]
            brake += self.brake * self.intensite_precedente
            act["brake"] = np.clip(brake, 0, 1)
        return act


    def gestion_virage(self, obs, act):

        vecteur = self.calcul_vecteur(obs["paths_start"][2], obs["paths_end"][2])
        direction = self.direction_virage(vecteur)
        phase = self.phase_virage(obs)

        if phase == 0 or direction == 0:
            return act

        act = self.modif_accel(act, phase)
        act = self.modif_steer(act, phase, direction)
        act = self.modif_brake(act, phase)

       
        return act