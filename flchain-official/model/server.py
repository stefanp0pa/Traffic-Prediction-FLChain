import torch
import flwr as fl
from torch import nn
import model.constants as constants
from datetime import datetime
from utils.utils import create_directory

class Server:
    
    def __init__(self, cluster, round):
        self.cluster = cluster
        self.round = round
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


    def save_model(self):
        save_directory = f"{constants.model_aggregated}/{self.cluster}_{self.round}"
        create_directory(save_directory)
        now = datetime.now()
        timestamp = now.timestamp()
        self.save_path = f"{save_directory}/{timestamp}.pth"
        model = self.__global_model
        model['signature'] = timestamp
        torch.save(model, self.save_path)


    def get_global_model(self):
        return self.__global_model


    def get_model(self):
        return self.__global_model


    def send_model(self):
        return self.__global_model
