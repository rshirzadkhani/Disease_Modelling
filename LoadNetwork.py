from NetworkUtils import *
from Safegraph_analyse import safegraph
from model.Network import Network, Data
import random
from contact_network_utils import matching_degree_top_edge, matching_degree_top_node, network_ave_degree
import networkx as nx
cur_dir = os.path.dirname(__file__)
def load_data(data):
    if data.name == Data.COPENHAGEN.name:
        data_path = os.path.join(cur_dir,"data","Copenhagen", "weighted_static_edgelist_daily_agg.edgelist")
        G = nx.read_weighted_edgelist(data_path, nodetype=int)
        temp_G = load_temporarl_edgelist("./data/Copenhagen/dynamic_network_daily_agg.csv")

    elif data.name == Data.WORKPLACE.name:
        data_path = os.path.join(cur_dir,"data","workplace", "weighted_edgelist_hourly_agg.edgelist")
        G = nx.read_weighted_edgelist(data_path, nodetype=int)
        temp_G = load_temporarl_edgelist("./data/workplace/dynamic_network_hourly_agg.csv.gz")

    elif data.name == Data.LYONSCHOOL.name:
        data_path = os.path.join(cur_dir,"data","Lyonschool", "weighted_edgelist_hourly_agg.edgelist")
        G = nx.read_weighted_edgelist(data_path, nodetype=int)
        temp_G = load_temporarl_edgelist("./data/Lyonschool/dynamic_network_hourly_agg.csv.gz")

    elif data.name == Data.HIGHSCHOOL.name:
        data_path = os.path.join(cur_dir,"data","Highschool", "weighted_edgelist_hourly_agg.edgelist")
        G = nx.read_weighted_edgelist(data_path, nodetype=int)
        temp_G = load_temporarl_edgelist("./data/Highschool/dynamic_network_hourly_agg.csv.gz")

    elif data.name == Data.COPENHAGEN.name:
        data_path = os.path.join(cur_dir,"data","sfhh", "weighted_edgelist_hourly_agg.edgelist")
        G = nx.read_weighted_edgelist(data_path, nodetype=int)
        temp_G = load_temporarl_edgelist("./data/sfhh/dynamic_network_hourly_agg.edgelist")

    elif data.name == Data.WIFI.name:
        G, temp_G = wifi_edgelist_creator("./wifi/wifi_raw_data_3.csv.gz", "1/1/2009", "3/7/2010")

    elif data.name == Data.SAFEGRAPH.name:
        weeks = ['2020-03-09', '2020-03-16', '2020-03-23', '2020-03-30'
                , '2020-04-06', '2020-04-13', '2020-04-20', '2020-04-27'
                , '2020-05-04', '2020-05-11', '2020-05-18', '2020-05-25'
                , '2020-06-01', '2020-06-08', '2020-06-15', '2020-06-22'
                , '2020-06-29', '2020-07-06', '2020-07-13', '2020-07-20'
                , '2020-07-27', '2020-08-03', '2020-08-10', '2020-08-17'
                , '2020-08-24', '2020-08-31', '2020-09-07', '2020-09-14'
                , '2020-09-21']
        nn = safegraph(weeks)
        temp_G, static_G = nn.run()
        G = static_G
    T = len(temp_G)
    dates = list(range(0, T+1))
    all_nodes = G.number_of_nodes()
    return G, temp_G, T, all_nodes


def load_contact_network(network, G, temp_G, seed):
    random.seed(seed)
    np.random.seed(seed)
    all_nodes = G.number_of_nodes()
    degree = network_ave_degree(G, temp_G, len(temp_G), all_nodes)

    if network.name == Network.EdgeMST.name:
        temporal_G = None
        all_nodes = G.number_of_nodes()
        degree = network_ave_degree(G, temp_G, len(temp_G), all_nodes)
        static_G = matching_degree_top_edge(G, degree)

    elif network.name == Network.DegMST.name:
        temporal_G = None
        all_nodes = G.number_of_nodes()
        degree = network_ave_degree(G, temp_G, len(temp_G), all_nodes)
        static_G = matching_degree_top_node(G, degree)

    elif network.name == Network.TEMPORAL.name:
        temporal_G = temp_G
        static_G = G

    elif network.name == Network.ER.name:
        n = G.number_of_nodes()
        p = degree / (n-1)
        static_G = nx.fast_gnp_random_graph(n, p)
        temporal_G = None

    elif network.name == Network.BA.name:
        temporal_G = None
        p = 1
        for m in np.arange(2,100, 1):
            syn_G = nx.dual_barabasi_albert_graph(all_nodes, m1=m, m2=1, p=1)
            g_degree = network_ave_degree(syn_G, temporal_G, len(temp_G), all_nodes)
            if g_degree >= degree:
                best_m = m
                break
        static_G = nx.barabasi_albert_graph(all_nodes, best_m)
        
    elif network.name == Network.STATIC.name:
        temporal_G = None
        static_G = G

    return static_G, temporal_G