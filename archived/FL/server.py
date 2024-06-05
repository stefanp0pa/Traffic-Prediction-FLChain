import torch
import flwr as fl
from torch import nn
import copy

class Server:
    
    def __init__(self, port, leader):
        self.__port = port
        self.__leader = leader
        self.__global_model = None
        self.__local_model = []

    def get_client_model(self, model):
        self.__local_model.append(model)

    def aggregate(self):
        self.__global_model = {}
        n = len(self.__local_model)
        layers_name = self.__local_model[0].keys()
        
        for layer in layers_name:
            self.__global_model[layer] = torch.zeros_like(self.__local_model[0][layer])

            for model in self.__local_model:
                self.__global_model[layer] += model[layer]
            self.__global_model[layer] /= n

        self.__local_model = []


    def get_global_model(self):
        return self.__global_model

    def get_model(self):
        return self.__global_model

    def get_leader(self):
        return self.__leader

    def get_port(self):
        return self.__port
    
    def send_model(self):
        return self.__global_model
