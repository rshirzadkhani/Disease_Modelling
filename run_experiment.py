import networkx as nx
import numpy as np
import os
from model.Constants import SEIR_COMPARTMENTS
from model.plotting_utils import plot_for_contact_network
from model.utils import compute_mean_confidence_interval
from contact_network_utils import *
from NetworkUtils import *
from model.Network import Network, Data
from LoadNetwork import load_contact_network, load_data
cur_dir = os.path.dirname(__file__)

def contact_network_exp(data, network):
    BETA = 0.78
    # 1 / days latent
    SIGMA = 1/5
    # recovery rate = 1 / days infected
    GAMMA = 1/14
    # the probability of an exposed become symptomatic infected
    SYMPTOMATIC_RATE = 0.6
    seeds = [3, 6, 13, 20, 21, 26, 43, 67, 97, 100]
    num_seeds = len(seeds)

    e_0 = 3
    i_0 = 2
    i_s_0 = int(np.round(i_0 * SYMPTOMATIC_RATE))
    i_a_0 = i_0 - i_s_0
    sir_0 = [e_0, i_s_0, i_a_0]   
    G, temp_G, T, all_nodes = load_data(data)
    
    temporal_density = network_ave_degree(G, temp_G, T, all_nodes)
    TRANSMISSIBILITY = BETA / temporal_density
    G, removing_nodes = delete_disconnected_components(G)
    all_nodes -= len(removing_nodes)
    for ntw in network:
        static_G, temporal_G = load_contact_network(ntw, G, temp_G, 0)
        Network_results = np.zeros((num_seeds, T+1, len(SEIR_COMPARTMENTS)))
        New_Network_results = np.zeros((num_seeds, T+1, len(SEIR_COMPARTMENTS)-1))
        Cum_Network_results = np.zeros((num_seeds, T+1, 2))
        for seed_idx, seed in enumerate(seeds):
            if ntw.name in [Network.ER.name, Network.BA.name]:
                static_G, temporal_G = load_contact_network(ntw, G, temp_G, seed)

            Network_results[seed_idx] , New_Network_results[seed_idx], Cum_Network_results[seed_idx] = run_with_network(T, static_G, temporal_G, 
                            TRANSMISSIBILITY, SIGMA, GAMMA, SYMPTOMATIC_RATE, sir_0, seed, all_nodes, removing_nodes)
        np.save("./output/"+data.name +"_" +ntw.name+"_active_cases", Network_results)
        np.save("./output/"+data.name +"_" +ntw.name+"_new_cases", New_Network_results)
        np.save("./output/"+data.name +"_" +ntw.name+"_cum_cases", Cum_Network_results)

def plot_graphs(seir, dates, filename, compartment=None, networks=None, t_match=0, t_reopen=0):
    mean_lst = []
    ci_lst = []
    seir = np.expand_dims(seir, axis=2)
    seir = np.expand_dims(seir, axis=4)
    for idx in range(seir.shape[0]):
        mean, ci = compute_mean_confidence_interval(seir[idx])
        mean = np.squeeze(mean, axis=0)
        ci = np.squeeze(ci, axis=0)
        mean_lst.append(mean)
        ci_lst.append(ci)
    mean_lst=np.squeeze(mean_lst)
    ci_lst = np.squeeze(ci_lst) 
    plot_for_contact_network(dates, mean_lst, ci_lst, filename, labels=networks)


def plot_experiments(data, network):
    print(data)
    d = {}
    with open("./output/"+data.name+"_stats.txt") as f:
        for line in f:
            (key, val) = line.split(" ")
            d[key] = int(val)
    density = []
    active_infected = []
    new_infected = []
    cum_infected = []
    for ntw in network:
        if ntw.name == Network.STATIC.name:
            density.append(d["static_deg"])
        else:
            density.append(d["dynamic_deg"])
        actives = np.load("./output/"+ data.name + "_" + ntw.name + "_active_cases.npy")
        new = np.load("./output/" + data.name + "_" + ntw.name + "_new_cases.npy")
        cum = np.load("./output/"+ data.name + "_" + ntw.name + "_cum_cases.npy")

        active_infected.append(actives[:,:,2])
        new_infected.append(new[:,:,1])
        cum_infected.append(cum[:,:,0])
    
    dates = list(range(d["T"]+1)) 
    graph_label = [("Full static"), ("DegMST"),
                        ("EdgeMST"),("Dynamic")]

    plot_graphs(np.array([new_infected[0],new_infected[1],new_infected[2], new_infected[3]]), 
                            dates, "./plots/"+data.name+"_new_cases", networks=graph_label)

    plot_graphs(np.array([active_infected[0],active_infected[1],active_infected[2], active_infected[3]]), 
                            dates, "./plots/"+data.name+"_active_cases", networks=graph_label)

    plot_graphs(np.array([cum_infected[0],cum_infected[1],cum_infected[2], cum_infected[3]]), 
                        dates, "./plots/"+data.name+"_cumulative_cases", networks=graph_label) 

if __name__ == "__main__":
    contact_network_exp(data = Data.COPENHAGEN , network = [Network.STATIC, Network.DegMST,
                     Network.EdgeMST, Network.TEMPORAL])

    plot_experiments(data = Data.COPENHAGEN , network = [Network.STATIC, Network.DegMST,
                     Network.EdgeMST,Network.TEMPORAL])