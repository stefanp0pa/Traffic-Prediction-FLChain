from utils.utils import extract_file, generate_random_string
from devnet_sc_proxy_trainer import query_get_training_data
from model.client import Client
import torch
import numpy as np
import os
import json

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


def initiate_model_from_hash(node_id, cluster, DEVICE):
    response = query_get_training_data(node_id, cluster)
    if response is None:
        pass
    
    body = json.loads(json.dumps(response))
    unhash_data = create_model_from_hash(body)
    client = Client(node_id, cluster, unhash_data['cluster_index'], unhash_data['matrix']['matrix'] ,unhash_data['dataset'],DEVICE)
    if 'node_index' in unhash_data['my_model']:
        del unhash_data['my_model']['node_index']
        del unhash_data['my_model']['cluster_index']
    
    client.load_model(unhash_data['my_model'], unhash_data['cluster_model'])
    return client