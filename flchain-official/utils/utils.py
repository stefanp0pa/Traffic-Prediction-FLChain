import random
import string
import requests
import numpy as np
from scipy.sparse.linalg import eigs

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

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