import random
import string
import requests
import numpy as np
import os
import torch
from scipy.sparse.linalg import eigs
import os
import time
from devnet_sc_proxy_trainer import mutate_set_stage, query_get_round, query_get_all_round_files, query_get_file_cluster_node


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def upload_file(filepath):
    IPFS_API_URL = 'http://localhost:5001/api/v0'
    files = {'file': open(filepath, 'rb')}
    response = requests.post(f'{IPFS_API_URL}/add', files=files)
    ipfs_hash = response.json()['Hash']
    return ipfs_hash


def extract_file(ipfs_hash, file_path):
    IPFS_API_URL = 'http://localhost:8080/ipfs/'
    response = requests.get(f'{IPFS_API_URL}/{ipfs_hash}')
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
        return file_path
    else:
        print('Failed to download the file')
        return None


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


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


def get_device():
    torch.cuda.device_count()
    torch.cuda.is_available()
    os.environ["CUDA_VISIBLE_DEVICES"] = '3'
    USE_CUDA = torch.cuda.is_available()
    DEVICE = torch.device('cuda:0')
    print("CUDA:", USE_CUDA, DEVICE)
    return DEVICE


def get_client_addr(client_index, file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if 0 < client_index <= len(lines):
            line = lines[client_index - 1]
            return line.rstrip('\n')
        return None


def advance_stage(next_stage):
    time.sleep(30)
    mutate_set_stage(next_stage)


def find_file_name_by_code(code, file_types):
    for file_type in file_types:
        if file_type.code == code:
            return file_type.file_name
    return None


def extract_evaluated_files(file_type):
    current_round = query_get_round()
    uploaded_files = query_get_all_round_files(current_round)
    uploaded_files = [file for file in uploaded_files if 'file_type' in file and find_file_name_by_code(file['file_type'], file_type) is not None]
    uploaded_files.reverse()
    return uploaded_files, current_round


def extract_node_files(cluster_id, dir_path, uploaded_files, searched_type_files):
    node_cluster_dict = {}
    for file in uploaded_files:
        hash = file['file_location']
        details = query_get_file_cluster_node(hash)
        node_id = details['global_node_index']
        print(node_id)
        cluster_index = details['cluster_index']
        type = find_file_name_by_code(file['file_type'], searched_type_files)
        file_path = f'{dir_path}/{type}_{node_id}.pth'

        if type is None:
            continue

        if cluster_id != cluster_index:
            continue
        
        if node_id not in node_cluster_dict:
            node_cluster_dict[node_id] = {}

        if type in node_cluster_dict[node_id]:
            continue

        succes = extract_file(hash, file_path)
        if succes is None:
            print(f'Error: File with hash: {hash} for node: {node_id} is not available')
            continue
        
        node_cluster_dict[node_id][type] = file_path
        node_cluster_dict[node_id][f"{type}_hash"] = hash

    return node_cluster_dict
