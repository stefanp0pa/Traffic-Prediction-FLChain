from pathlib import Path
from multiversx_sdk import TokenComputer
from multiversx_sdk import SmartContractTransactionsFactory
from multiversx_sdk import Transaction, TransactionComputer, Address
from multiversx_sdk import UserSigner
from multiversx_sdk import TransactionsFactoryConfig
from multiversx_sdk import ContractQueryBuilder
from multiversx_sdk import ApiNetworkProvider
from multiversx_sdk import AccountNonceHolder

PATRON_ADDR = "erd1dwlm0pazs43q0sad8h3r7ueehlzjmhyyq9spryaxruhvfgwych8qgydtwz"
PATRON_WALLET_ADDR = "/Users/stefan/Traffic-Prediction-FLChain/wallets/master.pem"
PATRONAGE_SUM = 500000000000000000 # 0.5 xEGLD

CHAIN_ID = "D"
NETWORK_PROVIDER = "https://devnet-api.multiversx.com"
CHAIN_NAME = "devnet"
GAS_LIMIT = 60000000

transaction_factory_config = TransactionsFactoryConfig(CHAIN_ID)
transaction_computer = TransactionComputer()
sc_factory = SmartContractTransactionsFactory(transaction_factory_config)
network_provider = ApiNetworkProvider(NETWORK_PROVIDER)

nonce_cache = {}

TRAINERS_ADDR_FILE = "/Users/stefan/Traffic-Prediction-FLChain/flchain-official/wallets/trainers_addresses.txt"
AGGREGATORS_ADDR_FILE = "/Users/stefan/Traffic-Prediction-FLChain/flchain-official/wallets/aggregators_addresses.txt"
EVALUATORS_ADDR_FILE = "/Users/stefan/Traffic-Prediction-FLChain/flchain-official/wallets/evaluators_addresses.txt"

def read_lines_to_array(file_path):
    lines_array = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                lines_array.append(line.strip())  # strip() to remove any trailing newline characters
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
    except IOError:
        print(f"An error occurred while reading the file at {file_path}.")
    return lines_array

trainers_addresses = read_lines_to_array(TRAINERS_ADDR_FILE)
aggregators_addreses = read_lines_to_array(AGGREGATORS_ADDR_FILE)
evaluators_addresses = read_lines_to_array(EVALUATORS_ADDR_FILE)

print(f"Trainers addresses: {trainers_addresses}\n")
print(f"Aggregators addresses: {aggregators_addreses}\n")
print(f"Evaluators addresses: {evaluators_addresses}\n")

def seed_account(receiver_addr):
    signer = UserSigner.from_pem_file(Path(PATRON_WALLET_ADDR))
    patron_addr = Address.from_bech32(PATRON_ADDR)
    nonce_holder = AccountNonceHolder(network_provider.get_account(patron_addr).nonce)
    # receiver_addr = Address.from_bech32(receiver_addr)
    transaction = Transaction(
        sender=PATRON_ADDR,
        receiver=receiver_addr,
        gas_limit=GAS_LIMIT,
        chain_id=CHAIN_ID,
        value=PATRONAGE_SUM
    )
    local_nonce = nonce_cache.get(PATRON_ADDR, -1)
    gateway_nonce = nonce_holder.get_nonce_then_increment()
    curr_nonce = max(local_nonce, gateway_nonce) # the higher value is the right one
    nonce_cache[PATRON_ADDR] = curr_nonce + 1
    transaction.nonce = curr_nonce

    # print(f"Current nonce {curr_nonce}\n")
    transaction_computer = TransactionComputer()
    transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(transaction))
    response = network_provider.send_transaction(transaction)
    print(f"Seeded {receiver_addr}. Transaction sent with hash: {response}")


for trainer_addr in trainers_addresses:
    seed_account(trainer_addr)

for aggregate_addr in aggregators_addreses:
    seed_account(aggregate_addr)
    
# for evaluator_addr in evaluators_addresses:
#     seed_account(evaluator_addr)