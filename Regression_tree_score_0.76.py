""" 
Use driver's 200 trips as positive training data and 300 trips from other drivers as negative training data
Use Gradient Boosted Regression Trees (GBRT) from sklearn and extract the  140 routes whith highest probability that y=1.

From these 140 routes create: 
-a new training set with top 70 routes as y=1, and 300 random routes from random drivers as y=0
-a new cross validation set with the 70 routes remaining as y=1, and 300 random routes from other drivers as y=0
Use the GBRT regression 3-times on cross validation set and take the results with hightest AUC score

The method score about 0.76 of AUC.

Next step is to include more features acceleration to improve the result and to add the resut of a trip matching algorithms
"""


import os
import pandas as pd
import random as rd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
import sklearn.metrics as metrics

# Creation of a sorted lists of all the drivers:
def listing_drivers(): 
	folder_dir ='/Users/borisvalensi/desktop/telematic_analysis/drivers'
	list_drivers = sorted(os.listdir(folder_dir))  #remove first element (DS_store.file)
	list_drivers = list_drivers[1:]
	list_drivers = [int(i) for i in list_drivers] 
	list_drivers = sorted(list_drivers)
	# print list_drivers
	return list_drivers

# Creation of a list of 400 routes that will be used as y=0:
def random_drivers(list_drivers):
	list=rd.sample((list_drivers),61)
	return list

def features_0(list_drivers,features):
	list=random_drivers(list_drivers)
	X_0=pd.DataFrame()
	for driver in list:
		X_0=X_0.append(features[features["driver"]==driver][:10])

	X_0=X_0.drop(X_0.columns[[0,1,2]], axis=1)

	return X_0

def features_1(driver):	
	return features[features["driver"]==driver]

def prepare_X(driver,X_0):
	# Prepare vector features:
	X_1=features_1(driver)
	X_1=X_1.drop(X_1.columns[[0,1,2]], axis=1)

	X_train=X_1.append(X_0[:300])
	# X_train=X_train.reset_index() # attention ajoute colonne index

	# Prepare result vector:
	Y_train_0=pd.DataFrame(0, index = np.arange(300), columns= ["y"])
	Y_train_1=pd.DataFrame(1, index = np.arange(200), columns= ["y"])
	Y_train=Y_train_1.append(Y_train_0)

	"""prepare cross validation set"""
	X_cv=pd.concat([X_1, X_0[300:600]])
	# print X_cv
	# print len(X_cv)
	Y_cv=pd.concat([Y_train_1, Y_train_0])
	# print len(Y_cv)
	return X_train.reset_index(drop=True), Y_train.reset_index(drop=True), X_cv.reset_index(drop=True), Y_cv.reset_index(drop=True)

def prepare_X_advanced(driver,X_0):
	X_train, Y_train, X_cv, Y_cv = prepare_X(driver,X_0)
	X_200=X_train[:200]
	Y_temp=1-Y_cv
	Y_cv=pd.concat([Y_temp, Y_cv], axis=1)

	# First GBRT to identify top 140 proba that y=1:

	GBRT = GradientBoostingClassifier(n_estimators=1000, learning_rate=0.05,max_depth=6, random_state=1, subsample=1, warm_start=False)
	GBRT.fit(X_train, Y_train)

	Y_prob=GBRT.predict_proba(X_train[:200])
	Y_prob=pd.DataFrame(Y_prob)
	# print Y_prob
	Y_1=Y_prob.ix[:,1].order(ascending=False)[:140]
	# print (Y_1)
	# print Y_1
	X_1_train_ix=Y_1[:70].index
	X_1_cv_ix=Y_1[70:140].index



	X_train_1=X_train[X_train.index.isin(X_1_train_ix)]
	# print X_train
	# print X_1_train_ix
	# print X_1_cv_ix

	X_cv_1=X_cv[X_cv.index.isin(X_1_cv_ix)]

	X_train=X_train_1.append(X_train[200:],ignore_index=True)
	X_cv= X_cv_1.append(X_cv[200:],ignore_index=True)

	Y_cv=(Y_cv[:70]).append(Y_cv[200:500], ignore_index=True)
	Y_train=(Y_train[70:140]).append(Y_train[200:500],ignore_index=True)

	# print X_200.shape
	# print X_train.shape
	# print X_cv.shape

	return X_200, X_train, Y_train, X_cv, Y_cv
	# print len(X_train)
	# print len(X_cv)



def performance_cv(Y_pred, Y_prob, Y_true):
	Y_temp=(Y_true[[1]]).values.ravel()
	Y_temp=np.array(Y_temp).reshape((500,1))
	Y_pred=np.array(Y_pred).reshape((500,1))
	
	accuracy=metrics.accuracy_score(Y_temp, Y_pred)
	
	average_precision=metrics.average_precision(Y_true[[1]], pd.DataFrame(Y_pred))
	f1_score=metrics.f1_score(Y_true[[1]],Y_pred)
	precision_score=metrics.precision_score(Y_true[[1]], Y_pred)
	recall_score=metrics.recall_score(Y_true[[1]], Y_pred)
	roc_auc_score=metrics.roc_auc_score(Y_true, Y_prob)

	print "accuracy_score is %d" %100*accuracy
	print "average_precision is %d" %100*average_precision
	print "f1_score is %d" %100*f1_score
	print "precision_score is %d" %100*precision_score
	print "recall is %d" %100*recall_score
	print "roc_auc_score is " +`roc_auc_score`


	Y_prob_one=Y_pred[:70]
	p_ones=Y_prob_one.mean()
	print "average proba for ones is " +str(p_ones)

	Y_prob_zeros=Y_pred[70:]
	p_zeros=Y_prob_zeros.mean()
	print "average proba for zeros is " +str(p_zeros)
	Y_zeros=Y_true[70:]

	return roc_auc_score

def GBRT(driver,X_0):
	X_200, X_train, Y_train, X_cv, Y_cv = prepare_X_advanced(driver,X_0)

	score_res=[]
	Y_res=[]

	for k in range(0,3):
		print "trial is %d" %k
		GBRT = GradientBoostingClassifier(n_estimators=1000, learning_rate=0.05, max_depth=6, random_state=k, subsample=1, warm_start=False)

		GBRT.fit(X_train, Y_train)
		Y_pred=GBRT.predict(X_cv)
		Y_prob=GBRT.predict_proba(X_cv)
		Y_prob=pd.DataFrame(Y_prob)

		Y_res_temp=pd.DataFrame(GBRT.predict_proba(X_200))

		score=performance_cv(Y_pred, Y_prob, Y_cv)

		print "ROC score is " + str(score)
		score_res.append(score)
		Y_res.append(Y_res_temp)

	idx=score_res.index(max(score_res))
	Res=Y_res[idx]
	return Res[[1]]

def GBRT_all(list_drivers):
	Y_final=pd.DataFrame()
	Y_final.index.names = ['driver_trip']
	X_0=features_0(list_drivers,features)
	i=0

	for driver in list_drivers:
		print "driver is " +`driver`
		i+=1
		Y_pred=GBRT(driver,X_0)

		ix=[]
		for i in range(1,201):
			ix.append(`driver`+"_"+ `i`)
		Y_pred=Y_pred.reindex(Y_pred.index.rename('driver_trip'))
		Y_pred=Y_pred.set_index([ix])
		Y_pred.columns=["prob"]
		Y_pred.index.names = ['driver_trip']


		Y_final=Y_final.append(Y_pred)


	path="results/GBRT_02_05_v1.0.csv"
	Y_final.to_csv(path)

doc="features2.csv"
features=pd.read_csv(doc)

def main():
	list_drivers=listing_drivers()
	GBRT_all(list_drivers)

if __name__ == '__main__':
	main()
