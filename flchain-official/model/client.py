import torch.optim as optim
import model.constants as constants
import torch
import torch.nn as nn
import numpy as np
from model.GCN import GCN
from datetime import datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error
from utils.utils import scaled_Laplacian, cheb_polynomial, create_directory
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

    def __init__(self, node, cluster, cluster_index, adj_matrix, data, DEVICE, round) -> None:
        self.__node = node
        self.__adj_matrix = adj_matrix
        self.DEVICE = DEVICE
        self.cluster = cluster
        self.cluster_index = cluster_index - 1
        self.__train_loader, self.__train_target_tensor =  create_dataloaders('train_x', 'train_target', data, DEVICE)
        self.__test_loader, self.__test_target_tensor = create_dataloaders('test_x', 'test_target', data, DEVICE)
        self.__test_target_tensor = self.__test_target_tensor.cpu().numpy()
        self.__mean = data['mean']
        self.__std = data['std']
        self.file_name = f'tracking_nodes/{node}_{cluster}'
        self.file_size = f'tracking_files/{node}_{cluster}'
        self.round = round
        create_directory('tracking_nodes')
        create_directory('tracking_files')
        self.create_model()
    
    
    def create_model(self):
        L_tilde = scaled_Laplacian(self.__adj_matrix)
        cheb = []
        if self.cluster_index < 0:
            cheb = [i for i in cheb_polynomial(L_tilde, constants.K)]
        else: 
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


    def remove_signature(self, model):
        if 'signature' in model:
            del model['signature']
        return model


    def load_model(self, local_model, global_model):
        local_model = self.remove_signature(local_model)
        global_model = self.remove_signature(global_model)
        self.model.load_state_dict(local_model)
        self.update_model(global_model)
        self.best_model = copy.deepcopy(self.model)


    def evaluate(self, test_data = None):
        test_loader = self.__test_loader
        if test_data is not None:
            test_loader = test_data

        self.model.train(False)
        prediction = []
        error = 0

        with torch.no_grad():
            for batch_data in test_loader:
                encoder_inputs, labels = batch_data
                if test_data is None:
                    encoder_inputs = encoder_inputs.unsqueeze(1)
                
                output = self.model(encoder_inputs)
                prediction.append(output.detach().cpu().numpy())
            
            prediction = np.concatenate(prediction, 0)
            error = mean_absolute_error(self.__test_target_tensor.reshape(-1, 1), prediction.reshape(-1, 1))
        return error


    def on_device(self, DEVICE):
        self.model.DEVICE = DEVICE
        self.model.to(DEVICE)
        for layer in self.model.Layer1:
            layer.cheb_conv.DEVICE = DEVICE
            for t in layer.cheb_conv.Theta:
                t.to(DEVICE)
        
        for layer in self.model.BlockList:
            layer.cheb_conv.DEVICE = DEVICE
            for t in layer.cheb_conv.Theta:
                t.to(DEVICE)


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
        self.model.train(True)

        for epoch in range(0, constants.epochs):
            self.model.train()

            training_loss = 0
            for batch_index, batch_data in enumerate(self.__train_loader):
                encoder_inputs, labels = batch_data
                encoder_inputs = encoder_inputs.unsqueeze(1)
                optimizer.zero_grad()
                outputs = self.model(encoder_inputs)
                loss = self.criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                training_loss += loss.item()

            avg_loss = training_loss/len(self.__train_loader)
            if best_acc > avg_loss:
                best_acc = avg_loss
                self.best_model = copy.deepcopy(self.model)

            text = f"Round: {self.round} Node: {self.get_node()}, Cluster: {self.get_cluster()} Epoch:{epoch} loss:{training_loss/len(self.__train_loader)}\n"
            with open(self.file_name, 'a') as file:
                file.write(text)
            print(text, end='')
        self.save_best_model()


    def save_best_model(self, type_file = 'footprint'):
        save_directory = f"{constants.model_save_directory}/{self.__node}_{self.cluster}"
        create_directory(save_directory)
        now = datetime.now()
        timestamp = now.timestamp()
        self.save_path = f"{save_directory}/{timestamp}.pth"
        model = self.best_model.state_dict()
        model['signature'] = timestamp
        torch.save(model, self.save_path)
        file_size = os.path.getsize(self.save_path)
        with open(self.file_size, 'a') as file:
            file.write(f'Round: {self.round} {type_file} size has: {file_size} Bytes\n') 
        

    def get_node(self):
        return self.__node


    def get_cluster_index(self):
        return self.cluster_index
    
    def get_cluster(self):
        return self.cluster


    def send_current_model(self):
        param = {}
        current_model = self.best_model.state_dict() 
        for layer in self.best_model.state_dict():
            if 'Layer1' not in layer:
                param[layer] = copy.deepcopy(current_model[layer])

        return param
    

    def get_last_model_file(self):
        return self.save_path
