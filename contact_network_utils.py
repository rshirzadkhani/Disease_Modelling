import numpy as np
import networkx as nx
import random
import pandas as pd
import statistics 
from model.Constants import SEIR_COMPARTMENTS
from NetworkedSEIR import NetworkedSEIR

def construct_network(static_graph, temporal_graph, sir_0):
    states = {}
    for i in static_graph.nodes:
        states[i] = {'state': 'S'}
    if temporal_graph is not None:
        cc = sorted(nx.connected_components(temporal_graph), key=len, reverse=True)
    else:
        cc = sorted(nx.connected_components(static_graph), key=len, reverse=True)
    node_indices = np.random.choice(list(cc[0]), np.sum(sir_0), replace=False)
    for i in np.arange(0, sir_0[0]):
        states[node_indices[i]] = {'state': 'E'}
    for i in np.arange(sir_0[0], sir_0[0] + sir_0[1]):
        states[node_indices[i]] = {'state': 'I_S'}
    for i in np.arange(sir_0[0] + sir_0[1], sir_0[0] + sir_0[1] + sir_0[2]):
        states[node_indices[i]] = {'state': 'I_A'}
    nx.set_node_attributes(static_graph, states)
    return static_graph

def run_with_network(t, G, temp_G, transmissibility, sigma, gamma, symptomatic_rate, sir_0, seed, all_nodes, removing_nodes, scale=1, npi=None, t_apply_npi=None, t_open_up=None, npi_reopen =None, **kwargs):
    random.seed(seed)
    np.random.seed(seed)
    first_temporal_graph = None
    if temp_G is not None:
        first_temporal_graph = temp_G[0]
    graph = G.copy()
    graph = construct_network(graph, first_temporal_graph, sir_0)
    seir = np.zeros(( t, len(SEIR_COMPARTMENTS)))
    seir, new_cases, cum_cases = network_exp_with_seed(transmissibility, sigma, symptomatic_rate, gamma, t, graph, temp_G,all_nodes,removing_nodes, scale )
    return seir, new_cases, cum_cases
    
def network_exp_with_seed(transmissibility, sigma, symptomatic_rate, gamma, t, graph, temp_G,all_nodes,removing_nodes, weight=False, scale=1):
    model1 = NetworkedSEIR(transmissibility=transmissibility, sigma=sigma, symptomatic_rate=symptomatic_rate,
                           gamma=gamma, duration=t, weight=weight, scale=scale, all_nodes=all_nodes,removing_nodes=removing_nodes)
    seir, new_cases, cum_cases = model1.run(graph, temp_G)
    return seir, new_cases, cum_cases

def delete_disconnected_components(graph):
    cc = sorted(nx.connected_components(graph), key=len, reverse=True)
    graph1 = graph.subgraph(max(nx.connected_components(graph), key=len))
    removing_nodes = []
    if len(cc) > 1:
        for i in range(1, len(cc)):
            a1 = list(cc[i])
            for n in a1:
                removing_nodes.append(n)
    return graph1, removing_nodes

def matching_degree_top_edge(main_G, degree):
    edges = sorted(main_G.edges(data=True), key=lambda t: t[2].get('weight', 1), reverse=True)
    G_E = MST(main_G)
    curr_degree = G_E.number_of_edges() *2 / main_G.number_of_nodes()
    j = 0
    while round(curr_degree) <= degree :
        new_edge = edges[j]
        G_E.add_edge(new_edge[0], new_edge[1])
        curr_degree = G_E.number_of_edges() *2 / main_G.number_of_nodes()
        j += 1
    return G_E

def matching_degree_top_node(main_G, degree):
    degree_sequence = pd.DataFrame(main_G.degree, columns=["node_id", "degree"])
    degree_sequence = degree_sequence.sort_values(by=["degree"], ascending=False)
    G_D = MST(main_G)
    curr_degree = G_D.number_of_edges() *2 / main_G.number_of_nodes()
    j = 0
    while round(curr_degree) <= degree :
        selected_node = degree_sequence["node_id"].iloc[j]
        new_edges = main_G.edges(selected_node)
        G_D.add_edges_from(new_edges)
        curr_degree = G_D.number_of_edges() *2 / main_G.number_of_nodes()
        j += 1
    return G_D

def MST(G):
    T=nx.minimum_spanning_tree(G)
    return T

def network_ave_degree( static_G, temporal_G, t, all_nodes):
    degree = []
    if temporal_G is None:
        num_edges = static_G.number_of_edges()
        degree.append(num_edges *2 / all_nodes)
    else:
        for t1 in range(t):
            num_edges = temporal_G[t1].number_of_edges()
            degree.append(num_edges*2/ all_nodes)
    return round(statistics.mean(degree))