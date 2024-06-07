import json
from utils.rabbitmq import setup_rabbit
from utils.utils import upload_file, get_device, get_client_addr, kill_current_process, advance_stage, create_directory, extract_file
from utils.process import create_process
from utils.model import create_model_from_hash, initiate_model_from_hash
from model.client import Client
import torch
from devnet_sc_proxy_trainer import query_get_all_round_files, query_get_round, query_get_file_cluster_node


DIR_EVALUATOR = 'node_evaluator'

def extract_node_files(cluster_id, evaluator_path, uploaded_files):
    node_cluster_dict = {}
    for file in uploaded_files:
        hash = file['file_location']
        details = query_get_file_cluster_node(hash)
        node_id = details['global_node_index']
        cluster_index = details['cluster_index']
        type = 'candidate' if file['file_type'] == 2 else 'footprint'
        file_path = f'{evaluator_path}/{type}_{node_id}.pth'

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

    return node_cluster_dict 


def evaluate_train(cluster_id):
    DEVICE = get_device()
    current_round = query_get_round()
    uploaded_files = query_get_all_round_files(current_round)
    uploaded_files = [file for file in uploaded_files if 'file_type' in file and (file['file_type'] == 5 or file['file_type'] == 2) ]
    uploaded_files.reverse()
    evaluator_path = f'{DIR_EVALUATOR}/{cluster_id}/{current_round}'
    create_directory(evaluator_path)
    node_cluster_dict = extract_node_files(cluster_id, evaluator_path, uploaded_files)

    for node_id in node_cluster_dict:
        node_files = node_cluster_dict[node_id]
    
        if 'candidate' not in node_files:
            print(f"Error: Node {node_id} doesn't have candidate file")
            continue

        if 'footprint' not in node_files:
            print(f"Error: Node {node_id} doesn't have footprint file")
            continue    
        
        client = initiate_model_from_hash(node_id, cluster_id, DEVICE)
        footprint_model = torch.load(f'{evaluator_path}/footprint_{node_id}.pth')
        candidate_model = torch.load(f'{evaluator_path}/candidate_{node_id}.pth')
        client.load_model(footprint_model, candidate_model)
        client.evaluate()
        return

    # kill_current_process()


def setup_trainer_evaluator(trained_evaluator_id):
    print(f"Trainer Evaluator {trained_evaluator_id} ready")
    stages_dict = {
        4:evaluate_train
    }
    setup_rabbit(trained_evaluator_id, stages_dict)


if __name__ == "__main__":
    evaluate_train(21)
    # create_process([21], setup_trainer_evaluator, lambda: advance_stage(5))