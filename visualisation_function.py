################################################################################################################################
#This file aims at visualising some features of the trips
#This includes: histograms, bar charts, scatter plots and maps of routes
################################################################################################################################
import numpy as np
import matplotlib.pyplot as plt
import random
import csv

# Get the values in a column as a list

def getColumn(filename, driver, column):
    doc = csv.reader(open(filename), delimiter=',', lineterminator='\n',quotechar='"')
    result=[]
    line=0
    i=0
    for row in doc:
    	if line==0:
    		result.append(row[column])
    	if line>0 and int(row[0])==driver:
    		result.append(row[column])
    		i+=1
    	if i==200:
    		break
    	line+=1
    return result

def map_all_routes(k):
	fig = plt.figure()
	ax = fig.add_subplot(111, axisbg = 'w')
	colors = ['b','g','r','c','m','y','k']
	for i in range(1,201):
	    with open('drivers/'+`k`+'/'+ `i`+'.csv','rb') as data: 
	        trajet = np.genfromtxt(data,delimiter=',', dtype = float)
	        x = [row[0] for row in trajet]
	        y = [row[1] for row in trajet]
	        # plt.figure(1)
	        ax.plot(x,y,(random.choice(colors)),lw=1.3)
	# plt.show()


def hist (driver,column):
	data=getColumn("features.csv.",driver,column)
	legend=data.pop(0)
	values=map(float, data)
	print len(values)
	# print values
	plt.hist(values, 50, facecolor='blue')
	plt.xlabel(legend)
	plt.ylabel('cummulative number of routes')
	# plt.figure(2)
	# plt.show()

def n_hists(driver, n_columns):
	for column in range(3,n_columns):
		plt.figure()
		hist(driver,column)

def bar_chart(driver,column):
	x=range(201)[1:]
	data=getColumn("features.csv.",driver,column)
	legend=data.pop(0)
	values=sorted(map(float, data))
	y=values
	plt.bar(x,y)
	plt.ylabel(legend)
	plt.xlabel("Routes")

def n_bar_chart (driver,n_columns):
	for column in range (3,n_columns):
		plt.figure()
		bar_chart(driver,column)

def curve_xy_1 (driver,feature_1, feature_2):
	color=['b','g','r']
	x=getColumn("features.csv.",driver,feature_1)
	y=getColumn("features.csv.",driver,feature_2)
	leg_x=x.pop(0)
	leg_y=y.pop(0)
	plt.scatter(x, y, c=random.choice(color), alpha=0.5)
	plt.ylabel(leg_y)
	plt.xlabel(leg_x)

def curve_xy_2 (driver_1, driver_2, feature_1, feature_2):
		curve_xy_1(driver_1,feature_1, feature_2)
		curve_xy_1(driver_2, feature_1, feature_2)

driver_1 = 1
driver_2 =1
feature_1 = 16
feature_2 = 5
# driver,route,Time_hour,Rayon,Distance_km,Vkmh_avg,Vmax,Vstd,V_25,V_75,A_afterstop_avg,Curves_light_a_avg,Curves_strong_a_avg,Braking_deceleration_avg,Braking_distance_avg,pc_highway,pc_backroad,pc_midroad,Stop_time,Stop_number
def main():

	# call functions:

	map_all_routes(driver_1)
	# hist(driver_1,feature_1)
	# n_hists(driver_1,feature_1)
	# bar_chart(driver_1,feature_1)
	# n_bar_chart(driver_1,feature_1)
	# curve_xy_1(driver_1,feature_1, feature_2)
	# curve_xy_2 (driver_1, driver_2, feature_1, feature_2)
	plt.show()
	return

if __name__ == '__main__':
	main()
