import os
import numpy as np
import torch
import torch.utils.data
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from scipy.sparse.linalg import eigs
import pandas as pd

def re_normalization(x, mean, std):
    x = x * std + mean
    return x

def get_adjacency_matrix(distance_df_filename):

    df = pd.read_csv(distance_df_filename)
    from_max_node_value = df['from'].max()
    to_max_node_value = df['to'].max()
    no_nodes = max(to_max_node_value, from_max_node_value) + 1

    A = np.zeros((no_nodes, no_nodes), dtype=np.float32)
    distanceA = np.zeros((no_nodes, no_nodes), dtype=np.float32)
    
    for _, row in df.iterrows():
        from_node, to_node, cost = row
        from_node = int(from_node)
        to_node = int(to_node)
        A[from_node, to_node] = 1
        A[to_node, from_node] = 1
        distanceA[from_node, to_node] = cost
        distanceA[to_node, from_node] = cost

    return A, distanceA, no_nodes


def adjancency_matrix_cluster(distance_df_filename, cluster_elements):
    df = pd.read_csv(distance_df_filename)
    no_nodes = len(cluster_elements)
    A = np.zeros((no_nodes, no_nodes), dtype=np.float32)

    for _, row in df.iterrows():
        from_node, to_node, cost = row
        from_node = int(from_node)
        to_node = int(to_node)
        if to_node in cluster_elements and from_node in cluster_elements:
            from_node_index = cluster_elements.index(from_node)
            to_node_index = cluster_elements.index(to_node)
            A[from_node_index, to_node_index] = 1
            A[to_node_index, from_node_index] = 1
    return A

def scaled_Laplacian(W):
    # L = D-W
    # lambda_max = eigenvalue
    # L^ = 2L/lambda_max - I

    D = np.diag(np.sum(W, axis=1))

    L = D - W

    lambda_max = eigs(L, k=1, which='LR')[0].real

    return (2 * L) / lambda_max - np.identity(W.shape[0])


def cheb_polynomial(L_tilde, K):
    # T0 = 1
    # T1 = L
    # T(n+1) = 2LTn -  T(n-1)
    N = L_tilde.shape[0]

    cheb_polynomials = [np.identity(N), L_tilde.copy()]

    for i in range(2, K):
        cheb_polynomials.append(2 * L_tilde * cheb_polynomials[i - 1] - cheb_polynomials[i - 2])

    return cheb_polynomials


def prepare_training(graphdata_file, batch_size, DEVICE):
    
    data = np.load(graphdata_file)
    mean = data['mean'][:, :, [0, 2], :]
    std = data['std'][:, :, [0, 2], :] 
    
    def create_dataloaders(field, target, shuffle=False):
        # train = data[field][:, node, [0, 2], :]
        # train_target = data[target][:, node, :]
        train = data[field][:, :, [0, 2], :]
        train_target = data[target]
        tensor = torch.from_numpy(train).type(torch.FloatTensor).to(DEVICE) 
        target_tensor = torch.from_numpy(train_target).type(torch.FloatTensor).to(DEVICE)
        dataset = torch.utils.data.TensorDataset(tensor, target_tensor)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

        return loader, target_tensor
        
    train_loader, train_target_tensor =  create_dataloaders('train_x', 'train_target')
    test_loader, test_target_tensor = create_dataloaders('test_x', 'test_target')

    # print('train_target:', train_target_tensor.size())
    # print('test:', test_target_tensor.size())
    
    return train_loader, train_target_tensor, test_loader, test_target_tensor, mean, std



def compute_val_loss_mstgcn(net, val_loader, criterion,  masked_flag,missing_value, epoch, limit=None):
    net.train(False)

    with torch.no_grad():

        val_loader_length = len(val_loader)

        tmp = []

        for batch_index, batch_data in enumerate(val_loader):
            encoder_inputs, labels = batch_data
            outputs = net(encoder_inputs)
            if masked_flag:
                loss = criterion(outputs, labels, missing_value)
            else:
                loss = criterion(outputs, labels)

            tmp.append(loss.item())
            if batch_index % 100 == 0:
                print('validation batch %s / %s, loss: %.2f' % (batch_index + 1, val_loader_length, loss.item()))
            if (limit is not None) and batch_index >= limit:
                break

        validation_loss = sum(tmp) / len(tmp)
    return validation_loss


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)



def predict_and_save_results_mstgcn(net, data_loader, data_target_tensor, global_step, metric_method,_mean, _std, params_path, type):
    '''
    :param net: nn.Module
    :param data_loader: torch.utils.data.utils.DataLoader
    :param data_target_tensor: tensor
    :param epoch: int
    :param _mean: (1, 1, 3, 1)
    :param _std: (1, 1, 3, 1)
    :param params_path: the path for saving the results
    :return:
    '''
    net.train(False)  # ensure dropout layers are in test mode

    with torch.no_grad():

        prediction = []

        input = []
     
        for _, batch_data in enumerate(data_loader):
            
            encoder_inputs, _ = batch_data
            input.append(encoder_inputs[:, :, 0:1].cpu().numpy())  # (batch, T', 1)
            outputs = net(encoder_inputs)
            prediction.append(outputs.detach().cpu().numpy())

        input = np.concatenate(input, 0)
        input = re_normalization(input, _mean, _std)
        # print(input)
        prediction = np.concatenate(prediction, 0)  # (batch, T', 1)
        prediction_length = prediction.shape[2]

        for i in range(prediction_length):
            print('current epoch: %s, predict %s points' % (global_step, i))
            mae = mean_absolute_error(data_target_tensor[:, :, i], prediction[:, :, i])
            rmse = mean_squared_error(data_target_tensor[:, :, i], prediction[:, :, i]) ** 0.5
            print('MAE: %.2f' % (mae))
            print('RMSE: %.2f' % (rmse))
