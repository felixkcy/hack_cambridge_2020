from flask import Flask, render_template, request, url_for

import random, json
import pandas as pd
import numpy as np
import glob
M=4000
A=181.4
B=2.42
C=0.62


app = Flask(__name__)

@app.route('/',  methods=['GET'])
def form():
    json_helper = {}
    json_helper['aggression'] = get_aggression(vel_arr[0:4])
    order = np.argsort(json_helper['aggression'])
    json_helper["aggression"] = list(np.array(json_helper["aggression"])[order])
    json_helper['trace'] = get_trace(fuel_cons[0:4], order)
    json_helper['max_fuel'] = max([max(i) for i in fuel_cons[0:4]])
    print(json_helper['max_fuel'])
    print(json_helper['trace'][0])
    print(json_helper['aggression'])
    json_object = json.dumps(json_helper)
    return render_template('index.html' , s_data=json_object)

@app.route('/acceleration',  methods=['GET'])
def acceleration():
    return render_template('index2.html')

def get_aggression(velocities):
    res = [aggressive(i) for i in velocities]
    return res

def aggressive(v):
    v = np.array(v)
    a=np.gradient(v)
    av=a*v
    agg=abs((1/M)*((A*v.sum()+B*(v**2).sum()+C*(v**3).sum()+M*av.sum())/v.sum())*(8.9/np.mean(v)))
    return np.round(agg * 20, decimals=2)

def get_trace(array, order):
    res = []

    print([len(a) for a in array])

    for idx in range(100):
        part = {"x": idx}
        for j in order:
            part["trace_{}".format(j)] = array[j][idx]
        res.append(part)
    return res


if __name__ == '__main__':

    filenames = glob.glob("VED_DynamicData_Part1/*")
    vel_arr = []
    fuel_cons = []
    for filename in filenames:
        df = pd.read_csv(filename)
        df["Fuel Rate[L/hr]"] = pd.to_numeric(df["Fuel Rate[L/hr]"])
        df = df[pd.notna(df["Fuel Rate[L/hr]"])]
        df = df[df["Fuel Rate[L/hr]"] > 0]
        df["Vehicle Speed[km/h]"] = pd.to_numeric(df["Vehicle Speed[km/h]"])
        for vehId in df["VehId"].unique():
            veh1 = df[df["VehId"] == vehId].reset_index()
            vel = list(np.array(veh1["Vehicle Speed[km/h]"])*1000/3600)
            fuel = list(np.array(veh1["Vehicle Speed[km/h]"]))
            vel_arr.append(list(vel))
            fuel_cons.append(list(np.array(fuel)/np.mean(vel)))
    app.run(debug=True)
