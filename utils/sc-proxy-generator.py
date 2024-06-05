import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--dest', type=str, required=True, help='CLIENT DESTINATION')
args = parser.parse_args()

SC_ADDR = "erd1qqqqqqqqqqqqqpgqhq5rwx3effnxvllgpyettrpkwj7a5uyhch8qqmz30z"
CHAIN_ID = "D"
NETWORK_PROVIDER = "https://devnet-api.multiversx.com" if CHAIN_ID == "D" else "https://testnet-api.multiversx.com"
CHAIN_NAME = "devnet" if CHAIN_ID == "D" else "testnet"
GAS_LIMIT = 60000000
ABI_SOURCE = "/Users/stefan/Traffic-Prediction-FLChain/trafficflchain/output/trafficflchain.abi.json" # STEFAN
# ABI_SOURCE  = "/home/robert/Desktop/Facultate/Licenta//Traffic-Prediction-FLChain/trafficflchain/output/trafficflchain.abi.json" # ROBERT
CLIENT_DEST = args.dest
# CLIENT_DEST = f"/home/robert/Desktop/Facultate/Licenta//Traffic-Prediction-FLChain/flchain-proxy/{CHAIN_NAME}_sc_proxy_client.py" # TODO
CALLER_USER_ADDR = "erd1dwlm0pazs43q0sad8h3r7ueehlzjmhyyq9spryaxruhvfgwych8qgydtwz" # STEFAN
WALLET_PATH = "/Users/stefan/Traffic-Prediction-FLChain/wallets/master.pem" # STEFAN
# CALLER_USER_ADDR = "erd1rxufcd8sn9t2k5cavngu60qeeytkuxymajdarnyq5f8enh850wpq8at8xu" # ROBERT
# WALLET_PATH = "/home/robert/Desktop/Facultate/Licenta//Traffic-Prediction-FLChain/wallets/master.pem" # ROBERT

ENDPOINTS_SECTION = "endpoints"
TYPES_SECTION = "types"

def read_abi_file(file_path = ABI_SOURCE):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file {file_path}.")
        exit(1)
 
def insert_imports(file_handler):
    file_handler.write("from pathlib import Path\n")
    file_handler.write("from multiversx_sdk import TokenComputer\n")
    file_handler.write("from multiversx_sdk import SmartContractTransactionsFactory\n")
    file_handler.write("from multiversx_sdk import Transaction, TransactionComputer, Address\n")
    file_handler.write("from multiversx_sdk import UserSigner\n")
    file_handler.write("from multiversx_sdk import TransactionsFactoryConfig\n")
    file_handler.write("from multiversx_sdk import ContractQueryBuilder\n")
    file_handler.write("from multiversx_sdk import ApiNetworkProvider\n")
    file_handler.write("from multiversx_sdk import AccountNonceHolder\n\n")    

def insert_constants(file_handler):
    file_handler.write(f"SC_ADDR = \"{SC_ADDR}\"\n")
    file_handler.write(f"CHAIN_ID = \"{CHAIN_ID}\"\n")
    file_handler.write(f"NETWORK_PROVIDER = \"{NETWORK_PROVIDER}\"\n")
    file_handler.write(f"CHAIN_NAME = \"{CHAIN_NAME}\"\n")
    file_handler.write(f"CALLER_USER_ADDR = \"{CALLER_USER_ADDR}\"\n")
    file_handler.write(f"WALLET_PATH = \"{WALLET_PATH}\"\n")
    file_handler.write(f"GAS_LIMIT = {GAS_LIMIT}\n\n")
    
    file_handler.write("transaction_factory_config = TransactionsFactoryConfig(CHAIN_ID)\n")
    file_handler.write("transaction_computer = TransactionComputer()\n")
    file_handler.write("sc_factory = SmartContractTransactionsFactory(transaction_factory_config)\n")
    file_handler.write("contract_address = Address.from_bech32(SC_ADDR)\n")
    file_handler.write("network_provider = ApiNetworkProvider(NETWORK_PROVIDER)\n\n")
    
    file_handler.write("# Dictionary to store the nonce for each user\n")
    file_handler.write("# The chain gateway is slower in updating the nonce, so we need\n")
    file_handler.write("# to keep track of it to avoid nonce desynchronization errors\n")
    file_handler.write("nonce_cache = {} \n\n")
    # self.user_addr = Address.from_bech32(user_addr)
    # self.signer = UserSigner.from_pem_file(Path(self.wallet_path))
    # self.nonce_holder = AccountNonceHolder(self.network_provider.get_account(self.user_addr).nonce)


# def read_utils(file_path = "/home/robert/Desktop/Facultate/Licenta//Traffic-Prediction-FLChain/utils/converts.py"):
def read_utils(file_path = "/Users/stefan/Traffic-Prediction-FLChain/utils/converts.py"):
    try:
        with open(file_path, 'r') as file:
            data = file.read()
            return data
    except FileNotFoundError:
        print(f"The utils file {file_path} does not exist.")
        exit(1)
        
def choose_decode_method(param_type):
    if param_type == 'u8':
        return 'base64_string_to_numeric'
    elif param_type == 'u16':
        return 'base64_string_to_numeric'
    elif param_type == 'u32':
        return 'base64_string_to_numeric'
    elif param_type == 'u64':
        return 'base64_string_to_numeric'
    elif param_type == 'Address':
        return 'base64_string_to_bech32_address'
    elif param_type == 'List<Address>':
        return 'base64_string_to_array_of_bech32_addresses'
    elif param_type == "List<byte>" or param_type == "List<u8>":
        return 'base64_string_to_bytes'
    elif param_type == "List<u16>":
        return 'base64_string_to_list_u16'
    elif param_type == "List<File>":
        return 'base64_string_to_file_array'
    elif param_type == "File":
        return 'base64_string_to_file'
    elif param_type == "TrainingData":
        return 'base64_string_to_training_data'
    elif param_type == "bytes":
        return 'base64_string_to_bytes'
    elif param_type == "GraphTopology":
        return 'base64_string_to_graphTopology'
    elif param_type == "variadic<array46<u8>>" or param_type == "List<array46<u8>>":
        return 'base64_string_to_ipfs_addresses'
    elif param_type == "array46<u8>":
        return 'base64_string_to_ipfs_address'
    elif param_type == "List<ClusterNode>":
        return 'base64_string_to_list_cluster_node'
    elif param_type == "NodeCluster":
        return 'base64_string_to_node_cluser'
    else:
        return 'base64_string_to_numeric'

print(f"[*] Started generating the client file at location {CLIENT_DEST}...")

abi_file_content = read_abi_file()
utils_methods = read_utils()
types_sectipn = abi_file_content[TYPES_SECTION]
endpoints_section = abi_file_content[ENDPOINTS_SECTION]

available_types = []
available_mutable_endpoints = []
available_immutable_endpoints = []
ignored_endpoints = ['upgrade']

def process_query_input(input):
    input_type = input['type']
    if input_type == 'Address':
        return f"Address.new_from_bech32({input['name']})"
    else:
        return input['name']

def generate_for_immutable_endpoint(file_handle, endpoint_data):
    method_name = f"query_{endpoint_data['name']}"
    inputs_seq = ', '.join([f"{input['name']}" for input in endpoint_data['inputs']])
    if len(endpoint_data['inputs']) > 0:
        inputs_seq += ', '
    inputs_seq += "caller_user_addr = CALLER_USER_ADDR"
    
    file_handle.write(f"def {method_name}({inputs_seq}):\n")
    file_handle.write("\tbuilder = ContractQueryBuilder(\n")
    file_handle.write(f"\t\tcontract = contract_address,\n")
    file_handle.write(f"\t\tfunction = \"{endpoint_data['name']}\",\n")
    file_handle.write("\t\tcall_arguments = [")
    
    query_inputs = endpoint_data['inputs']
    query_inputs = map(process_query_input, query_inputs)
    call_input_seq = ', '.join([f"{input}" for input in query_inputs])
    file_handle.write(f"{call_input_seq}")
    
    file_handle.write("],\n")
    file_handle.write("\t\tcaller = Address.from_bech32(caller_user_addr)\n")
    file_handle.write("\t)\n")
    file_handle.write("\tquery = builder.build()\n")
    file_handle.write(f"\tprint(f'>>>Performing immutable query to {endpoint_data['name']}...')\n")
    file_handle.write("\tresponse = network_provider.query_contract(query).to_dictionary()\n")
    file_handle.write("\tprint(response)\n")
    file_handle.write("\treturn_code = response['returnCode']\n")
    file_handle.write("\tif return_code != 'ok':\n")
    file_handle.write("\t\tprint('Error in the response')\n")
    file_handle.write("\t\treturn None\n")
    
    # file_handle.write("\treturn_message = response['returnMessage']\n")
    # file_handle.write("\tgas_used = response['gasUsed']\n")
    file_handle.write("\treturn_data = response['returnData']\n")
    output_type = endpoint_data['outputs'][0]['type']
    print(f"Output type: {output_type} for endpoint {endpoint_data['name']}")
    file_handle.write(f"\toutput_type = \'{output_type}\'\n")
    file_handle.write("\treturn_data = return_data[0]\n")
    file_handle.write(f"\tdecode_method = {choose_decode_method(output_type)}\n")
    file_handle.write("\tdecoded_response = decode_method(return_data)\n")
    file_handle.write("\tprint(decoded_response)\n")
    file_handle.write("\treturn decoded_response\n\n\n")


def generate_for_mutable_endpoint(file_handle, endpoint_data):
    method_name = f"mutate_{endpoint_data['name']}"
    inputs_seq = ', '.join([f"{input['name']}" for input in endpoint_data['inputs']])
    if len(endpoint_data['inputs']) > 0:
        inputs_seq += ', '
    if "payableInTokens" in endpoint_data and endpoint_data['payableInTokens'][0] == '*':
        inputs_seq += 'native_amount = 1, '
    inputs_seq += 'wallet_path = WALLET_PATH, caller_user_addr = CALLER_USER_ADDR'
    file_handle.write(f"def {method_name}({inputs_seq}):\n")
    if len(endpoint_data['inputs']) > 0:
        file_handle.write("\t\"\"\"Parameters description\n")
        for input in endpoint_data['inputs']:
            file_handle.write(f"\t\t{input['name']} - {input['type']}\n")
        file_handle.write("\t\"\"\"\n")
    
    file_handle.write("\tsigner = UserSigner.from_pem_file(Path(wallet_path))\n")
    file_handle.write("\tuser_addr = Address.from_bech32(caller_user_addr)\n")
    file_handle.write("\tnonce_holder = AccountNonceHolder(network_provider.get_account(user_addr).nonce)\n")
    file_handle.write("\tcall_transaction = sc_factory.create_transaction_for_execute(\n")
    file_handle.write(f"\t\tsender=user_addr,\n")
    file_handle.write(f"\t\tcontract=contract_address,\n")
    file_handle.write(f"\t\tfunction=\"{endpoint_data['name']}\",\n")
    file_handle.write(f"\t\tgas_limit={GAS_LIMIT},\n")
    if "payableInTokens" in endpoint_data and endpoint_data['payableInTokens'][0] == '*':
        file_handle.write("\t\tnative_transfer_amount=native_amount,\n")
    file_handle.write("\t\targuments=[")
    file_handle.write(', '.join([f"{input['name']}" for input in endpoint_data['inputs']]))
    file_handle.write("]\n")
    file_handle.write("\t)\n")
    file_handle.write("\tlocal_nonce = nonce_cache.get(caller_user_addr, -1)\n")
    file_handle.write("\tgateway_nonce = nonce_holder.get_nonce_then_increment()\n")
    file_handle.write("\tcurr_nonce = max(local_nonce, gateway_nonce) # the higher value is the right one\n")
    file_handle.write("\tnonce_cache[caller_user_addr] = curr_nonce + 1 # setting the next nonce value\n")
    file_handle.write("\tcall_transaction.nonce = curr_nonce\n")
    file_handle.write("\tcall_transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(call_transaction))\n")
    file_handle.write(f"\tprint(f'>>>Performing mutable call to {endpoint_data['name']}...')\n")
    file_handle.write("\tresponse = network_provider.send_transaction(call_transaction)\n")
    file_handle.write("\tprint(f'>>>Transaction hash: {response}')\n\n")
    

with open(CLIENT_DEST, 'w') as file:
    print(f'[*] Started generating the client file at location {CLIENT_DEST}...')
    file.write("# CODE AUTOMATICALLY GENERATED BY sc-proxy-generator.py\n\n")
    file.write(utils_methods)
    file.write("\n\n")
    insert_imports(file)
    insert_constants(file)
    
    mutable_endpoints = [endpoint for endpoint in endpoints_section
                         if endpoint['mutability'] == 'mutable' and endpoint['name'] not in ignored_endpoints]
    immutable_endpoints = [endpoint for endpoint in endpoints_section
                           if endpoint['mutability'] == 'readonly' and endpoint['name'] not in ignored_endpoints]
    
    print(f"Mutable endpoints: {mutable_endpoints}")
    print(f"Immutable endpoints: {immutable_endpoints}")
    
    for endpoint in immutable_endpoints:
        generate_for_immutable_endpoint(file, endpoint)
        
    for endpoint in mutable_endpoints:
        generate_for_mutable_endpoint(file, endpoint)
        
print(f"[*] Finished generating the client file at location {CLIENT_DEST}!")