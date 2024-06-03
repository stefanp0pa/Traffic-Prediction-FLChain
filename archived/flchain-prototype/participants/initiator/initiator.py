import tensorflow as tf
from tensorflow.keras import layers, models
import os
import time
import pickle
import subprocess

from pathlib import Path
from multiversx_sdk_core import TokenComputer
from multiversx_sdk_core.transaction_factories import SmartContractTransactionsFactory
from multiversx_sdk_core.transaction_builders.relayed_v1_builder import RelayedTransactionV1Builder
from multiversx_sdk_core import Transaction, TransactionComputer, Address
from multiversx_sdk_wallet.user_signer import UserSigner
from multiversx_sdk_core.transaction_factories import TransactionsFactoryConfig
from multiversx_sdk_core import ContractQueryBuilder
from multiversx_sdk_network_providers import ApiNetworkProvider
from multiversx_sdk_core import AccountNonceHolder

SC_ADDR = "erd1qqqqqqqqqqqqqpgqs80m9r27j5un8v3kpm7zzx2kmdsay53pmgyqpnh426"
WALLET_DIR = "/home/robert/Desktop/Facultate/Licenta//flchain-prototype/participants/initiator/initiator.pem"
INITIATOR_ADDR = "erd1glmnq6c75uedla2dtlc58ll56lwak4jrvlw38pfr64h6p8933ezsaajxtk"
NETWORK_PROVIDER = "https://devnet-api.multiversx.com"
SC_START_SESSION = "start_session"
SC_SET_ACTIVE_ROUND="set_active_round"
GAS_LIMIT = 60000000
MODELS_DIR = '../../models/'
GLOBAL_MODEL_FILE = 'global_model.pkl'
FULL_FILENAME = MODELS_DIR + GLOBAL_MODEL_FILE
NEXT_ROUND = 2

config = TransactionsFactoryConfig(chain_id="D")
transaction_computer = TransactionComputer()
sc_factory = SmartContractTransactionsFactory(config, TokenComputer())
contract_address = Address.from_bech32(SC_ADDR)
initiator = Address.new_from_bech32(INITIATOR_ADDR)
signer = UserSigner.from_pem_file(Path(WALLET_DIR))
network_provider = ApiNetworkProvider(NETWORK_PROVIDER)
nonce_holder = AccountNonceHolder(network_provider.get_account(initiator).nonce)

def sc_start_next_round():
    call_transaction = sc_factory.create_transaction_for_execute(
        sender=initiator,
        contract=contract_address,
        function=SC_SET_ACTIVE_ROUND,
        gas_limit=GAS_LIMIT,
        arguments=[NEXT_ROUND]
    )
    call_transaction.nonce = nonce_holder.get_nonce_then_increment()
    call_transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(call_transaction))

    print(f'>>>[Initiator] Transaction nonce: {call_transaction.nonce}')
    response = network_provider.send_transaction(call_transaction)
    print(f"Transaction hash: {response}")


def sc_start_session(file_id):
    call_transaction = sc_factory.create_transaction_for_execute(
        sender=initiator,
        contract=contract_address,
        function=SC_START_SESSION,
        gas_limit=GAS_LIMIT,
        arguments=[file_id, 200, 10, 10]
    )
    call_transaction.nonce = nonce_holder.get_nonce_then_increment()
    call_transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(call_transaction))

    print(f'>>>[Initiator] Transaction nonce: {call_transaction.nonce}')
    response = network_provider.send_transaction(call_transaction)
    print(f"Transaction hash: {response}")


def upload_global_model_ipfs(weights, directory, filename):
    upload_file = os.path.join(directory, filename)
    with open(upload_file, 'wb') as file:
        pickle.dump(weights, file)
    upload_command = ["ipfs add ", upload_file, " | awk '{print $2}'"]
    upload_file_id = subprocess.run(''.join(upload_command), shell=True, capture_output=True, text=True).stdout[:-1]
    print(f'>>>[Initiator] {filename} was uploaded to IPFS with ID {upload_file_id}')
    return upload_file_id



print(">>>[Initiator] Initializing global model...")

global_model = models.Sequential()
global_model.add(layers.Conv2D(16, (3, 3), activation='relu', input_shape=(28, 28, 1)))
global_model.add(layers.MaxPooling2D((2, 2)))
global_model.add(layers.Flatten())
global_model.add(layers.Dense(10, activation='softmax'))

global_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print(f">>>[Initiator] Global model initialized and saved to {FULL_FILENAME}")
file_id = upload_global_model_ipfs(global_model.get_weights(), MODELS_DIR, GLOBAL_MODEL_FILE)
print(f">>>[Initiator] Global model uploaded to IPFS")

# start session
sc_start_session(file_id)

print(">>>[Initiator] Session started successfully!")

time.sleep(8)
sc_start_next_round()