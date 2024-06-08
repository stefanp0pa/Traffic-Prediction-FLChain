from utils.utils import extract_file, generate_random_string
from devnet_sc_proxy_trainer import query_get_training_data, query_get_all_nodes_per_cluster
from model.client import Client, create_dataloaders
import torch
import numpy as np
import os
import json
import model.constants as constants 


def extract_data_hash(hash, file_path, callback):
    if extract_file(hash, file_path) == None:
        return None
    data = callback(file_path)
    os.remove(file_path)
    return data


def create_model_from_hash(body):
    file_length = 10
    adj_matrix_hash = body['cluster_adj_matrix_addr']
    dataset_hash = body['dataset_addr']
    cluster_model_hash = body['aggr_cluser_model_addr']
    my_model_hash = body['footprind_model_addr']
    cluster_index = body['local_node_index']

    return {'cluster_index':cluster_index,
            'matrix':extract_data_hash(adj_matrix_hash, f'{generate_random_string(file_length)}.npz', np.load),
            'my_model': extract_data_hash(my_model_hash, f'{generate_random_string(file_length)}.pth', torch.load),
            'cluster_model': extract_data_hash(cluster_model_hash, f'{generate_random_string(file_length)}.pth', torch.load),
            'dataset': extract_data_hash(dataset_hash, f'{generate_random_string(file_length)}.npz', np.load)}


def load_data_per_node(node_id, cluster_id):
    response = query_get_training_data(node_id, cluster_id)
    if response is None:
        return None
     
    body = json.loads(json.dumps(response))
    unhash_data = create_model_from_hash(body)
    return unhash_data


def get_cluster_data(cluster_id, DEVICE):
    nodes = query_get_all_nodes_per_cluster(cluster_id)
    nodes = [node['global_node_index'] for node in nodes]
    new_data = {'train_x' : [], 'train_target': [], 'test_x': [], 'test_target' : {}}

    for node_id in nodes:
        data = load_data_per_node(node_id, cluster_id)
        new_data['train_x'].append(data['dataset']['train_x'][:, np.newaxis, :, :])
        new_data['train_target'] = data['dataset']['train_target']
        new_data['test_x'].append(data['dataset']['test_x'][:, np.newaxis, :, :])
        new_data['test_target'] = data['dataset']['test_target']

    new_data['train_x'] = np.concatenate(new_data['train_x'], axis=1)
    new_data['test_x'] = np.concatenate(new_data['test_x'], axis=1)
    training_data, _ = create_dataloaders('train_x', 'train_target', new_data, DEVICE)
    test_data, _ = create_dataloaders('test_x', 'test_target', new_data, DEVICE)

    return training_data, test_data


def initiate_model_from_hash(node_id, cluster, DEVICE, is_global = False):
    unhash_data = load_data_per_node(node_id, cluster)
    if unhash_data is None:
        return None
     
    cluster_index = unhash_data['cluster_index']
    if is_global == True:
        cluster_index = 0
    client = Client(node_id, cluster, cluster_index, unhash_data['matrix']['matrix'] ,unhash_data['dataset'],DEVICE)
    if 'node_index' in unhash_data['my_model']:
        del unhash_data['my_model']['node_index']
        del unhash_data['my_model']['cluster_index']
    
    client.load_model(unhash_data['my_model'], unhash_data['cluster_model'])
    return client