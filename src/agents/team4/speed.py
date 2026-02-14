class SpeedController:
    
    def manage_speed(self, steer, obs):
        
        points = obs.get("paths_start",[])
        vel = obs.get("velocity", [0.0, 0.0, 0.0])
        speed = float(vel[2])

        if len(points) <=2:
            return 1.0, False
        

        if obs['distance_down_track']<=2:
            return 1.0, False
        
        i2 = 2
        i3 = min(3,len(points)-1)
        i4 = min(4,len(points)-1)
        
        target_now = points[i2][0]
        target_soon = points[i3][0]
        target_late = points[i4][0]

        if target_now >= 12:
            
            if speed >=20.0:
                #print("Gros Freinage !")
                brake = True
                acceleration = 0.0
            else:
                #print("On lache seuleument l'accelerateur !")
                brake = False
                acceleration = 0.0
        
        elif abs(steer) >= 0.7:
            #print("En virage")
            brake = False
            acceleration = 0.8
        else:
            brake = False
            acceleration = 1.0
        return acceleration, brake