import requests
import os
import pandas as pd
import numpy as np
from scipy.sparse.linalg import eigs
import torch
import torch.nn as nn
from model import GCN

def write_hash(hash_codes, filename):
    with open(filename, 'w') as file:
        for code in hash_codes:
            file.write(f"{code}\n")


def check_and_create_directory(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def upload_file(filepath):
    IPFS_API_URL = 'http://localhost:5001/api/v0'
    files = {'file': open(filepath, 'rb')}
    response = requests.post(f'{IPFS_API_URL}/add', files=files)
    ipfs_hash = response.json()['Hash']
    return ipfs_hash



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
    D = np.diag(np.sum(W, axis=1))

    L = D - W

    lambda_max = eigs(L, k=1, which='LR')[0].real

    return (2 * L) / lambda_max - np.identity(W.shape[0])


def cheb_polynomial(L_tilde, K):
    N = L_tilde.shape[0]

    cheb_polynomials = [np.identity(N), L_tilde.copy()]

    for i in range(2, K):
        cheb_polynomials.append(2 * L_tilde * cheb_polynomials[i - 1] - cheb_polynomials[i - 2])

    return cheb_polynomials


def create_model(adj_matrix, cluster_index):
    L_tilde = scaled_Laplacian(adj_matrix)
    cheb = [np.expand_dims(i[:, cluster_index], axis=0) for i in cheb_polynomial(L_tilde, 3)]
    cheb_polynomial_layer1 = [torch.from_numpy(i).type(torch.FloatTensor) for i in cheb]
    cheb_polynomials = [torch.from_numpy(i).type(torch.FloatTensor) for i in cheb_polynomial(L_tilde, 3)]
    model = GCN(2, 2, 3, 64, 64, 1, cheb_polynomial_layer1, cheb_polynomials, 12, 12)

    for p in model.parameters():
        if p.dim() > 1:
            nn.init.xavier_uniform_(p)
        else:
            nn.init.uniform_(p)
    
    return model