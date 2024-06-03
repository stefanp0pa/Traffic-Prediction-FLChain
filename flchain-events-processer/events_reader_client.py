# CODE AUTOMATICALLY GENERATED BY events-reader-generator.py

from bech32 import bech32_encode, convertbits
from datetime import datetime, timezone
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

def hex_string_to_training_data(hex_string):
    if not hex_string:
        return 0
    cluster_adj_matrix_addr = hex_string[:92] # 46 bytes x 2 = 92 chars for cluster adjacency matrix address
    dataset_addr = hex_string[92:184] # 46 bytes x 2 = 92 chars for dataset address
    aggr_cluser_model_addr = hex_string[184:276] # 46 bytes x 2 = 92 chars for aggregated cluster model address
    local_node_index = hex_string[276:280] # 2 bytes x 2 = 4 chars for local node index
    decoded_response = {
        'cluster_adj_matrix_addr': hex_string_to_string(cluster_adj_matrix_addr),
        'dataset_addr': hex_string_to_string(dataset_addr),
        'aggr_cluser_model_addr': hex_string_to_string(aggr_cluser_model_addr),
        'local_node_index': hex_string_to_numeric(local_node_index)
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
        
    return decoded_response

def base64_string_to_file(encoded_string):
    if not encoded_string:
        return 0
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    decoded_response = hex_string_to_file(decoded_bytes)
    return decoded_response

def base64_string_to_ipfs_addresses(encoded_string):
    if not encoded_string:
        return []
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    ipfs_addresses = []
    ipfs_cdv1_addr_size = 46 * 2
    for i in range(0, len(decoded_bytes), ipfs_cdv1_addr_size):
        ipfs_addresses.append(hex_string_to_string(decoded_bytes[i:i + ipfs_cdv1_addr_size]))
    return ipfs_addresses

def base64_string_to_ipfs_address(encoded_string):
    if not encoded_string:
        return 0
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    decoded_response = hex_string_to_string(decoded_bytes)
    return decoded_response

def base64_string_to_training_data(encoded_string):
    if not encoded_string:
        return 0
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    decoded_response = hex_string_to_training_data(decoded_bytes)
    return decoded_response

def base64_string_to_list_u16(encoded_string):
    if not encoded_string:
        return []
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    u16_numbers = []
    u16_part_size = 4
    for i in range(0, len(decoded_bytes), u16_part_size):
        decoded_response = hex_string_to_numeric(decoded_bytes[i:i + u16_part_size])    
        u16_numbers.append(decoded_response)
    return u16_numbers

def base64_string_to_list_cluster_node(encoded_string):
    if not encoded_string:
        return []
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    cluster_node_size = 8 # 4 bytes + 4 bytes
    cluster_nodes = []
    for i in range(0, len(decoded_bytes), cluster_node_size):
        cluster_nodes.append({
            'global_node_index': hex_string_to_numeric(decoded_bytes[i:i + 4]),
            'local_node_index': hex_string_to_numeric(decoded_bytes[i + 4:i + 8])
        })
    return cluster_nodes

def read_signup_user_event(payload):
	event_name = base64_string_to_string(payload[0])
	user_addr = base64_string_to_bech32_address(payload[1])
	stake = base64_string_to_numeric(payload[2])
	role = base64_string_to_numeric(payload[3])
	return json.dumps({'user_addr': user_addr, 'stake': stake, 'role': role, 'identifier': event_name})


def read_user_cleared_event(payload):
	event_name = base64_string_to_string(payload[0])
	user_addr = base64_string_to_bech32_address(payload[1])
	return json.dumps({'user_addr': user_addr, 'identifier': event_name})


def read_set_round_event(payload):
	event_name = base64_string_to_string(payload[0])
	round = base64_string_to_numeric(payload[1])
	return json.dumps({'round': round, 'identifier': event_name})


def read_set_stage_event(payload):
	event_name = base64_string_to_string(payload[0])
	stage = base64_string_to_numeric(payload[1])
	return json.dumps({'stage': stage, 'identifier': event_name})


def read_upload_file_event(payload):
	event_name = base64_string_to_string(payload[0])
	file_location = base64_string_to_ipfs_address(payload[1])
	file_type = base64_string_to_numeric(payload[2])
	round = base64_string_to_numeric(payload[3])
	author_addr = base64_string_to_bech32_address(payload[4])
	return json.dumps({'file_location': file_location, 'file_type': file_type, 'round': round, 'author_addr': author_addr, 'identifier': event_name})


def read_clear_file_event(payload):
	event_name = base64_string_to_string(payload[0])
	file_location = base64_string_to_ipfs_address(payload[1])
	file_type = base64_string_to_numeric(payload[2])
	round = base64_string_to_numeric(payload[3])
	author_addr = base64_string_to_bech32_address(payload[4])
	return json.dumps({'file_location': file_location, 'file_type': file_type, 'round': round, 'author_addr': author_addr, 'identifier': event_name})


def read_evaluate_file_event(payload):
	event_name = base64_string_to_string(payload[0])
	file_location = base64_string_to_ipfs_address(payload[1])
	status = base64_string_to_numeric(payload[2])
	evaluator = base64_string_to_bech32_address(payload[3])
	return json.dumps({'file_location': file_location, 'status': status, 'evaluator': evaluator, 'identifier': event_name})


def read_reputation_updated_event(payload):
	event_name = base64_string_to_string(payload[0])
	user_addr = base64_string_to_bech32_address(payload[1])
	new_reputation = base64_string_to_numeric(payload[2])
	return json.dumps({'user_addr': user_addr, 'new_reputation': new_reputation, 'identifier': event_name})


def read_transferValueOnly(payload):
	event_name = base64_string_to_string(payload[0])
	value = base64_string_to_numeric(payload[1])
	dest = base64_string_to_bech32_address(payload[2])
	return json.dumps({'value': value, 'dest': dest, 'identifier': event_name})


event_names = ['signup_user_event',
'user_cleared_event',
'set_round_event',
'set_stage_event',
'upload_file_event',
'clear_file_event',
'evaluate_file_event',
'reputation_updated_event',
'transferValueOnly']

ignore_events = ['SCUpgrade', 'writeLog', 'completedTxEvent', 'signalError', 'internalVMErrors']

def show_all_event_types():
	return event_names

def show_all_ignore_events():
	return ignore_events

def use_read_method(event_name):
	event_read_methods = {
		'signup_user_event': read_signup_user_event,
		'user_cleared_event': read_user_cleared_event,
		'set_round_event': read_set_round_event,
		'set_stage_event': read_set_stage_event,
		'upload_file_event': read_upload_file_event,
		'clear_file_event': read_clear_file_event,
		'evaluate_file_event': read_evaluate_file_event,
		'reputation_updated_event': read_reputation_updated_event,
		'transferValueOnly': read_transferValueOnly,
	}

	if event_name in event_read_methods:
		return event_read_methods[event_name]
	else:
		print(f"Event {event_name} not found in available events.")
		return None

def read_event_payload(event_name, payload):
	read_method = use_read_method(event_name)
	return read_method(payload)
