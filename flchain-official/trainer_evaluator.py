import json
from utils.rabbitmq import setup_rabbit
from utils.utils import upload_file, get_device, get_client_addr, kill_current_process, advance_stage
from utils.process import create_process
from utils.model import create_model_from_hash
from model.client import Client
from devnet_sc_proxy_trainer import query_get_all_round_files, query_get_round, query_get_file_cluster_node

def evaluate_train(cluster_id):
    node_cluster_dict = {}
    current_round = query_get_round()
    uploaded_files = query_get_all_round_files(current_round)
    uploaded_files = [file for file in uploaded_files if 'file_type' in file and file['file_type'] == 5 ]
    uploaded_files.reverse()

    for file in uploaded_files:
        hash = file['file_location']
        details = query_get_file_cluster_node(hash)
        node_index = details['global_node_index']
        cluster_index = details['cluster_index']
        file_path = ''
        if (node_index, cluster_index) in node_cluster_dict:
            continue
        # .pth

    # kill_current_process()


def setup_trainer_evaluator(trained_evaluator_id):
    print(f"Trainer Evaluator {trained_evaluator_id} ready")
    stages_dict = {
        4:evaluate_train
    }
    setup_rabbit(trained_evaluator_id, stages_dict)


if __name__ == "__main__":
    evaluate_train(20)
    # create_process([21], setup_trainer_evaluator, lambda: advance_stage(5))