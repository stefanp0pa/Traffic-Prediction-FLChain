import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from numpy import load

distances = pd.read_csv('./distance.csv')
data = load('./pems08.npz')

lst = data.files
timestamp_count = data[lst[0]].shape[0]
locations_count = data[lst[0]].shape[1]
features_count = data[lst[0]].shape[2]

print("Timestamp count: ", timestamp_count)
print("Locations count: ", locations_count)
print("Features count: ", features_count)

distances_dict = {}
with open('./distance.csv', 'r') as file:
    lines = file.readlines()
    for line in lines[1:]:
        from_node, to_node, cost = line.strip().split(',')
        distances_dict[(from_node, to_node)] = float(cost)

traffic_data = data[lst[0]]
data_dict = []
for timestep in range(traffic_data.shape[0]):
    for location in range(traffic_data.shape[1]):
        data_dict.append({
            "timestep" : timestep+1,
            "location" : location,
            "flow"     : traffic_data[timestep][location][0],
            "occupy"   : traffic_data[timestep][location][1],
            "speed"    : traffic_data[timestep][location][2]
        })      

print("Data dict length: ", len(data_dict))