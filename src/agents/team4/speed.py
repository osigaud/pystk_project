class SpeedController:
    
    def manage_speed(self, steer, obs):
        
        points = obs.get("paths_start",[]) # Récupération des points 
        vel = obs.get("velocity", [0.0, 0.0, 0.0]) # Recuperation des vecteurs velocite
        speed = float(vel[2]) # Recuperation de la vitesse frontal

        if len(points) <=2: # Si pas assez de points
            return 1.0, False
        

        if obs['distance_down_track']<=2: # Au départ on accélère à fond
            return 1.0, False
        
        i2 = 2 # Point d'indice 2
        i3 = min(3,len(points)-1) # Point d'indice 3 ou moins si pas assez de points
        i4 = min(4,len(points)-1) # Point d'indice 4 ou moins si pas assez de points
        
        target_now = points[i2][0] # Décalage latéral du point d'indice 2
        target_soon = points[i3][0] # Décalage latéral du point d'indice 3
        target_late = points[i4][0] # Décalage latéral du point d'indice 4

        if target_now >= 12:
            # Si virage serre prevu et grosse vitesse on freine et on relache la pedale d'accel
            if speed >=20.0:
                #print("Gros Freinage !")
                brake = True
                acceleration = 0.0
            # Si virage serre prevu et vitesse modere on relache seuleument la pedale d'accel
            else:
                #print("On lache seuleument l'accelerateur !")
                brake = False
                acceleration = 0.0
        
        # Pas de frein si dans un virage, on baisse l'acceleration
        elif abs(steer) >= 0.7:
            #print("En virage")
            brake = False
            acceleration = 0.8
        # A fond dans une ligne droite
        else:
            brake = False
            acceleration = 1.0
        
        return acceleration, brake