import torch
import sys
from utils.utils import extract_file, upload_file
from utils.rabbitmq import setup_rabbit
from devnet_sc_proxy_trainer import query_get_candidate_models_for_aggregation, query_get_round, mutate_upload_cluster_aggregation_file
from model.server import Server

cluster_id = int(sys.argv[1])

def agregate_model():
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
    print(f"File hash:{file_hash}")
    mutate_upload_cluster_aggregation_file(file_hash, cluster_id)


if __name__ == "__main__":
    stages_dict = {
        4:agregate_model
    }
    setup_rabbit(stages_dict)