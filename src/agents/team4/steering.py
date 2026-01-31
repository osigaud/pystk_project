class Steering:
    def steering(self,obs):
        points = obs['paths_start'] #on recupère les noeuds
        x = 0.0
        if len(points)>2:
            x = points[2][0] #deballage du décalage latéral en prenant le troisième point sur la liste
        return x*0.7 #coefficient pour rendre l'agent moins nerveux

