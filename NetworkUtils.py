
from ast import Break
from sqlite3 import Timestamp
import networkx as nx
import numpy as np
import os
import pandas as pd
import datetime
import itertools
cur_dir = os.path.dirname(__file__)

def load_temporarl_edgelist(fname):
    data_path = os.path.join(cur_dir, fname)
    edgelist = open(data_path, "r")
    lines = list(edgelist.readlines())
    edgelist.close()
    cur_t = 0
    G_times = []
    G = nx.Graph()
    for i in range(0, len(lines)):
        if (i == 0):
            continue
        line = lines[i]
        values = line.split(",")
        t = int(values[0])
        u = int(values[1])
        v = int(values[2])
        #start a new graph with a new date
        if (t != cur_t):
            G_times.append(G)   #append old graph
            G = nx.Graph()  #create new graph
            cur_t = t 
        G.add_edge(u, v) 
    G_times.append(G)
    print ("maximum time stamp is " + str(len(G_times)))
    return G_times

def edge_count(fname):
    data_path = os.path.join(cur_dir, "data",  fname)
    edgelist = pd.read_csv(data_path, sep = ',', names=["time", "user_a", "user_b"])
    print(edgelist)
    edge_list = np.array([[edgelist["user_a"][0], edgelist["user_b"][0]]])
    edge_freq = [1]
    number_of_days = edgelist['time'].unique()
    for t1 in range(len(number_of_days)):
        t_edgelist = edgelist[(edgelist['time']==number_of_days[t1])]
        for i,line in t_edgelist.iterrows():

            u = line['user_a']
            v = line['user_b']

            p1 = np.where((edge_list == u))
            p2 = np.where((edge_list == v))
            uv = list(set(p1[0]) & set(p2[0]))
            
            if len(uv)==1 and edge_freq[uv[0]]<(t1+1):
                edge_freq[uv[0]] += 1
            elif len(uv)==0:
                edge_list = np.append(edge_list, [[u , v]], axis=0)
                edge_freq.append(1)

    edgelist = pd.DataFrame(edge_list, columns=['user_a','user_b'])
    edgelist['freq'] = pd.Series(edge_freq) 
    edgelist.to_csv("~/DiseaseModeling/data/Copenhagen/weighted_static_edgelist_daily_agg.edgelist",sep=' ', index=False, header=False)
    return 

def wifi_edgelist_creator(data, start_date, end_date):
    data_path = os.path.join(cur_dir,"data", data)
    data = pd.read_csv(data_path, compression='gzip',names=["user", "node", "login", "logout"])
    START_DATE = datetime.datetime.strptime(start_date, "%m/%d/%Y").date()
    END_DATE = datetime.datetime.strptime(end_date, "%m/%d/%Y").date()
    date_list = pd.date_range(start = START_DATE, end = END_DATE, freq="W")
    print("number of weeks : ", len(date_list))

    data ["login"] = pd.to_datetime(data["login"])
    data ["logout"] = pd.to_datetime(data["logout"])
    edit_n={}
    G_times = []
    ii = 0
    H = nx.Graph()
    community_list = []
    for day_num, day1 in enumerate(date_list):
        G = nx.Graph()
        day7 = day1 + datetime.timedelta(days=6)
        active_nodes = data[(((data["login"] >= day1) & (data["login"] <= day7))  # List of active nodes in a week
                                | ((data["logout"] >= day1) & (data["logout"] <= day7))
                                | ((data["login"] <= day1) & (data["logout"] >= day7)))][[
                                    "user","node"]]
        node_numbers = active_nodes["node"].unique()

        # only monitoring nodes that have been active in the first 20 days
        unique_active_users = active_nodes["user"].unique()
        if day_num < 20:
            for n in unique_active_users:
                community_list.append(n)
        else:
            unique_active_users = [n for n in unique_active_users if n in community_list]
        print(day_num, len(community_list))

        for i, nn in enumerate(node_numbers):
            each_node_connections = active_nodes[(active_nodes["node"]==nn)][["user"]]
            unique_nodes = each_node_connections["user"].unique()
            unique_nodes = [n for n in unique_nodes if n in unique_active_users]
            if len(unique_nodes)>1:
                daily_contacts = itertools.combinations(unique_nodes, 2)

                for dc in daily_contacts:
                    if dc[0] not in edit_n:
                        edit_n[dc[0]]=ii
                        ii+=1
                    if dc[1] not in edit_n:
                        edit_n[dc[1]]=ii
                        ii+=1
                    G.add_edge(edit_n[dc[0]], edit_n[dc[1]])
                    if H.has_edge(edit_n[dc[0]], edit_n[dc[1]]):
                        H[edit_n[dc[0]]][edit_n[dc[1]]]['weight'] +=1
                    else:
                        H.add_edge(edit_n[dc[0]], edit_n[dc[1]], weight=1)
        G_times.append(G)
    return H, G_times
