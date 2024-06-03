from devnet_sc_proxy_client import mutate_upload_cluster_description
from devnet_sc_proxy_client import mutate_clear_cluster_description

DATASET_FILE_PATH = '/Users/stefan/Traffic-Prediction-FLChain/seed-traffic-data/cluster_descriptions.txt'

try:
    with open(DATASET_FILE_PATH, 'r') as file:
        for line_number, line_content in enumerate(file, start=1):
            line_content = line_content.strip()
            line_terms = line_content[1:-1].split(", ")
            for index, term in enumerate(line_terms, start=1):
                cluster_index = int(line_number)
                node_global_index = int(term)
                node_local_index = int(index)
                print(f"Cluster {cluster_index}: with {node_global_index} and index {node_local_index}")
                mutate_upload_cluster_description(cluster_index, node_global_index, node_local_index)
                # mutate_clear_cluster_description(cluster_index, node_global_index)
            # mutate_clear_dataset_file(line_content, line_number)
            # mutate_upload_dataset_file(line_content, line_number)
except FileNotFoundError:
    print(f"The file at {DATASET_FILE_PATH} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")