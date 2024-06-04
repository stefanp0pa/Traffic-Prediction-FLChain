import sys
from utils.utils import generate_random_string
import constants
import pika
import json
import numpy as np
from utils.rabbitmq import init_rabbit
from utils.utils import extract_file
from devnet_sc_proxy_trainer import query_get_all_clusters_per_node, query_get_cluster_adjacency_matrix

trainer_id = int(sys.argv[1])
WORKER_NAME = generate_random_string(10)

# query_get_all_clusters_per_node(112)
# query_get_cluster_adjacency_matrix(8)
# query_get_cluster_aggregation(1, 0)
# query_get_training_data(112, 1)
def train_model():
    print("Incepe antrenamentul bobita")
    clusters = query_get_all_clusters_per_node(trainer_id)
    for cluster in clusters:
        print(cluster)
        adj_matrix_hash = query_get_cluster_adjacency_matrix(cluster)
        check, matrix_path = extract_file(adj_matrix_hash)
        data = np.load(matrix_path)
        matrix = data['matrix']


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