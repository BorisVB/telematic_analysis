**===>Goal of the competition:**

AXA has provided a dataset of over 50,000 anonymized driver trips. The intent of this competition is to develop an algorithmic signature of driving type. For this competition, Kaggle participants must come up with a "telematic fingerprint" capable of distinguishing when a trip was driven by a given driver. 

We are provided a directory containing about 3000 folders. Each folder represents a driver. Within each folder are 200 .csv files. Each file represents a driving trip. The trips are recordings of the car's position (in meters) every second.
In order to protect the privacy of the drivers' location, the trips were centered to start at the origin (0,0), randomly rotated, and short lengths of trip data were removed from the start/end of the trip.

A small and random number of false trips (trips that were not driven by the driver of interest) are planted in each driver's folder. These false trips are sourced from drivers not included in the competition data, in order to prevent similarity analysis between the included drivers. We are not given the number of false trips (it varies), nor a labeled training set of true positive trips. It is allowed to safely make the assumption that the majority of the trips in each folder do belong to the same driver.

The challenge of this competition is to identify trips which are not from the driver of interest, based on their telematic features. There is to predict a probability that each trip was taken by the driver of interest.

**==> My approach:**

1. First to be able to visually understand what are the similarities between the 200 routes associated to one driver, and the difference between two drivers. 
2. Create algorithms capable of predicting with a probability P the likelihood that a route has been driven by the designated driver

I am focusing on:
1. Speed distribution

2. Acceleration distribution

3. Acceleration/decceleration before and after stop

4. Acceleration/decceleration in curves

I am currently focusing on speed and acceleration visualisation. This first involve to clean the data (removing anomalies due to GPS imprecision e.g.). I am also approaching this problem by breaking down the trips between behavior on highway, backroad, and 'midroad'.

