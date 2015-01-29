####################################################################################################################################
# Program computing several features based on inital GPS coordinates of the routes (every second) such as:
# -Lenght of the trip
# -Duration of the trip
# -Average speeds and several quartiles
# -Average accelerations and several quartiles
# -The angle between two successive position of the car (every second)
# -Number of stops
# etc.
####################################################################################################################################


import numpy as np
import matplotlib.pyplot as plt
import csv
import os  
from glob import glob
import random
import sys

# Function features

def features(list):         # Take a list of position(x,y) every second for a route and return different features
    S=list[1:]
    S2=list[:-1]

    Vinst = S-S2            # List of speeds, every second, vector (x,y)
    Vms=[]                  # List of speeds, every second, scalar, in m/s
    highway=0               # Time on highway, Vms>50mph=22m/s
    backroad=0              # Time on backroad, Vms<35mph=16m/s
    midroad=0               # Time on midroad, Vms>35mph=16m/s and Vms<50mph=22m/s
    Angles=[]               # List of angles, change in car direction, every second, in degree
    Angles_after_stop=[]    # List of angles, after a stop, in degree
    Ainst=Vinst[1:]-Vinst[:-1]
                            # List of accelerations, every second, vector (x,y)
    Ams2=[]                 # List of accelerations, every second, scalar, in m/s2                    
    A_afterstop=[]          # List of accelerations, from a stop, every second, scalar, in m/s2
    Curves_light_a=[]       # List of accelerations, in curves where 23<theta<45
    Curves_strong_a= []     # List of accelerations, in curves where 45<theta<90
    Stop_time=0             # Total duration of all stops, in s    
    Stop_number=0           # Number of Stops during the route
    Braking_deceleration=[] # List of decelerations, 3 seconds before a stop (m/s2) 
    Braking_distance=[]     # List of distances driven, 3 seconds before each stop (m)

    i=0
    Vbefore=[]
    Theta=0



    for row in Vinst:
        Vms.append((row[0]**2+row[1]**2)**0.5)

        if Vms[i]>=22:
            highway=+1
        if Vms[i]<=16:
            backroad=+1
        else:
            midroad=+1

        if i>0:
            Theta= (360/(2*(np.pi)))*np.arccos((Vbefore[0]*row[0]+Vbefore[1]*row[1])/(Vms[i]*Vms[i-1]))
            Angles.append(Theta)
            if Vms[i-1]>2:
                if Theta>23 and Theta<45:
                    Curves_light_a.append(((row[0]-Vbefore[0])**2+(row[1]-Vbefore[1])**2)**0.5)
                if Theta>45 and Theta<90:
                    Curves_strong_a.append(((row[0]-Vbefore[0])**2+(row[1]-Vbefore[1])**2)**0.5)
        
        if i>0 and Vms[i]>=2 and Vms[i-1]<2:
                A_afterstop.append(Vms[i])
                Angles_after_stop.append(Theta)
                                                                                    
        if Vms[i]<2:                 # less than 2m in 1sec counted as stop
            Stop_time += 1
            if i>0 and Vms[i-1]>2:        # does not count starting
                Stop_number+=1             # count the new stops only
        i+=1    
        Vbefore=row
    i=0    
    for row in Ainst:
        Ams2.append(( (row[0])**2+(row[1])**2 )**0.5)
        if i>2 and i<len(Vms) and Ams2[i]<1 and Vms[i+1]<2 and Ams2[i-1]>1:
            Braking_deceleration.append(Ams2[i-3])
            Braking_distance=Vms[i+1]+Vms[i]+Vms[i-1]+Vms[i-2]
            # print "Ams2[i] is "+ `Ams2[i]`
            # print "vms(i) is " + `Vms[i+1]`
        i+=1

    return (Vms,highway, backroad, midroad, Angles_after_stop, Ams2, A_afterstop, Curves_light_a,Curves_strong_a, Stop_time,Stop_number,Braking_deceleration, Braking_distance)

def basic_infos(route, Vms): #Calculate basic infos of the trip
    Time_hour=len(route)/float(3600)
    Rayon=((route[len(route)-1,0])**2+(route[len(route)-1,1])**2)**0.5
    Distance_km=sum(Vms)/float(1000)
    return [Time_hour, Rayon, Distance_km]

def speeds (Vms):   #Calculate speed averages and percentiles
    Vkmh=3.6*np.array(Vms) # List speed vector km/h
    Vkmh_avg=np.mean(Vkmh)    # Average speed in km/h
    Vmax=max(Vkmh)        # Max speed in km/h
    Vstd=np.std(Vkmh)      # Standard deviation to average speed in km/h
    V_25=np.percentile(Vkmh,25)
    V_75=np.percentile(Vkmh,75)
    return [Vkmh_avg,Vmax,Vstd, V_25, V_75]

def type_route(highway,backroad,midroad):   #calculate percentages of trip on highway, backroad or midroad
    result=[]
    tot=float(highway+backroad+midroad)
    if tot==0:
        result=[0,0,0]
    else: 
        result=[highway/tot,backroad/tot,midroad/tot]
    return result

def acceleration_averages(A_afterstop,Curves_light_a,Curves_strong_a): #Calculate different averages on the acceleration
    A_afterstop_avg=0
    cleaned_Curves_light_a = [x for x in Curves_light_a if float(x) != 'nan']
    cleaned_Curves_strong_a = [x for x in Curves_strong_a if float(x) != 'nan']

    Curves_light_a_avg=0
    Curves_strong_a_avg=0

    if len(A_afterstop)>1:                
        A_afterstop_avg=np.mean(A_afterstop)
    else:
        A_afterstop_avg=0
        
    if len(cleaned_Curves_light_a)>1:                
        Curves_light_a_avg=np.mean(cleaned_Curves_light_a)
    else:
        Curves_light_a_avg=0
        
    if len(cleaned_Curves_strong_a)>1:                
        Curves_strong_a_avg=np.mean(cleaned_Curves_strong_a)
    else:
        Curves_strong_a_avg=0

    return [A_afterstop_avg,Curves_light_a_avg, Curves_strong_a_avg]

def braking_averages(Braking_deceleration, Braking_distance): #Calculate averages on braking
    

    if len(np.atleast_1d(Braking_deceleration))>0:
        Braking_deceleration_avg=np.mean(Braking_deceleration)
    else:
        Braking_deceleration_avg=0

    if len(np.atleast_1d(Braking_distance))>0:
        Braking_distance_avg=np.mean(Braking_distance)
    else:
        Braking_distance_avg=0

    return [Braking_deceleration_avg,Braking_distance_avg]

def main():
        # Create a list of drivers
        list_drivers=sorted(os.listdir('/Users/borisvalensi/desktop/telematic_analysis/drivers'))
        list_drivers=list_drivers[1:]
        list_drivers = [int(i) for i in list_drivers]
        list_drivers = sorted(list_drivers)

        # Preparation of the result file
        results = csv.writer(open("features.csv.", "wb"),lineterminator="\n")
        results.writerow(["driver", "route","Time_hour", "Rayon", "Distance_km", "Vkmh_avg","Vmax","Vstd", "V_25", "V_75", "A_afterstop_avg", "Curves_light_a_avg", "Curves_strong_a_avg", "Braking_deceleration_avg", "Braking_distance_avg", "pc_highway","pc_backroad","pc_midroad", "Stop_time","Stop_number"])


        # Iterating over all the drivers 
        for drivers in list_drivers:
            print 'driver is '+ `drivers`
            
            # Create array X to write the features of the driver

            X = np.ones((200,18))

            # Reading of the 200 routes and calculating features
            
            for i in range(1,201):
                file='drivers/' +`drivers`+'/'+`i`+'.csv'
                with open(file,'rb') as data:
                    reader=np.genfromtxt(data,delimiter=',', dtype = float)
                    x=list(reader)
                    route=np.array(x[1:]) # List of all [x,y] for a route
                    
                    (Vms,highway, backroad, midroad, Angles_after_stop, Ams2, A_afterstop, Curves_light_a,Curves_strong_a, Stop_time,Stop_number,Braking_deceleration, Braking_distance)=features(route)    

                    [Time_hour, Rayon, Distance_km]=basic_infos(route, Vms)
                    [Vkmh_avg,Vmax,Vstd, V_25, V_75]=speeds(Vms)    
                    [A_afterstop_avg,Curves_light_a_avg, Curves_strong_a_avg]=acceleration_averages(A_afterstop,Curves_light_a,Curves_strong_a)
                    [Braking_deceleration_avg,Braking_distance_avg]=braking_averages(Braking_deceleration, Braking_distance)
                    [pc_highway,pc_backroad,pc_midroad]=type_route(highway, backroad, midroad)

                    X[i-1]=[Time_hour, Rayon, Distance_km, Vkmh_avg,Vmax,Vstd, V_25, V_75, A_afterstop_avg,Curves_light_a_avg, Curves_strong_a_avg, Braking_deceleration_avg,Braking_distance_avg, pc_highway,pc_backroad,pc_midroad, Stop_time,Stop_number]

            # Writing results

            route=0
            for row in X:
                route+=1
                resultats=row
                resultats=resultats.tolist()
                resultats.insert(0,route)
                resultats.insert(0,drivers)
                results.writerow(resultats)

    return
if __name__ == '__main__':   
main()

