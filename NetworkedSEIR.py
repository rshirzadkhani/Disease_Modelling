# from typing_extensions import Self
import numpy as np
import random
from model.Constants import SEIR_STATES, SEIR_COMPARTMENTS


class NetworkedSEIR:

    def __init__(self, transmissibility=0.6, sigma=0.5, symptomatic_rate=0.5, gamma=0.2, duration=30, weight=False, scale=1,all_nodes=0,removing_nodes=None, no_npi_nodes=set()):
        self.transmissibility = transmissibility
        self.sigma = sigma
        self.symptomatic_rate = symptomatic_rate
        self.gamma = gamma
        self.duration = duration
        self.seir = None
        self.active_infected = set()
        self.scale = scale
        self.no_npi_nodes = []
        self.transmissibility_strengths = [1, 0.8, 0.6]
        self.vary_transmissibility = False
        self.quarantine = False
        self.hubs_to_keep = set()
        self.removed_edges = []
        self.reopened = False
        self.new_seir = [[0,0,0,0]]
        self.cumulative_seir = [[0,0]]
        self.new_cases=[]
        self.weight=weight
        self.total_population = all_nodes
        self.removing_nodes = removing_nodes

    def run(self, static_graph, temporal_graph):
        self.reset(static_graph)
        for t in range(self.duration):
            if temporal_graph is not None:
                graph = temporal_graph[t]
                graph.remove_nodes_from(self.removing_nodes)
            else:
                graph = static_graph
            new_exposed = self.get_new_exposed(graph, t)
            new_infected = self.get_new_infected(t)
            new_recovered = self.get_new_recovered(t)
            self.update_seir(t, new_exposed, new_infected, new_recovered)
            self.update_new( new_exposed, new_infected, new_recovered)
            self.update_cumulative_seir(t, new_infected, new_recovered)
        return self.to_seir()

    def reset(self, graph):
        self.seir = []
        compartments = [set(), set(), set(), set(), set()]
        for x, y in graph.nodes(data=True):
            compartments[SEIR_STATES.index(y['state'])].add(x)
        self.seir.append(compartments)
        self.active_infected = self.seir[0][2].union(self.seir[0][3])

    def get_new_exposed(self, graph, t):
        susceptible = self.seir[t][0]
        contacts = []
        p1 = []
        inactivate = set()
        for i in self.active_infected:
            if i in graph.nodes:
                if set(graph.neighbors(i)).isdisjoint(susceptible):
                    continue
                else:
                    if self.scale == 1:
                        contacts += graph.neighbors(i)
                        if self.weight is True:
                            p1 += [(graph.get_edge_data(*e)['weight']) for e in graph.edges(i)]
                    else:
                        neighbours = list(graph.neighbors(i))
                        neighbours_exposed = random.sample(neighbours, int(len(neighbours) * self.scale))
                        contacts += neighbours_exposed
        success = np.random.uniform(0, 1, len(contacts)) > self.transmissibility
        success_contact = list(np.extract(success, contacts))
        return set(success_contact).intersection(susceptible)

    def get_new_recovered(self, t):
        infected = self.seir[t][2]
        num_recovered = int(self.gamma * (len(infected)))
        new_recovered = set(np.random.choice(list(infected), num_recovered, replace=False))
        return new_recovered

    def get_new_infected(self, t):
        exposed = self.seir[t][1]
        num_infected = int(self.sigma * len(exposed))
        new_infected = set(np.random.choice(list(exposed), num_infected, replace=False))
        return new_infected    

    def update_seir(self, t, new_exposed, new_infected, new_recovered):
        susceptible_next = self.seir[t][0].difference(new_exposed)
        exposed_next = self.seir[t][1].union(new_exposed).difference(new_infected)
        infected_next = self.seir[t][2].union(new_infected).difference(new_recovered)
        recovered_next = self.seir[t][3].union(new_recovered)
        next_seir = [susceptible_next, exposed_next, infected_next, recovered_next]
        self.active_infected = self.active_infected.union(new_infected)\
            .difference(new_recovered)
        self.seir.append(next_seir)

    def update_cumulative_seir(self, t, new_infected, new_recovered):
        cum_infected = self.cumulative_seir[t][0]+len(new_infected)
        cum_recovered = self.cumulative_seir[t][1]+len(new_recovered)
        self.cumulative_seir.append([cum_infected,cum_recovered])

    def to_seir(self):
        seir_0 = np.zeros((self.duration+1, len(SEIR_COMPARTMENTS)))
        seir_new = np.zeros((self.duration+1, len(SEIR_COMPARTMENTS)-1))
        seir_cum = np.zeros((self.duration+1, 2))
        for t in range(self.duration+1):
            s, e, i, r = len(self.seir[t][0]), \
                         len(self.seir[t][1]), \
                         len(self.seir[t][2]), \
                         len(self.seir[t][3])
            seir_0[t] = [s, e, i, r]

            e_n, i_n, r_n = self.new_seir[t][1], \
                self.new_seir[t][2], \
                self.new_seir[t][3]
            seir_new[t] = [e_n, i_n, r_n]

            i_c = self.cumulative_seir[t][0]
            r_c = self.cumulative_seir[t][1]
            seir_cum[t] = [i_c, r_c]
        return seir_0/ self.total_population, seir_new/ self.total_population , seir_cum /self.total_population# np.expand_dims(np.sum(seir_0, axis=1), 1)        

    def update_new(self, new_exposed, new_infected, new_recovered):
        num_new_exposed = len(new_exposed)
        num_new_infected = len(new_infected)
        num_new_recovered = len(new_recovered)
        num_new_susceptable = -1*(num_new_exposed)
        new_seir = [num_new_susceptable, num_new_exposed, num_new_infected, num_new_recovered]
        self.new_seir.append(new_seir)