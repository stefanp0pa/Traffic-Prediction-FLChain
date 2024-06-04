from utils.utils import extract_file
import torch
import numpy as np
import os

def extract_data_hash(hash, file_path, callback):
    if extract_file(hash, file_path) == None:
        return None
    data = callback(file_path)
    os.remove(file_path)
    return data


def create_model_from_hash(body):
    adj_matrix_hash = body['cluster_adj_matrix_addr']
    dataset_hash = body['dataset_addr']
    cluster_model_hash = body['aggr_cluser_model_addr']
    my_model_hash = body['footprind_model_addr']
    cluster_index = body['local_node_index']

    return {'cluster_index':cluster_index,
            'matrix':extract_data_hash(adj_matrix_hash, 'matrix.npz', np.load),
            'my_model': extract_data_hash(my_model_hash, 'my_model.pth', torch.load),
            'cluster_model': extract_data_hash(cluster_model_hash, 'cluster_model.pth', torch.load),
            'dataset': extract_data_hash(dataset_hash, 'data.npz', np.load)}