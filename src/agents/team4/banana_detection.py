class Banana:

    def banana_detection(self,obs,limit_path,center_path):

        items_pos = obs['items_position'] # Récupération des positions des items
        items_type = obs['items_type'] # Récupération des types des items

        banana = []

        for i in range(len(items_pos)):
            if items_type == 1 or items_type == 4:
                pos_x = items_pos[i][0]
                pos_z = items_pos[i][2]

                dist_obj_centre= abs(center_path+pos_x)

                if dist_obj_centre > limit_path:
                    continue

                if -2.0 <= pos_x <= 2.0 and 0.0 <= pos_z <= 17.0:
                    banana.append((pos_x,pos_z))

        banana.sort(key=lambda x: x[1])

        if len(banana) == 0:
            return "CLEAR",None,None
        
        first = banana[0]
        first_x = first[0]
        first_z = first[1]

        if len(banana) >=2:
            second = banana[1]
            x = second[0]
            z = second[1]
            if abs(z-first_z) <= 2.0:
                gap_x = (x+first_x)/2.0
                return "LIGNE", gap_x, banana
            else:
                return "SINGLE", first_x,banana
        else:
            return "SINGLE",first_x,banana