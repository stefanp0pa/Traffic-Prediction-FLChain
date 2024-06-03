from devnet_sc_proxy_client import mutate_upload_dataset_file
from devnet_sc_proxy_client import mutate_clear_dataset_file
from devnet_sc_proxy_client import query_get_files_count

DATASET_FILE_PATH = '/Users/stefan/Traffic-Prediction-FLChain/seed-traffic-data/nodes_dataset_ipfs_addr.txt'

def read_file_with_line_numbers(file_path):
    try:
        with open(file_path, 'r') as file:
            for line_number, line_content in enumerate(file, start=1):
                line_content = line_content.strip()
                print(f"Line {line_number}: {line_content}")
                # mutate_clear_dataset_file(line_content, line_number)
                mutate_upload_dataset_file(line_content, line_number)
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

read_file_with_line_numbers(DATASET_FILE_PATH)
