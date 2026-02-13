class Banana:

    def banana_detection(self,obs):

        items_pos = obs['items_position'] # Récupération des positions des items
        items_type = obs['items_type'] # Récupération des types des items

        clo_banana_z = float("inf")
        clo_banana_x = 0.0
        trouve = False 

        for i in range(len(items_pos)): #Boucle pour parcourir la liste entière des items
            if items_type[i] == 1: #Si c'est une banane 
                pos_x = items_pos[i][0] # On récupère le décalage latéral
                pos_z = items_pos[i][2] # On récupère la profondeur
                if -2.5 <= pos_x <= 2.5 and 0.0 <= pos_z <= 17.0:
                    if pos_z < clo_banana_z:
                        clo_banana_z = pos_z
                        clo_banana_x = pos_x
                        trouve = True
        
        return trouve, clo_banana_x, clo_banana_z