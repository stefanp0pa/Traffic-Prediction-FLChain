import random
import string
import requests
import numpy as np
import os
import torch
from scipy.sparse.linalg import eigs
import os
import signal
import time
from devnet_sc_proxy_trainer import mutate_set_stage 

def kill_current_process():
    os.kill(os.getpid(), signal.SIGTERM)


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