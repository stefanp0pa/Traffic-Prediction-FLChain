import flwr as fl
import torch.optim as optim
import constants
import torch
import torch.nn as nn
import numpy as np
from utils.utils import cheb_polynomial, scaled_Laplacian, create_directory
from models.GCN import GCN
from datetime import datetime
import copy
import os

def create_dataloaders(field, target, data, DEVICE, shuffle=False):
        train = data[field]
        train_target = data[target]
        tensor = torch.from_numpy(train).type(torch.FloatTensor).to(DEVICE) 
        target_tensor = torch.from_numpy(train_target).type(torch.FloatTensor).to(DEVICE)
        dataset = torch.utils.data.TensorDataset(tensor, target_tensor)
        loader = torch.utils.data.DataLoader(dataset, batch_size=constants.batch_size, shuffle=shuffle)

        return loader, target_tensor

class Client:

    def __init__(self, node, server_port, adj_matrix, cluster_index, DEVICE) -> None:
        self.__server_port = server_port
        self.__node = node
        self.DEVICE = DEVICE
        self.__adj_matrix = adj_matrix
        self.cluster_index = cluster_index
        data = np.load(f"data_node/{self.__node}.npz")
        self.__train_loader, self.__train_target_tensor =  create_dataloaders('train_x', 'train_target', data, DEVICE)
        self.__test_loader, self.__test_target_tensor = create_dataloaders('test_x', 'test_target', data, DEVICE)
        self.create_model()


    def create_model(self):
        L_tilde = scaled_Laplacian(self.__adj_matrix)
        cheb = [np.expand_dims(i[:, self.cluster_index], axis=0) for i in cheb_polynomial(L_tilde, constants.K)]
        cheb_polynomial_layer1 = [torch.from_numpy(i).type(torch.FloatTensor).to(self.DEVICE) for i in cheb]
        cheb_polynomials = [torch.from_numpy(i).type(torch.FloatTensor).to(self.DEVICE) for i in cheb_polynomial(L_tilde, constants.K)]
        model = GCN(self.DEVICE, constants.nb_block, constants.in_channels, constants.K, constants.nb_chev_filter, constants.nb_time_filter, constants.num_of_hours, cheb_polynomial_layer1, cheb_polynomials, constants.num_for_predict, constants.len_input)

        for p in model.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
            else:
                nn.init.uniform_(p)
        
        self.model = model
        self.best_model = copy.deepcopy(model)


    def update_model(self, global_model):
        param = {}
        current_model = self.best_model.state_dict() 
        
        for layer in current_model:
            if 'Layer1' not in layer:
                param[layer] = copy.deepcopy(global_model[layer])
            else:
                param[layer] = copy.deepcopy(current_model[layer])
        self.model.load_state_dict(param)

    def train(self):
        self.criterion = nn.L1Loss().to(self.DEVICE)
        optimizer = optim.Adam(self.model.parameters(), lr=constants.learning_rate)
        best_acc = np.inf

        for epoch in range(0, constants.epochs):
            self.model.train()

            training_loss = 0
            for batch_index, batch_data in enumerate(self.__train_loader):
                encoder_inputs, labels = batch_data
                encoder_inputs = encoder_inputs.unsqueeze(1)
                optimizer.zero_grad()
                outputs = self.model(encoder_inputs)
                outputs = outputs[:, self.cluster_index]
                loss = self.criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                training_loss += loss.item()

            avg_loss = training_loss/len(self.__train_loader)
            if best_acc > avg_loss:
                best_acc = avg_loss
                self.best_model = copy.deepcopy(self.model)

            print(f"Epoch:{epoch} loss:{training_loss/len(self.__train_loader)}")
        
        save_path = f"{constants.model_save_directory}/{self.__node}_{self.__server_port}"
        create_directory(save_path)
        now = datetime.now()
        timestamp = now.timestamp()
        torch.save(self.best_model.state_dict(), f"{save_path}/{timestamp}")
        

    def get_node(self):
        return self.__node


    def send_current_model(self):
        param = {}
        current_model = self.best_model.state_dict() 
        for layer in self.best_model.state_dict():
            if 'Layer1' not in layer:
                param[layer] = copy.deepcopy(current_model[layer])

        return param


    def get_server_port(self):
        return self.__server_port


    def get_matrix(self):
        return self.__adj_matrix