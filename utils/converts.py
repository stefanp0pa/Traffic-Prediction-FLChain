from bech32 import bech32_encode, convertbits
import base64
import json

def hex_string_to_bech32_address(hex_str, hrp = 'erd'):
    hex_bytes = bytes.fromhex(hex_str.rstrip('\x00'))
    data = convertbits(hex_bytes, 8, 5)
    bech32_str = bech32_encode(hrp, data)
    return bech32_str
    
def base64_string_to_string(encoded_string):
    if not encoded_string:
        return 0
    decoded_bytes = base64.b64decode(encoded_string.rstrip('\x00'))
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string

def base64_string_to_bytes(encoded_string):
    if not encoded_string:
        return 0
    decoded_bytes = base64.b64decode(encoded_string.rstrip('\x00'))
    return decoded_bytes

def hex_string_to_numeric(hex_string):
    if not hex_string:
        return 0
    numeric_value = int(hex_string.rstrip('\x00'), 16)
    return numeric_value

def hex_string_to_string(hex_string):
    if not hex_string:
        return 0
    decoded_bytes = bytes.fromhex(hex_string.rstrip('\x00'))
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string

def base64_string_to_hex_string(encoded_string):
    if not encoded_string:
        return 0
    decoded_bytes = base64.b64decode(encoded_string.rstrip('\x00'))
    hex_encoded = decoded_bytes.hex()
    return hex_encoded

def base64_string_to_numeric(encoded_string):
    if not encoded_string:
        return 0
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    numeric_value = hex_string_to_numeric(decoded_bytes)
    return numeric_value

def base64_string_to_bech32_address(encoded_string):
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    bech32_address = hex_string_to_bech32_address(decoded_bytes)
    return bech32_address

def base64_string_to_array_of_bech32_addresses(encoded_string):
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    bech32_addresses = []
    for i in range(0, len(decoded_bytes), 64):
        bech32_addresses.append(hex_string_to_bech32_address(decoded_bytes[i:i + 64]))
    return bech32_addresses

def base64_string_to_graphTopology(encoded_string):
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    vertices_count = decoded_bytes[:16] # 8 bytes x 2 = 16 chars for vertices count
    edges_count = decoded_bytes[16:32] # 8 bytes x 2 = 16 chars for edges count
    owner = decoded_bytes[32:96] # 32 bytes x 2 = 64 chars for owner address
    storage_addr = decoded_bytes[96:188] # 46 bytes x 2 = 92 chars for storage address
    timestamp = decoded_bytes[188:204] # 8 bytes x 2 = 16 chars for timestamp
    hash = decoded_bytes[204:] # 32 bytes x 2 = 64 chars for hash
    decoded_response = {
        'vertices_count': hex_string_to_numeric(vertices_count),
        'edges_count': hex_string_to_numeric(edges_count),
        'owner': hex_string_to_bech32_address(owner),
        'storage_addr': hex_string_to_string(storage_addr),
        'timestamp': hex_string_to_numeric(timestamp),
        'hash': hex_string_to_string(hash)
    }
    print(decoded_response)
    return decoded_response

def hex_string_to_file(hex_string):
    if not hex_string:
        return 0
    file_location = hex_string[:92] # 46 bytes x 2 = 92 chars for file location
    file_type = hex_string[92:94] # 2 bytes x 1 = 2 chars for file type
    round = hex_string[94:102] # 2 bytes x 4 = 8 chars for round
    decoded_response = {
        'file_location': hex_string_to_string(file_location),
        'file_type': hex_string_to_numeric(file_type),
        'round': hex_string_to_numeric(round)
    }
    return decoded_response

def base64_string_to_file_array(encoded_string):
    if not encoded_string:
        return []

    decoded_bytes = base64_string_to_hex_string(encoded_string)
    file_struct_size = 102
    segments = []
    for i in range(0, len(decoded_bytes), file_struct_size):
        segments.append(decoded_bytes[i:i + file_struct_size])
    
    decoded_response = []
    for i in range(0, len(segments)):
        segment = segments[i]    
        decoded_response.append(hex_string_to_file(segment))
        
    print(decoded_response)
    return decoded_response

def base64_string_to_file(encoded_string):
    if not encoded_string:
        return 0
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    decoded_response = hex_string_to_file(decoded_bytes)
    return decoded_response

def base64_string_to_ipfs_addresses(encoded_string):
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    ipfs_addresses = []
    ipfs_cdv1_addr_size = 46 * 2
    for i in range(0, len(decoded_bytes), ipfs_cdv1_addr_size):
        ipfs_addresses.append(hex_string_to_string(decoded_bytes[i:i + ipfs_cdv1_addr_size]))
    return ipfs_addresses