import sys
from utils.utils import generate_random_string
import constants
import pika
import json
import numpy as np
from utils.rabbitmq import init_rabbit
from utils.utils import extract_file, upload_file
from utils.model import create_model_from_hash
from model.client import Client
import torch
import os
from devnet_sc_proxy_trainer import query_get_all_clusters_per_node, query_get_training_data, mutate_upload_footprint_model_file, mutate_upload_candidate_model_file

torch.cuda.device_count()
torch.cuda.is_available()
os.environ["CUDA_VISIBLE_DEVICES"] = '3'
USE_CUDA = torch.cuda.is_available()
DEVICE = torch.device('cuda:0')
print("CUDA:", USE_CUDA, DEVICE)

trainer_id = int(sys.argv[1])
WORKER_NAME = generate_random_string(10)

def train_model():
    print("Incepe antrenamentul bobita")
    clusters = query_get_all_clusters_per_node(trainer_id)
    if clusters is None:
        return

    for cluster in clusters:
        response = query_get_training_data(trainer_id, cluster)
        if response is None:
            pass
    
        body = json.loads(json.dumps(response))
        unhash_data = create_model_from_hash(body)
        client = Client(trainer_id, cluster, unhash_data['cluster_index'], unhash_data['matrix']['matrix'] ,unhash_data['dataset'],DEVICE)
        del unhash_data['my_model']['node_index']
        del unhash_data['my_model']['cluster_index']
        client.load_model(unhash_data['my_model'], unhash_data['cluster_model'])
        client.train()

        model_save_path = client.get_last_model_file()
        file_hash = upload_file(model_save_path)
        print(f"Footprint file hash: {file_hash}")
        mutate_upload_footprint_model_file(file_hash, client.get_node(), client.get_cluster())

        client.save_best_model()
        model_save_path = client.get_last_model_file()
        file_hash = upload_file(model_save_path)
        print(f"Candidate file hash:{file_hash}")
        mutate_upload_candidate_model_file(file_hash, client.get_cluster())


def stage_callback(ch, method, properties, body):
    try:
        payload = json.loads(body.decode())
        payload = json.loads(payload)
        if payload['identifier'] == 'set_stage_event':
            stage = payload['stage']
            if stage not in stages_dict:
                print(f"Stage:{stage} is not available for trainer mode")
                return
            stages_dict[stage]()
    
    except Exception as e:
        print(f"Error: {e}")


def setup_queue():
    queues_name = [f"{WORKER_NAME}-set_stage_event"]
    callbacks = [stage_callback]
    init_rabbit(queues=queues_name, callbacks=callbacks)


if __name__ == "__main__":
    stages_dict = {
        3:train_model
    }
    setup_queue()