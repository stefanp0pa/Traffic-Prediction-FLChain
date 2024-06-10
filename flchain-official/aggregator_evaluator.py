from utils.rabbitmq import setup_rabbit
from utils.utils import get_device, create_directory, extract_node_files, extract_evaluated_files, get_wallet_and_client_addr
from utils.process import create_process, kill_current_process
from utils.model import initiate_model_from_hash, get_cluster_data
import torch
import constants
import time
from devnet_sc_proxy_trainer import mutate_evaluate_file, query_get_all_nodes_per_cluster, mutate_next_round, mutate_next_stage

DIR_EVALUATOR = constants.DIR_AGGREGATOR_EVALUATOR
ERROR_THRESHOLD = constants.ERROR_THRESHOLD

def evaluate_aggregation(cluster_id):
    wallet_path, caller_user_addr = get_wallet_and_client_addr(constants.WALLETS_DIR_EVALUATORS, cluster_id)
    print(wallet_path)
    DEVICE = get_device()
    training_data, test_data = get_cluster_data(cluster_id, DEVICE)
    cluster_nodes = query_get_all_nodes_per_cluster(cluster_id)
    searched_file_type = [constants.File_Type.ClusterAggregationModel]
    uploaded_files, current_round = extract_evaluated_files(searched_file_type)
    evaluator_path = f'{DIR_EVALUATOR}/{cluster_id}/{current_round}'
    create_directory(evaluator_path)
    node_cluster_dict = extract_node_files(cluster_id, evaluator_path, uploaded_files, searched_file_type)

    for key in node_cluster_dict:
        data = node_cluster_dict[key]

        client = initiate_model_from_hash(cluster_nodes[0]['global_node_index'], cluster_id, DEVICE, True)
        candidate_model = torch.load(f'{evaluator_path}/{constants.File_Type.ClusterAggregationModel.file_name}_{key}.pth')
        client.load_model(candidate_model, candidate_model)
        error = client.evaluate(test_data)
        status = constants.Verdict.POSITIVE
        print(f"Cluster: {cluster_id} has error: {error}")
        print(f"Cluster: {cluster_id} has a {'Positive' if status == constants.Verdict.POSITIVE else 'Negative'} status")
        mutate_evaluate_file(data[f'{constants.File_Type.ClusterAggregationModel.file_name}_hash'], status.code, wallet_path, caller_user_addr)

    kill_current_process()


def setup_aggregator_evaluator(aggregator_evaluator_id):
    print(f"Evaluator Agregator {aggregator_evaluator_id} ready")
    stages_dict = {
        6:evaluate_aggregation
    }
    setup_rabbit(aggregator_evaluator_id, stages_dict)


def next_round():
    time.sleep(30)
    mutate_next_round()


if __name__ == "__main__":
    # evaluate_aggregation(21)
    create_process([21], setup_aggregator_evaluator, lambda: next_round())