import numpy as np 


class ReactionItems : 
    def __init__(self,angle_negative, angle_positive) : 
        self.angle_n = angle_negative
        self.angle_p = angle_positive
        
    def reaction_items(self, obs):
        """
        permet d'eviter les 'bad' items et se diriger les 'good' items 
        """
        items_pos = obs.get('items_position', [])            
        items_type = obs.get('items_type', [])
        steering_adjustment = 0.0

        GOOD_ITEM_IDS = [0, 2, 3, 6]  # BONUS_BOX, NITRO_BIG, NITRO_SMALL, EASTER_EGG
        best_good_dist = 1000.0 # tres grand nombre qui sert comme point de base

        angle_evite = 0.0
        dist_min_evite = 15.0

        for i, pos in enumerate(items_pos):#le sert à faire le lien entre la position de l'item qu'on regarde et son type
            pos = np.array(pos)
            dist = np.linalg.norm(pos)

            # items derriere ou trop loin => ignorer
            
            if pos[2] < 0 or dist > 25.0:
                continue

            item_type = items_type[i] if i < len(items_type) else None

            # prendre le meilleur "good" item le plus proche
            if item_type in GOOD_ITEM_IDS:
                if dist < best_good_dist:
                    best_good_dist = dist
                    angle = np.arctan2(pos[0], pos[2])
                    #modification parce que correction centre piste etait largement plus importante que steering adjustement
                    steering_adjustment = float(np.clip(angle * 5, -0.8, 0.8))#adapter cette partie aux differentes pistes
            else:
                # éviter les bad items proches
                if dist < dist_min_evite:
                    angle_evite = self.angle_n if pos[0] > 0 else self.angle_p

        if abs(angle_evite) > 0:
            return angle_evite #evite bad item
        return steering_adjustment #se dirige vers good items
