""" 
Program computing several features based on inital GPS coordinates of the routes (every second) such as:
 -Lenght of the trip
 -Duration of the trip
 -Average speeds and quartiles
 -Number of stops/average duration of stops
 -% of the time on highway/backroad/midroad
 A previous version included the calculation of acceleration quartiles and decelartion in curves, this has been removed for now on as I am focusing 
the study on speeds but will eventually add the features back.
"""

import os
import pandas as pd
import random as rd
import numpy as np
from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression

def listing_drivers(): 
	""" List the drivers in the directory"""

	folder_dir ='/Users/borisvalensi/desktop/telematic_analysis/drivers'
	list_drivers = sorted(os.listdir(folder_dir))  #remove first element (DS_store.file)
	list_drivers = list_drivers[1:]
	list_drivers = [int(i) for i in list_drivers] 
	list_drivers = sorted(list_drivers)
	# print list_drivers
	return list_drivers


def compute_duration(trip):
	"""Compute the duration of the trip in minutes"""
	df=trip
	return float(len(df)/60)

def compute_trip_length(trip):
	"""Compute the length of the trip in kilometers"""
	df=trip
	return df.sum()/1000

def compute_speed_average_and_deviation(trip):
	"""Compute the length of the trip in kilometers"""
	df=trip
	average=3.6*df.mean()
	deviation=3.6*df.std()
	return average, deviation

def compute_speed_quantiles(trip):
	"""Compute quantiles of the speed distribution in km/h"""

	df=trip
	quantiles=np.linspace(0.1,1.0,num=10)
	result=[]
	for i in range(len(quantiles)):
		result.append(3.6*df.quantile(quantiles[i]))

	dico={}
	noms=["q1","q2","q3","q4","q5","q6","q7","q8","q9","q10"]
	for i in range(len(result)):
		dico[noms[i]]=result[i]
	return dico

def compute_stops(trip):
	"""Compute the number of stops and average duration of stops"""

	df=trip
	nb_stops=0
	stop_duration=0
	average_stop_duration=0
	for i in range(len(df)):
		if df.iloc[i]<3:
			stop_duration+=1
			if i>1 and df.iloc[i-1]>3:
				nb_stops+=1
	if nb_stops !=0:
		average_stop_duration=float(stop_duration)/nb_stops

	return nb_stops, average_stop_duration

def type_of_route(trip):
	"""Compute the percentages of time spent on highways (v>50mph), backroads (v<35mph), and midroads ( 35<v<50)"""
	df=trip
	l=len(df)
	len_highway=len([df>22])
	len_backroad=len([df<16])
	len_midroad=len(df)-len_backroad-len_highway
	return 100*(len_highway/float(l)), 100*(len_midroad/float(l)), 100*(len_backroad/float(l))

def open_file_driver(driver,route):
	file="speed_norm/"+`driver`+"_"+ `route` +".csv"
	df=pd.read_csv(file)
	return df.norm

def compute_feature(trip,driver,route):
	driver=driver
	route=route
	T = compute_duration(trip)
	L = compute_trip_length(trip)
	v_avg, v_std = compute_speed_average_and_deviation(trip)
	dico = compute_speed_quantiles(trip)
	nb_stops, stop_duration_avg = compute_stops(trip)
	pc_h, pc_m, pc_b=type_of_route(trip)
	return [driver,route,T,L,pc_h, pc_m, pc_b,v_avg,v_std,dico["q1"],dico["q2"],dico["q3"],dico["q4"],dico["q5"],dico["q6"],dico["q7"],dico["q8"],dico["q9"],dico["q10"],nb_stops,stop_duration_avg]

def write_csv_features(list_drivers):	 
	df=pd.DataFrame(columns=["driver","route","T","L","pc_h", "pc_m", "pc_b","v_avg","v_std","q1","q2","q3","q4","q5","q6","q7","q8","q9","q10","nb_stops","stop_duration_avg"])
	idx=0
	for driver in list_drivers:
		print "driver is " + `driver`
		for i in range(1,201):
			trip=open_file_driver(driver,i)
			df.loc[idx]=(compute_feature(trip,driver,i))
			idx+=1

	df.to_csv("features2.csv")



def main():
	list_drivers=listing_drivers()
	write_csv_features(list_drivers)

if __name__=="__main__":
	main()



