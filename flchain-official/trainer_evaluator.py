from utils.rabbitmq import setup_rabbit
from utils.utils import get_device, create_directory, extract_node_files, extract_evaluated_files
from utils.process import create_process, kill_current_process
from utils.model import initiate_model_from_hash
import torch
import constants
from devnet_sc_proxy_trainer import mutate_evaluate_file

DIR_EVALUATOR = 'node_evaluator'
ERROR_THRESHOLD = 0.03

def evaluate_train(cluster_id):
    DEVICE = get_device()
    searched_file_type = [constants.File_Type.CandidateModel, constants.File_Type.FootprintModel]
    uploaded_files, current_round = extract_evaluated_files(searched_file_type)
    evaluator_path = f'{DIR_EVALUATOR}/{cluster_id}/{current_round}'
    create_directory(evaluator_path)
    node_cluster_dict = extract_node_files(cluster_id, evaluator_path, uploaded_files, searched_file_type)

    for node_id in node_cluster_dict:
        node_files = node_cluster_dict[node_id]
        valid = True

        for file_type in searched_file_type:
            if file_type.file_name not in node_files:
                print(f"Error: Node {node_id} doesn't have {file_type.file_name} file")
                valid = False

        if valid is not True:
            continue
        
        client = initiate_model_from_hash(node_id, cluster_id, DEVICE)
        footprint_model = torch.load(f'{evaluator_path}/footprint_{node_id}.pth')
        candidate_model = torch.load(f'{evaluator_path}/candidate_{node_id}.pth')
        client.load_model(footprint_model, candidate_model)
        error = client.evaluate()
        # status = constants.Verdict.NEGATIVE
        # if error < ERROR_THRESHOLD:
        status = constants.Verdict.POSITIVE

        print(f"Node: {node_id} has candidate file with a {'Positive' if status == constants.Verdict.POSITIVE else 'Negative'} status")
        mutate_evaluate_file(node_files[f'{constants.File_Type.CandidateModel.file_name}_hash'], status.code)

    kill_current_process()


def setup_trainer_evaluator(trained_evaluator_id):
    print(f"Trainer Evaluator {trained_evaluator_id} ready")
    stages_dict = {
        4:evaluate_train
    }
    setup_rabbit(trained_evaluator_id, stages_dict)


if __name__ == "__main__":
    evaluate_train(21)
    # create_process([21], setup_trainer_evaluator, lambda: advance_stage(5))