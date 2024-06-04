from devnet_sc_proxy_client import mutate_upload_footprint_model_file
from devnet_sc_proxy_client import mutate_clear_footprint_model_file

DATASET_FILE_PATH = '/Users/stefan/Traffic-Prediction-FLChain/seed-traffic-data/nodes_footprints_ipfs_addr.txt'

def read_file_with_line_numbers(file_path):
    try:
        with open(file_path, 'r') as file:
            for line_number, line_content in enumerate(file, start=1):
                line_content = line_content.strip()
                parts = line_content.split(',')
                address = parts[2][1:-1]
                global_node_index = parts[1]
                cluster_index = parts[0]
                print(f"Seeding footprint file at address {address} for node {global_node_index} in cluster {cluster_index}")
                mutate_upload_footprint_model_file(address, int(global_node_index), int(cluster_index))
                # mutate_clear_footprint_model_file(address, int(global_node_index), int(cluster_index), 0)
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

read_file_with_line_numbers(DATASET_FILE_PATH)
