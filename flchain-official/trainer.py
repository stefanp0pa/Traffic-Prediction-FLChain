import json
from utils.rabbitmq import setup_rabbit
from utils.utils import upload_file, get_device, get_client_addr, kill_current_process, advance_stage
from utils.process import create_process
from utils.model import create_model_from_hash, initiate_model_from_hash
from model.client import Client
from devnet_sc_proxy_trainer import query_get_all_clusters_per_node, query_get_training_data, mutate_upload_footprint_model_file, mutate_upload_candidate_model_file, mutate_set_stage

WALLET_DIR="wallets"
WALLET_DIR_ADDRESS_FILE="wallets_addr"
WALLETS_DIR_TRAINERS="trainers"
WORK_DIR="/home/robert/Desktop/Facultate/Licenta/Traffic-Prediction-FLChain/flchain-official"


def upload_client_file(client, callback):
    model_save_path = client.get_last_model_file()
    file_hash = upload_file(model_save_path)
    print(f"File hash:{file_hash}")
    callback(file_hash)


def train_model(node_id):
    DEVICE = get_device()
    wallet_path = f"{WORK_DIR}/{WALLET_DIR}/{WALLETS_DIR_TRAINERS}/{node_id}.pem"
    wallet_addres = f"{WORK_DIR}/{WALLET_DIR}/{WALLET_DIR_ADDRESS_FILE}/{WALLETS_DIR_TRAINERS}"
    
    caller_user_addr = get_client_addr(node_id, wallet_addres)
    if caller_user_addr is None:
        return

    clusters = query_get_all_clusters_per_node(node_id, caller_user_addr)
    if clusters is None:
        return

    for cluster in clusters:
        client = initiate_model_from_hash(node_id, cluster, DEVICE)
        client.train()

        upload_client_file(client, lambda file_hash: mutate_upload_footprint_model_file(file_hash, client.get_node(), client.get_cluster(), wallet_path, caller_user_addr))
        client.save_best_model()
        upload_client_file(client, lambda file_hash: mutate_upload_candidate_model_file(file_hash, client.get_node(), client.get_cluster(), wallet_path, caller_user_addr))

    kill_current_process()


def setup_trainer(trained_id):
    print(f"Trainer {trained_id} ready")
    stages_dict = {
        3:train_model
    }
    setup_rabbit(trained_id, stages_dict)


if __name__ == "__main__":
    create_process([121, 123, 140], setup_trainer, lambda: advance_stage(4))