from utils.rabbitmq import setup_rabbit
from utils.utils import get_device, create_directory, extract_node_files, extract_evaluated_files, advance_stage, get_wallet_and_client_addr
from utils.process import create_process, kill_current_process
from utils.model import initiate_model_from_hash
import torch
import constants
from devnet_sc_proxy_trainer import mutate_evaluate_file

DIR_EVALUATOR = constants.DIR_TRAINER_EVALUATOR
ERROR_THRESHOLD = constants.ERROR_THRESHOLD

def evaluate_train(cluster_id):
    DEVICE = get_device()
    searched_file_type = [constants.File_Type.CandidateModel, constants.File_Type.FootprintModel]
    uploaded_files, current_round = extract_evaluated_files(searched_file_type)
    evaluator_path = f'{DIR_EVALUATOR}/{cluster_id}/{current_round}'
    create_directory(evaluator_path)
    node_cluster_dict = extract_node_files(cluster_id, evaluator_path, uploaded_files, searched_file_type)
    file_result = []
    for node_id in node_cluster_dict:
        node_files = node_cluster_dict[node_id]
        valid = True

        for file_type in searched_file_type:
            if file_type.file_name not in node_files:
                print(f"Error: Node {node_id} doesn't have {file_type.file_name} file")
                valid = False

        if valid is not True:
            continue
        
        wallet_path, caller_user_addr = get_wallet_and_client_addr(constants.WALLETS_DIR_TRAINERS, node_id)
        if wallet_path is None:
            return

        client = initiate_model_from_hash(node_id, cluster_id, DEVICE)
        footprint_model = torch.load(f'{evaluator_path}/{constants.File_Type.FootprintModel.file_name}_{node_id}.pth')
        candidate_model = torch.load(f'{evaluator_path}/{constants.File_Type.CandidateModel.file_name}_{node_id}.pth')
        client.load_model(footprint_model, candidate_model)
        error = client.evaluate()
        file_result.append({'error': error, 'file_hash':node_files[f'{constants.File_Type.CandidateModel.file_name}_hash'], 'node_id':node_id, 'wallet_path': wallet_path, 'caller_user_addr': caller_user_addr})
        
    file_result = sorted(file_result, key=lambda x: x['error'])
    lowest_error = file_result[0]['error']
    for result in file_result:
        node_id = result['node_id']
        error = result['error']
        wallet_path = result['wallet_path']
        caller_user_addr = result['caller_user_addr']
        hash = result['file_hash']
        status = constants.Verdict.NEGATIVE
        if error - lowest_error <= 0.01:
            status = constants.Verdict.POSITIVE
        
        with open(f'trainer_evaluator/{node_id}', 'a') as file:
            file.write(f"Round: {current_round} Node: {node_id} Cluster: {cluster_id} has error: {error}\n") 
        print(f"Round: {current_round} Node: {node_id} Cluster: {cluster_id} has error: {error}")
        print(f"Node: {node_id} has candidate file with a {'Positive' if status == constants.Verdict.POSITIVE else 'Negative'} status")
        mutate_evaluate_file(hash, status.code, wallet_path, caller_user_addr)
        # mutate_evaluate_file(node_files[f'{constants.File_Type.FootprintModel.file_name}_hash'], status.code, wallet_path, caller_user_addr)

    kill_current_process()


def setup_trainer_evaluator(trained_evaluator_id):
    print(f"Trainer Evaluator {trained_evaluator_id} ready")
    stages_dict = {
        4:evaluate_train
    }
    setup_rabbit(trained_evaluator_id, stages_dict)


if __name__ == "__main__":
    # evaluate_train(21)
    create_directory('trainer_evaluator')
    create_process([9], setup_trainer_evaluator, lambda: advance_stage())