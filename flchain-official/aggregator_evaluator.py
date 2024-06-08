from utils.rabbitmq import setup_rabbit
from utils.utils import get_device, create_directory, extract_node_files, extract_evaluated_files
from utils.process import create_process, kill_current_process
from utils.model import initiate_model_from_hash
import torch
import constants
from devnet_sc_proxy_trainer import mutate_evaluate_file, query_get_all_nodes_per_cluster

DIR_EVALUATOR = 'cluster_evaluator'
ERROR_THRESHOLD = 0.03

def evaluate_aggregation(cluster_id):
    DEVICE = get_device()
    cluster_nodes = query_get_all_nodes_per_cluster(cluster_id)
    searched_file_type = [constants.File_Type.ClusterAggregationModel]
    uploaded_files, current_round = extract_evaluated_files(searched_file_type)
    evaluator_path = f'{DIR_EVALUATOR}/{cluster_id}/{current_round}'
    create_directory(evaluator_path)
    node_cluster_dict = extract_node_files(cluster_id, evaluator_path, uploaded_files, searched_file_type)
    print(cluster_nodes)
    for key in node_cluster_dict:
        data = node_cluster_dict[key]

        client = initiate_model_from_hash(cluster_nodes[0]['global_node_index'], cluster_id, DEVICE)
        candidate_model = torch.load(f'{evaluator_path}/{constants.File_Type.ClusterAggregationModel.file_name}_{key}.pth')
        client.load_model(candidate_model, candidate_model)
        error = client.evaluate()
        print(error)


def setup_aggregator_evaluator(aggregator_evaluator_id):
    print(f"Evaluator Agregator {aggregator_evaluator_id} ready")
    stages_dict = {
        6:evaluate_aggregation
    }
    setup_rabbit(aggregator_evaluator_id, stages_dict)


if __name__ == "__main__":
    evaluate_aggregation(21)
    # create_process([21], setup_aggregator_evaluator, lambda: advance_stage(5))