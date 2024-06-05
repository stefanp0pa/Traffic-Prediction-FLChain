import torch
import os
import json
import sys
from utils.utils import generate_random_string, extract_file, upload_file
from utils.rabbitmq import init_rabbit
from devnet_sc_proxy_trainer import query_get_candidate_models_for_aggregation, query_get_round, mutate_upload_cluster_aggregation_file
from model.server import Server

torch.cuda.device_count()
torch.cuda.is_available()
os.environ["CUDA_VISIBLE_DEVICES"] = '3'
USE_CUDA = torch.cuda.is_available()
DEVICE = torch.device('cuda:0')
print("CUDA:", USE_CUDA, DEVICE)

cluster_id = int(sys.argv[1])
WORKER_NAME = generate_random_string(10)


def agregate_model():

    print("Start agregate models bitch")
    current_round = query_get_round()
    models_hash = query_get_candidate_models_for_aggregation(cluster_id)
    cluster_aggregator_file = f"{cluster_id}_{current_round}.pth"
    server = Server(cluster_id, current_round)

    for hash in models_hash:
        file_path = extract_file(hash, cluster_aggregator_file)
        if file_path is None:
            pass
    
        data = torch.load(file_path)
        del data['signature']
        server.get_client_model(data)

    server.aggregate()
    server.save_model()
    file_hash = upload_file(server.save_path)
    print(f"Candidate file hash:{file_hash}")
    mutate_upload_cluster_aggregation_file(file_hash, cluster_id)


def stage_callback(ch, method, properties, body):
    try:
        payload = json.loads(body.decode())
        payload = json.loads(payload)
        print(payload)
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
        4:agregate_model
    }
    setup_queue()