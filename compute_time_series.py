####################################################################################################################################
# This script aims at computing several time series based on inital GPS coordinates of the routes (every second)
# We can thus compute:
#  the speed vector and speed norm (every second)
#  the acceleration vector and norm (every second)
#  the angle between two successive position of the car (every second)
# For each trip, these information are written on csv files
####################################################################################################################################


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

def scatter_plot (file_x, file_y, column_x, column_y):
	color=['b','g','r']
	x=getData(file_x,column_x)
	y=getData(file_y,column_y)
	plt.scatter(x,y, c=random.choice(color), alpha=0.5)
	plt.ylabel(column_x)
	plt.xlabel(column_y)

def label_point(x, y, val, ax):
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    print a
    for i, point in a.iterrows():
        ax.text(point['x'], point['y'], str(point['val']))

def scatter_plot_mu_sigma_driver (driver,folder_name): # scatter plot (mu,sigma) for speed or acceleration for the 200 trips of a driver
	result=pd.DataFrame(columns=["mu","sigma"])
	for i in range(1,201):
		file=folder_name +"/"+`driver`+"_"+`i`+".csv"
		df=pd.read_csv(file)
		df=df.drop(df.columns[[0]],axis=1)
		# print df
		result.loc[i]=[df.norm.mean(), df.norm.std()]
	# print result
	result=result.dropna()
	print result.mu
	print result.sigma

	ax=result.plot(kind="scatter", x="mu", y="sigma")

	ax.set_title("Scatter plot (m/s) of " + folder_name)

	# Adding labels on points to identify visually the outlying routes

	for k, v in result.iterrows():
		ax.annotate(k, v, xytext=(-3,5), textcoords='offset points', fontsize=8, color='darkslategrey')


def scatter_plot_mu_sigma_speed (driver,folder_name): # scatter plot (mu,sigma) for speed or acceleration for the 200 trips of a driver
	result_hw=pd.DataFrame(columns=["mu","sigma"])
	result_mr=pd.DataFrame(columns=["mu","sigma"])
	result_br=pd.DataFrame(columns=["mu","sigma"])
	# print result
	for i in range(1,201):
		file=folder_name +"/"+`driver`+"_"+`i`+".csv"
		df=pd.read_csv(file)
		df=df.drop(df.columns[[0]],axis=1)
		
		temp_hw=df["norm"][(df.norm>22)]
		temp_mr=df["norm"][(df.norm<22) & (df.norm>16)]
		temp_br=df["norm"][(df.norm<16)]

		result_hw.loc[i]=[temp_hw.mean(), temp_hw.std()]
		# print result_hw.loc[i]
		result_mr.loc[i]=[temp_mr.mean(), temp_mr.std()]
		result_br.loc[i]=[temp_br.mean(), temp_br.std()]

	result_hw=result_hw.dropna()
	result_br=result_br.dropna()
	result_mr=result_mr.dropna()
	# print result_mr

	fig, axes = plt.subplots(nrows=1, ncols=3)
	result_hw.plot(ax=axes[0], kind="scatter", x="mu", y="sigma")
	result_mr.plot(ax=axes[1], kind="scatter", x="mu", y="sigma")
	result_br.plot(ax=axes[2], kind="scatter", x="mu", y="sigma")
	axes[0].set_title("Highway (m/s)")
	axes[1].set_title("Midroad (m/s)")
	axes[2].set_title("Backroad (m/s)")

	# Adding labels on points to identify visually the outlying routes

	for k, v in result_hw.iterrows():
		axes[0].annotate(k, v, xytext=(-3,5), textcoords='offset points', fontsize=8, color='darkslategrey')
	for k, v in result_mr.iterrows():
		axes[1].annotate(k, v,xytext=(-3,5), textcoords='offset points', fontsize=8, color='darkslategrey')
	for k, v in result_br.iterrows():
		axes[2].annotate(k, v,xytext=(-3,5), textcoords='offset points', fontsize=8, color='darkslategrey')

def getData(file,column):
	df=pd.read_csv(file)
	return df[column]

def main():
	driver_1 = 1
	driver_2 =1
	route_1 = 1
	route_2 = 1
	file_x="Theta/"+`driver_1`+"_"+`route_1`+".csv"
	file_y="acceleration_norm/"+`driver_1`+"_"+`route_1`+".csv"
	column_x= "Angle"
	column_y= "norm"
	folder_name_1="speed_norm"
	folder_name_2="acceleration_norm"

	scatter_plot(file_x, file_y, column_x, column_y)
	scatter_plot_mu_sigma_speed (driver_1,folder_name_1)
	scatter_plot_mu_sigma_driver (driver_1,folder_name_2)

	plt.show()
	return

if __name__ == '__main__':
	main()
