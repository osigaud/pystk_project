from agents.kart_agent import KartAgent
import numpy as np

class AgentVirage(KartAgent):

    def __init__(self, env, conf, agent ):
        super().__init__(env)
        self.agent = agent
        self.intensite_precedente = None
        self.conf = conf
        self.seuil_intensite = self.conf.seuil_intensite
        self.seuil_corde = self.conf.seuil_corde
        self.seuil_delta = self.conf.seuil_delta
        self.steer1 = self.conf.steer1
        self.steer2 = self.conf.steer2
        self.acceleration = self.conf.acceleration
        self.min_speed = self.conf.min_speed
        self.seuil_drift = self.conf.seuil_drift
        self.marge_drift = self.conf.marge_drift

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
            elif (self.intensite_precedente > self.seuil_corde):
                phase = 2
            else:
                phase = 0

        
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
    

    def modif_steer(self, obs, act, phase, direction):
        steer = act["steer"]

        distance_center = obs["center_path_distance"][0]
        half_track = obs["paths_width"][0] / 2

        marge = 1.0
        facteur = 1.0

        trop_a_droite = distance_center > half_track - marge
        trop_a_gauche = distance_center < -half_track + marge

        # réduction au lieu de blocage
        if direction == -1 and trop_a_droite:
            facteur = 0.2
        elif direction == 1 and trop_a_gauche:
            facteur = 0.2

        if phase == 1:
            steer += facteur * self.steer1 * direction * self.intensite_precedente

        elif phase == 2:
            steer += facteur * self.steer2 * direction * self.intensite_precedente

        act["steer"] = np.clip(steer, -1, 1)
        return act



    def gestion_drift(self, obs, act, phase):
        speed = np.linalg.norm(obs["velocity"])
        distance_center = abs(obs["center_path_distance"][0])
        half_track = obs["paths_width"][0][0] / 2

        if phase != 2:
            act["drift"] = False
            return act

        if speed < self.min_speed:
            act["drift"] = False
            return act

        if self.intensite_precedente < self.seuil_drift:
            act["drift"] = False
            return act

        if distance_center > half_track - self.marge_drift:
            act["drift"] = False
            return act

        act["drift"] = True
        return act

    def gestion_virage(self, obs, act):

        vecteur = self.calcul_vecteur(obs["paths_start"][2], obs["paths_end"][2])
        direction = self.direction_virage(vecteur)
        phase = self.phase_virage(obs)

        if phase == 0 or direction == 0:
            act["drift"] = False
            return act

        act = self.modif_accel(act, phase)
        act = self.modif_steer(obs, act, phase, direction)
        act = self.gestion_drift(obs, act, phase)
       
        return act
