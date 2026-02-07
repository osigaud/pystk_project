import math

class Steering:
    def manage_steering(self,obs):
        points = obs['paths_start'] #on récupère les noeuds
        if len(points)>2:
            x = points[2][0] #deballage du décalage latéral en prenant le troisième point sur la liste
            z = points[2][2] #deballage de la profondeur en prenant le troisième point sur la liste
            steer = math.atan2(x,z) * 2 #calcul de l'angle de braquage avec math.atan2 qui gère le cas où z vaut 0 ainsi que le signe de x et z
        else:
            steer = 0.0
        return steer


