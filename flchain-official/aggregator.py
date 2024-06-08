import torch
from utils.process import create_process, kill_current_process
from utils.utils import upload_file, advance_stage, extract_evaluated_files, create_directory, extract_node_files
from utils.rabbitmq import setup_rabbit
from devnet_sc_proxy_trainer import mutate_upload_cluster_aggregation_file, query_get_all_file_evaluations, mutate_finalize_session
from model.server import Server
import constants

def agregate_model(cluster_id):
    searched_file_type = [constants.File_Type.CandidateModel]
    uploaded_file, current_round = extract_evaluated_files(searched_file_type)
    aggregator_path = f'{constants.AGGREGATOR_DIR}/{cluster_id}/{current_round}'
    server = Server(cluster_id, current_round)
    create_directory(aggregator_path)
    node_cluster_dict = extract_node_files(cluster_id, aggregator_path, uploaded_file, searched_file_type)
    models_file_path = []

    for node_id in node_cluster_dict:
        info = node_cluster_dict[node_id]
        for file_type in searched_file_type:
            if file_type.file_name in info:
                hash_file = info[f'{file_type.file_name}_hash']
                file_path = info[f'{file_type.file_name}']
                evaluations = query_get_all_file_evaluations(hash_file)
                length = len(evaluations)
                no_approve = sum(1 for eval in evaluations if eval['evaluation'] == constants.Verdict.POSITIVE.code)
                if no_approve > length/2:
                    models_file_path.append(file_path)

    for file_path in models_file_path:
        data = torch.load(file_path)
        if 'signature' in data:
            del data['signature']
        server.get_client_model(data)

    server.aggregate()
    server.save_model()
    file_hash = upload_file(server.save_path)
    print(f"File hash:{file_hash}")
    mutate_upload_cluster_aggregation_file(file_hash, cluster_id)
    kill_current_process()


def setup_aggregator(aggregator_id):
    print(f"Agregator {aggregator_id} ready")
    stages_dict = {
        5:agregate_model
    }
    setup_rabbit(aggregator_id, stages_dict)


if __name__ == "__main__":
    agregate_model(21)
    # create_process([21], setup_aggregator, lambda: advance_stage(5))