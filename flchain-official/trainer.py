from utils.rabbitmq import setup_rabbit
from utils.utils import upload_file, get_device, advance_stage, get_wallet_and_client_addr
from utils.process import create_process, kill_current_process
from utils.model import initiate_model_from_hash
from devnet_sc_proxy_trainer import query_get_all_clusters_per_node, mutate_upload_footprint_model_file, mutate_upload_candidate_model_file
import constants

def upload_client_file(client, callback):
    model_save_path = client.get_last_model_file()
    file_hash = upload_file(model_save_path)
    # print(f"File hash:{file_hash}")
    callback(file_hash)


def train_model(node_id):
    DEVICE = get_device()
    wallet_path, caller_user_addr = get_wallet_and_client_addr(constants.WALLETS_DIR_TRAINERS, node_id)
    if wallet_path is None:
        return

    clusters = query_get_all_clusters_per_node(node_id, caller_user_addr)
    if clusters is None:
        return

    for cluster in clusters:
        client = initiate_model_from_hash(node_id, cluster, DEVICE)
        if client is None:
            continue
        print("Antreneaza BOBITA")
        client.train()

        upload_client_file(client, lambda file_hash: mutate_upload_footprint_model_file(file_hash, client.get_node(), client.get_cluster(), wallet_path, caller_user_addr))
        client.save_best_model('candidate')
        upload_client_file(client, lambda file_hash: mutate_upload_candidate_model_file(file_hash, client.get_node(), client.get_cluster(), wallet_path, caller_user_addr))

    kill_current_process()


def setup_trainer(trained_id):
    print(f"Trainer {trained_id} ready")
    stages_dict = {
        3:train_model
    }
    setup_rabbit(trained_id, stages_dict)


if __name__ == "__main__":
    create_process([121, 123, 140], setup_trainer, lambda: advance_stage())
