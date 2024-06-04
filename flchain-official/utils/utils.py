import random
import string
import requests

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def extract_file(ipfs_hash):
    IPFS_API_URL = 'http://localhost:8080/ipfs/'
    file_name = 'matrix.npz'
    response = requests.get(f'{IPFS_API_URL}/{ipfs_hash}')
    if response.status_code == 200:
        with open('matrix.npz', "wb") as file:
            file.write(response.content)
        return (True, file_name)
    else:
        print('Failed to download the file')
        return (False, None)