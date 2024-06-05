import flwr as fl
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import constants as constants
from server import Server
from client import Client
from utils.utils import adjancency_matrix_cluster, prepare_training
from circles import create_infrastructure
import os

torch.cuda.device_count()
torch.cuda.is_available()
os.environ["CUDA_VISIBLE_DEVICES"] = constants.ctx
USE_CUDA = torch.cuda.is_available()
DEVICE = torch.device('cuda:0')
print("CUDA:", USE_CUDA, DEVICE)

graph, leaders = create_infrastructure()
port = constants.server_start_port
servers = []
clients = []


def init_fed(leader):
    global port

    cluster_elements = [source for source, attribute in graph.items() if leader in attribute['leaders']]
    A = adjancency_matrix_cluster("../dataset/roads.csv", cluster_elements)
    
    cluster_server = Server(port, leader)
    servers.append(cluster_server)

    for index, node in enumerate(cluster_elements):
        new_client = Client(node, port, A, index, DEVICE)
        clients.append(new_client)
    
    port += 1


def train_cluster(leader):
    server = [sv for sv in servers if sv.get_leader() == leader]
    
    if not server:
        return -1

    server = server[0]
    cluster_clients = [clnt for clnt in clients if clnt.get_server_port() == server.get_port()]
    for round in range(0, constants.rounds):
        print(f"Round:{round}")
        global_model = server.get_global_model()
        
        for clnt in cluster_clients:    
            if global_model is not None:
                clnt.update_model(global_model)

            clnt.train()
            param = clnt.send_current_model()
            server.get_client_model(param) 
        
        server.aggregate()


if __name__ == "__main__":
    init_fed(141)
    init_fed(0)
    train_cluster(141)
   