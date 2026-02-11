class Banana:

    def banana_detection(self,obs):

        items_pos = obs['items_position'] # Récupération des positions des items
        items_type = obs['items_type'] # Récupération des types des items 

        for i in range(len(items_pos)): #Boucle pour parcourir la liste entière des items
            if items_type[i] == 1: #Si c'est une banane 
                pos_x = items_pos[i][0] # On récupère le décalage latéral
                pos_z = items_pos[i][2] # On récupère la profondeur
                if -2.5 <= pos_x <= 2.5 and 0.1 <= pos_z <= 8.0 and obs['distance_down_track'] >= 55.0:
                    return True, pos_x # Si la logique est respectée, on retourne Vrai ainsi que la position_x de la banane
        return False,0