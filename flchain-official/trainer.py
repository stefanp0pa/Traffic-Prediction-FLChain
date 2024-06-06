import sys
import json
from utils.rabbitmq import setup_rabbit
from utils.utils import upload_file, get_device
from utils.model import create_model_from_hash
from model.client import Client
from devnet_sc_proxy_trainer import query_get_all_clusters_per_node, query_get_training_data, mutate_upload_footprint_model_file, mutate_upload_candidate_model_file

DEVICE = get_device()
trainer_id = int(sys.argv[1])

def upload_client_file(client, callback):
    model_save_path = client.get_last_model_file()
    file_hash = upload_file(model_save_path)
    print(f"File hash:{file_hash}")
    callback(file_hash)


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
        if 'node_index' in unhash_data['my_model']:
            del unhash_data['my_model']['node_index']
            del unhash_data['my_model']['cluster_index']

        client.load_model(unhash_data['my_model'], unhash_data['cluster_model'])
        client.train()
       
        upload_client_file(client, lambda file_hash: mutate_upload_footprint_model_file(file_hash, client.get_node(), client.get_cluster()) )
        client.save_best_model()
        upload_client_file(client, lambda file_hash: mutate_upload_candidate_model_file(file_hash, client.get_cluster()) )
       

if __name__ == "__main__":
    stages_dict = {
        3:train_model
    }
    setup_rabbit(stages_dict)