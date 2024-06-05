from tensorflow.keras import layers, models
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical

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
import tensorflow as tf
import os
import time
import sys
import pika
import pickle
import subprocess
import json
import base64
import random
from dotenv import load_dotenv

load_dotenv()

SC_ADDR = "erd1qqqqqqqqqqqqqpgqs80m9r27j5un8v3kpm7zzx2kmdsay53pmgyqpnh426"
WALLET_DIR = "/home/robert/Desktop/Facultate/Licenta//flchain-prototype/participants/evaluator/evaluator.pem"
EVALUATOR_ADDR = "erd19gpr46ga46wnv669mkspwwrwcuc8eegn7enlgg7dh9qcjyn86mus09j4k9"
NETWORK_PROVIDER = "https://devnet-api.multiversx.com"
SC_CURRENT_GLOBAL="get_current_global_version"
SC_SET_ACTIVE_ROUND="set_active_round"
SC_END_SESSION="end_session"
GAS_LIMIT = 60000000
MODELS_DIR = '../../models/'
NEXT_ROUND = 2

config = TransactionsFactoryConfig(chain_id="D")
transaction_computer = TransactionComputer()
sc_factory = SmartContractTransactionsFactory(config, TokenComputer())
contract_address = Address.from_bech32(SC_ADDR)
evaluator = Address.new_from_bech32(EVALUATOR_ADDR)
signer = UserSigner.from_pem_file(Path(WALLET_DIR))
network_provider = ApiNetworkProvider(NETWORK_PROVIDER)
nonce_holder = AccountNonceHolder(network_provider.get_account(evaluator).nonce)

print(f">>>[Evaluator] Loaded dataset")
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
train_images = train_images.reshape((60000, 28, 28, 1)).astype('float32') / 255
test_images = test_images.reshape((10000, 28, 28, 1)).astype('float32') / 255

train_labels = to_categorical(train_labels)
test_labels = to_categorical(test_labels)

global_model = models.Sequential()
global_model.add(layers.Conv2D(16, (3, 3), activation='relu', input_shape=(28, 28, 1)))
global_model.add(layers.MaxPooling2D((2, 2)))
global_model.add(layers.Flatten())
global_model.add(layers.Dense(10, activation='softmax'))
global_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

def sc_end_session():
    call_transaction = sc_factory.create_transaction_for_execute(
        sender=evaluator,
        contract=contract_address,
        function=SC_END_SESSION,
        gas_limit=GAS_LIMIT,
        arguments=[]
    )
    call_transaction.nonce = nonce_holder.get_nonce_then_increment()
    print(f'>>>[Evaluator] Transaction nonce: {call_transaction.nonce}')
    call_transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(call_transaction))
    response = network_provider.send_transaction(call_transaction)
    print(f"Transaction hash: {response}")


def sc_current_global_model():
    builder = ContractQueryBuilder(
        contract=contract_address,
        function=SC_CURRENT_GLOBAL,
        call_arguments=[],
        caller=evaluator
    )
    query = builder.build()
    response = network_provider.query_contract(query)
    return base64.b64decode(response.return_data[0]).decode('utf-8').rstrip('\x00')


def sc_start_next_round():
    call_transaction = sc_factory.create_transaction_for_execute(
        sender=evaluator,
        contract=contract_address,
        function=SC_SET_ACTIVE_ROUND,
        gas_limit=GAS_LIMIT,
        arguments=[NEXT_ROUND]
    )
    call_transaction.nonce = nonce_holder.get_nonce_then_increment()
    print(f'>>>[Evaluator] Transaction nonce: {network_provider.get_account(evaluator).nonce}')
    call_transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(call_transaction))
    response = network_provider.send_transaction(call_transaction)
    print(f"Transaction hash: {response}")


def download_weights_ipfs(file_id, directory, filename):
    download_file = os.path.join(directory, filename)
    with open(download_file, 'w'):
        pass

    download_command = ["ipfs cat ", file_id, " > ", download_file]   
    subprocess.run(''.join(download_command), shell=True, capture_output=True, text=True)
    with open(download_file, 'rb') as file:
        weights = pickle.load(file)
    return weights


def on_evaluating_round_started():
    print(f"\n*\n*\n*\n>>>[Evaluator] Evaluating round started!")
    global_file_id = sc_current_global_model()
    print(f">>>[Evaluator] Downloading global model for round {round} with file ID: {global_file_id}...")
    global_weights = download_weights_ipfs(
        global_file_id, MODELS_DIR, f'evalutor_weights.pkl')
    print(f">>>[Evaluator] Downloaded global model for round {round}!")
    global_model.set_weights(global_weights)
    test_loss, test_acc = global_model.evaluate(test_images, test_labels)
    print(f'\n>>>[Evaluator] Final Test Accuracy: {test_acc}')
    print(f'>>>[Evaluator] Final Test Loss: {test_loss}')
    
    if (test_acc > 0.94) :
        print(f">>>[Evaluator] Accuracy is greater than 0.94, so we will stop the session...")
        time.sleep(8)
        sc_end_session()
        print(f">>>[Evaluator] Session ended!")
        sys.exit()
    else:
        print(f">>>[Evaluator] Accuracy is less than 0.94, so we will continue the training!")
        time.sleep(8)
        sc_start_next_round()


def process_blockchain_event(channel, method, properties, body):
    events = json.loads(body.decode('utf-8'))
    just_events = events.get('events', [])
    possible_events = [
        "start_session",
        "end_session",
        "signup",
        "set_active_round",
        "signup_started_event",
        "training_started_event",
        "aggregation_started_event",
        "evaluation_started_event"]

    for event in just_events:
        if event['identifier'] in possible_events:
            identifier = event['identifier']
            topic = base64.b64decode(event['topics'][0]).decode('utf-8').rstrip('\x00')
            if (identifier == "set_active_round"):
                if (topic == "evaluation_started_event"):
                    on_evaluating_round_started()
            elif (identifier == "end_session"):
                print(f">>>[Evaluator] Session ended!")
                sys.exit()


def setup_events_listener():
    host = os.getenv("BEACONX_HOST")
    port = os.getenv("BEACONX_PORT")
    username = os.getenv("BEACONX_USER")
    password = os.getenv("BEACONX_PASSWORD")
    virtual_host = os.getenv("BEACONX_VIRTUAL_HOST")
    queue_name = os.getenv("BEACONX_QUEUE")
    credentials = pika.PlainCredentials(username, password)
    parameters = pika.ConnectionParameters(host=host, port=port, virtual_host=virtual_host, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    try:
        channel = connection.channel()
        channel.basic_consume(queue=queue_name, on_message_callback=process_blockchain_event, auto_ack=True)
        print(f">>>[Evaluator] Successfully connected to RabbitMQ and consuming messages from the queue.")
        channel.start_consuming()
    except Exception as e:
        print(f">>>[Evaluator] Failed to connect to RabbitMQ: {str(e)}")
    finally:
        connection.close()
        sys.exit()
        
print(f">>>[Evaluator] Setting up the events listener...")
setup_events_listener()