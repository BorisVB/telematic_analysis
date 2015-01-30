####################################################################################################################################
# This script aims at computing several time series based on inital GPS coordinates of the routes (every second)
# We can thus compute:
#  the speed vector and speed norm (every second)
#  the acceleration vector and norm (every second)
#  the angle between two successive position of the car (every second)
# For each trip, these information are written on csv files
####################################################################################################################################

import os
import pandas as pd
import numpy as np

def listing_drivers(folder_dir): 	        # Create a sorted list with all the drivers id
    list_drivers=sorted(os.listdir(folder_dir)) #remove first element (DS_store. file)
    list_drivers=list_drivers[1:]  
    list_drivers = [int(i) for i in list_drivers] 
    list_drivers = sorted(list_drivers)
    # print list_drivers
    return list_drivers


def compute_speeds(file):
	df=pd.read_csv(file,delimiter=',', dtype = float)
	dfminusfirst=df[1:].reset_index()
	# print dfminusfirst
	dfminuslast=df[:-1]
	# print dfminuslast

	speed_vector=pd.DataFrame()
	speed_norm=pd.DataFrame()

	speed_vector["x"]=dfminusfirst["x"]-dfminuslast["x"]
	speed_vector["y"]=dfminusfirst["y"]-dfminuslast["y"]
	speed_vector.loc[-1]=[0,0]
	speed_vector.index=speed_vector.index+1
	speed_vector=speed_vector.sort()

	speed_norm["norm"]=(speed_vector["x"]**2+speed_vector["y"]**2)**0.5
	# print speed_norm

	#remove anormal data (speed>56m/s)
	for i in range(len(speed_norm.index)):
		# print "i is : " + `i`
		# print speed_norm.iat[i,0]
		j=1
		if speed_norm.iat[i,0]>56 and i>0 and (i+j)<len(speed_norm.index):
			sup_norm=speed_norm.iat[i+j,0]
			sup_vect_x=speed_vector.iat[i+j,0]
			sup_vect_y=speed_vector.iat[i+j,1]
			while speed_norm.iat[i+j,0]>56 and (i+j+1)<len(speed_norm.index):
				sup_norm=speed_norm.iat[i+j+1,0]
				# print speed_norm.iat[i+j,0]
				sup_vect_x=speed_vector.iat[i+j+1,0]
				sup_vect_y=speed_vector.iat[i+j+1,1]
				j+=1
			for k in range(0,j):
				speed_norm.iat[i+k,0]=(speed_norm.iat[i-1,0]+sup_norm)/2
				speed_vector.iat[i+k,0]=(speed_vector.iat[i-1,0]+sup_vect_x)/2
				speed_vector.iat[i+k,1]=(speed_vector.iat[i-1,1]+sup_vect_y)/2

	# print speed_norm
	# print df['x']
	# # print df.iloc[[3]]
	return (speed_vector, speed_norm)

def compute_angles(speed_norm_file,speed_vector_file):
	speed_norm=pd.read_csv( speed_norm_file,delimiter=',', dtype = float)
	speed_vector=pd.read_csv( speed_vector_file,delimiter=',', dtype = float)
	sp_norm_plus=speed_norm[1:].reset_index()
	sp_norm_minus=speed_norm[:-1]
	sp_vector_plus=speed_vector[1:].reset_index()
	sp_vector_minus=speed_vector[:-1]
	Theta=pd.DataFrame()
	Theta["Angle"]= (360/(2*(np.pi)))*np.arccos(((sp_vector_plus["x"]*sp_vector_minus["x"])+(sp_vector_plus["y"]*sp_vector_minus["y"]))/(sp_norm_plus["norm"]*sp_norm_minus["norm"]))
	Theta.fillna(0,inplace=True)
	Theta.loc[-1]=[0]
	Theta.index=Theta.index+1
	# print Theta
	return Theta

def compute_acceleration(speed_vector_file):
	speed_vector=pd.read_csv( speed_vector_file,delimiter=',', dtype = float)
	sp_vector_plus=speed_vector[1:].reset_index()
	sp_vector_minus=speed_vector[:-1]
	
	acceleration_vector=pd.DataFrame()
	acceleration_norm=pd.DataFrame()

	acceleration_vector["x"]=sp_vector_plus["x"]-sp_vector_minus["x"]
	acceleration_vector["y"]=sp_vector_plus["y"]-sp_vector_minus["y"]
	acceleration_vector.loc[-1]=[0,0]
	acceleration_vector.index=acceleration_vector.index+1

	acceleration_norm["norm"]=(acceleration_vector["x"]**2 + acceleration_vector["y"]**2)**0.5

	print acceleration_norm

	return (acceleration_vector,acceleration_norm)

def compute_stops(speed_norm_file):
	speed_norm=pd.read_csv( speed_norm_file,delimiter=',', dtype = float)
	stop_info=pd.DataFrame()
	start=10
	stop=len(speed.norm.index)-60
	if len(speed.norm.index)>60:
		for i in range(start,stop) :
			if speed_norm.iat[i,0]<0.5 and speed_norm.iat[i-1,0]>0.5: # Nouveau Stop
				k=1
				while speed_norm[i+k,0]<0.5 and i+k<stop:
					k=k+1
				stop_info.iat[i,"a - 3sec"]=speed_norm.iat[i-3,0]/3
				stop_info.iat[i,"a - 2sec"]=speed_norm.iat[i-2,0]/2
				stop_info.iat[i,"a - 1sec"]=speed_norm.iat[i-1,0]
				stop_info.iat[i,"duration"]=k
				stop_info.iat[i,"a + 3sec"]=speed_norm.iat[i+3,0]/3
				stop_info.iat[i,"a + 2sec"]=speed_norm.iat[i+2,0]/2
				stop_info.iat[i,"a + 1sec"]=speed_norm.iat[i+1,0]
	else:
		stop_info.loc[0] = pd.Series({"a - 3sec":0, "a - 2sec":0, "a - 1sec":0, "duration":0, "a + 3sec":0, "a + 2sec":0, "a + 1sec":0})
	return stop_info

def write_csv_speed(list_drivers):
	for drivers in list_drivers:
		print 'driver is '+ `drivers`
		for k in range(1,201):
			# print "route is" +`k`
			file='drivers/' +`drivers`+'/'+`k`+'.csv'
			(speed_vector, speed_norm)=compute_speeds(file)
			path_vector="speed_vector/"+`drivers`+"_"+`k`+".csv"
			# print speed_vector
			speed_vector.to_csv(path_vector)
			path_norm="speed_norm/"+`drivers`+"_"+`k`+".csv"
			speed_norm.to_csv(path_norm)

def write_csv_angles(list_drivers):
	for drivers in list_drivers:
		print 'driver is '+ `drivers`
		for k in range(1,201):
			# print "route is" +`k`
			speed_norm_file='speed_norm/' +`drivers`+'_'+`k`+'.csv'
			speed_vector_file='speed_vector/' +`drivers`+'_'+`k`+'.csv'

			Theta=compute_angles(speed_norm_file,speed_vector_file)
			
			path_Theta="Theta/"+`drivers`+"_"+`k`+".csv"
			print Theta
			Theta.to_csv(path_Theta)
		

def write_csv_acceleration(list_drivers):
	for drivers in list_drivers:
		print 'driver is '+ `drivers`
		for k in range(1,201):
			# print "route is" +`k`
			file='speed_vector/' +`drivers`+'_'+`k`+'.csv'
			(acceleration_vector, acceleration_norm)=compute_speeds(file)
			path_vector="acceleration_vector/"+`drivers`+"_"+`k`+".csv"
			acceleration_vector.to_csv(path_vector)
			path_norm="acceleration_norm/"+`drivers`+"_"+`k`+".csv"
			acceleration_norm.to_csv(path_norm)

def write_csv_stops(list_drivers):
	for drivers in list_drivers:
		print 'driver is '+ `drivers`
		for k in range(1,201):
			# print "route is" +`k`
			file='speed_norm/' +`drivers`+'_'+`k`+'.csv'
			stop_info=compute_stops(file)
			path_vector="stop_info/"+`drivers`+"_"+`k`+".csv"
			stop_info.to_csv(path_vector)

def main():
	folder_dir='/Users/borisvalensi/desktop/telematic_analysis/drivers'
	list_drivers=listing_drivers(folder_dir)
	# print 'total number of drivers is ' +`len(list_drivers)`
	# write_csv_speed(list_drivers)
	write_csv_angles(list_drivers)
	# write_csv_acceleration(list_drivers)


if __name__=="__main__":
	main()
