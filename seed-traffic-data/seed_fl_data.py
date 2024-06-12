import time
from devnet_sc_proxy_client import mutate_upload_adj_matrix_file, mutate_clear_adj_matrix_file
from devnet_sc_proxy_client import mutate_upload_dataset_file, mutate_clear_dataset_file
from devnet_sc_proxy_client import mutate_upload_cluster_aggregation_file, mutate_clear_cluster_aggregation_file
from devnet_sc_proxy_client import mutate_upload_cluster_description, mutate_clear_cluster_description
from devnet_sc_proxy_client import mutate_upload_footprint_model_file, mutate_clear_footprint_model_file
from devnet_sc_proxy_client import query_get_round, mutate_set_round

SC_ADDR = 'erd1qqqqqqqqqqqqqpgq3fx434vuswz3qsf54kg8w0uxqzqx5dvfch8qcf53r6'
CALLER_ADDR = 'erd1dwlm0pazs43q0sad8h3r7ueehlzjmhyyq9spryaxruhvfgwych8qgydtwz'
WALLET_PATH = '/Users/stefan/Traffic-Prediction-FLChain/wallets/master.pem'

ADJ_MATRICES_FILE = '/Users/stefan/Traffic-Prediction-FLChain/seed-traffic-data/adj_matrices_ipfs_addr.txt' # 22
DATASET_FILE = '/Users/stefan/Traffic-Prediction-FLChain/seed-traffic-data/nodes_dataset_ipfs_addr.txt' # 206
AGGR_MODELS_FILE = '/Users/stefan/Traffic-Prediction-FLChain/seed-traffic-data/cluster_models_ipfs_addr.txt' # 22
FOOTPRINT_MODELS_FILE = '/Users/stefan/Traffic-Prediction-FLChain/seed-traffic-data/nodes_footprints_ipfs_addr.txt' # 206
CLUSTER_DESC_FILE = '/Users/stefan/Traffic-Prediction-FLChain/seed-traffic-data/cluster_descriptions.txt'

def seed_adj_matrices_files():
    try:
        with open(ADJ_MATRICES_FILE, 'r') as file:
            for line_number, line_content in enumerate(file, start=1):
                line_content = line_content.strip()
                ipfs_addr = line_content
                cluster_index = line_number
                print(f"Seeding adj. matrix at {ipfs_addr} for cluster {cluster_index}")
                mutate_upload_adj_matrix_file(
                    file_location=ipfs_addr,
                    cluster_index=cluster_index,
                    wallet_path=WALLET_PATH,
                    caller_user_addr=CALLER_ADDR
                )
            print('✅ Done seeding adj. matrices files.')
    except FileNotFoundError:
        print(f"The file at {ADJ_MATRICES_FILE} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def seed_dataset_files():
    try:
        with open(DATASET_FILE, 'r') as file:
            for line_number, line_content in enumerate(file, start=1):
                line_content = line_content.strip()
                parts = line_content.split(',')
                ipfs_addr = parts[2][1:-1]
                global_node_index = int(parts[1])
                cluster_index = int(parts[0])
                print(f"Seeding dataset file at {ipfs_addr} for node {global_node_index} and cluster {cluster_index}")
                mutate_upload_dataset_file(
                    file_location=ipfs_addr,
                    global_node_index=global_node_index,
                    cluster_index=cluster_index,
                    wallet_path=WALLET_PATH,
                    caller_user_addr=CALLER_ADDR
                )
            print('✅ Done seeding dataset files.')
    except FileNotFoundError:
        print(f"The file at {DATASET_FILE} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def seed_aggregation_cluster_model_files():
    try:
        with open(AGGR_MODELS_FILE, 'r') as file:
            for line_number, line_content in enumerate(file, start=1):
                line_content = line_content.strip()
                ipfs_addr = line_content
                cluster_index = line_number
                print(f"Seeding aggregation model at {ipfs_addr} address for cluster {cluster_index}")
                mutate_upload_cluster_aggregation_file(
                    file_location=ipfs_addr,
                    cluster_index=cluster_index,
                    wallet_path=WALLET_PATH,
                    caller_user_addr=CALLER_ADDR
                )
            print('✅ Done seeding aggregation cluster model files.')
    except FileNotFoundError:
        print(f"The file at {AGGR_MODELS_FILE} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def seed_footprint_model_files():
    try:
        with open(FOOTPRINT_MODELS_FILE, 'r') as file:
            for line_number, line_content in enumerate(file, start=1):
                line_content = line_content.strip()
                parts = line_content.split(',')
                ipfs_addr = parts[2][1:-1]
                global_node_index = int(parts[1])
                cluster_index = int(parts[0])
                print(f"Seeding footprint file at address {ipfs_addr} for node {global_node_index} in cluster {cluster_index}")
                mutate_upload_footprint_model_file(
                    file_location=ipfs_addr,
                    global_node_index=global_node_index,
                    cluster_index=cluster_index,
                    wallet_path=WALLET_PATH,
                    caller_user_addr=CALLER_ADDR
                )
            print('✅ Done seeding footprint model files.')
    except FileNotFoundError:
        print(f"The file at {FOOTPRINT_MODELS_FILE} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def seed_cluster_descriptions():
    try:
        with open(CLUSTER_DESC_FILE, 'r') as file:
            for line_number, line_content in enumerate(file, start=1):
                line_content = line_content.strip()
                line_terms = line_content[1:-1].split(", ")
                for index, term in enumerate(line_terms, start=1):
                    cluster_index = int(line_number)
                    global_node_index = int(term)
                    local_node_index = int(index)
                    print(f"Cluster {cluster_index}: with global index {global_node_index} and local index {local_node_index}")
                    mutate_upload_cluster_description(
                        cluster_index=cluster_index,
                        global_node_index=global_node_index,
                        local_node_index=local_node_index,
                        wallet_path=WALLET_PATH,
                        caller_user_addr=CALLER_ADDR
                    )
            print('✅ Done seeding cluster descriptions.')
    except FileNotFoundError:
        print(f"The file at {CLUSTER_DESC_FILE} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

print(f">>> Starting the seeding process for SC: {SC_ADDR}...")
curr_round = query_get_round(CALLER_ADDR)
if curr_round != 0:
    mutate_set_round(0, WALLET_PATH, CALLER_ADDR)
    print(f"Resetting round to 0 for SC: {SC_ADDR}")
    time.sleep(12)
    
# seed_adj_matrices_files()
# seed_dataset_files()
# seed_aggregation_cluster_model_files()
# seed_footprint_model_files()
# seed_cluster_descriptions()

# 456 total files = 22 + 22 + 206 + 206