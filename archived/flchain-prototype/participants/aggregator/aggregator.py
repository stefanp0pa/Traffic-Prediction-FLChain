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
import numpy as np
import os
import sys
import pika
import time
import pickle
import subprocess
import json
import base64
import random
import re

from dotenv import load_dotenv

load_dotenv()

SC_ADDR = "erd1qqqqqqqqqqqqqpgqs80m9r27j5un8v3kpm7zzx2kmdsay53pmgyqpnh426"
WALLET_DIR = "/home/robert/Desktop/Facultate/Licenta//flchain-prototype/participants/aggregator/aggregator.pem"
AGGR_ADDR = "erd1u069qhqrkm4e03u4c6mtwgy0exyshjjrrg24hh70cgww9r3hmaus72t3zr"
NETWORK_PROVIDER = "https://devnet-api.multiversx.com"
SC_DOWNLOAD_LOCAL = "get_local_updates"
SC_NEW_GLOBAL = "set_global_version"
SC_CURRENT_GLOBAL="get_current_global_version"
SC_SET_ACTIVE_ROUND="set_active_round"
GAS_LIMIT = 60000000
MODELS_DIR = '../../models/'
NEXT_ROUND = 4

config = TransactionsFactoryConfig(chain_id="D")
transaction_computer = TransactionComputer()
sc_factory = SmartContractTransactionsFactory(config, TokenComputer())
contract_address = Address.from_bech32(SC_ADDR)
aggregator = Address.new_from_bech32(AGGR_ADDR)
signer = UserSigner.from_pem_file(Path(WALLET_DIR))
network_provider = ApiNetworkProvider(NETWORK_PROVIDER)
nonce_holder = AccountNonceHolder(network_provider.get_account(aggregator).nonce)

def upload_weights_ipfs(weights, directory, filename):
    upload_file = os.path.join(directory, filename)
    with open(upload_file, 'wb') as file:
        pickle.dump(weights, file)
    upload_command = ["ipfs add ", upload_file, " | awk '{print $2}'"]
    upload_file_id = subprocess.run(''.join(upload_command), shell=True, capture_output=True, text=True).stdout[:-1]
    print(f'File {filename} was uploaded to IPFS with ID {upload_file_id}')
    return upload_file_id   

def download_weights_ipfs(file_id, directory, filename):
    download_file = os.path.join(directory, filename)
    with open(download_file, 'w'):
        pass

    download_command = ["ipfs cat ", file_id, " > ", download_file]   
    subprocess.run(''.join(download_command), shell=True, capture_output=True, text=True)
    with open(download_file, 'rb') as file:
        weights = pickle.load(file)
    return weights


def sc_start_next_round():
    call_transaction = sc_factory.create_transaction_for_execute(
        sender=aggregator,
        contract=contract_address,
        function=SC_SET_ACTIVE_ROUND,
        gas_limit=GAS_LIMIT,
        arguments=[NEXT_ROUND]
    )
    call_transaction.nonce = nonce_holder.get_nonce_then_increment()
    print(f'>>>[Aggregator] Transaction nonce: {call_transaction.nonce}')
    call_transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(call_transaction))
    response = network_provider.send_transaction(call_transaction)
    print(f"Transaction hash: {response}")


def sc_set_global_model(file_id):
    call_transaction = sc_factory.create_transaction_for_execute(
        sender=aggregator,
        contract=contract_address,
        function=SC_NEW_GLOBAL,
        gas_limit=GAS_LIMIT,
        arguments=[file_id]
    )
    call_transaction.nonce = nonce_holder.get_nonce_then_increment()
    print(f'>>>[Aggregator] Transaction nonce: {call_transaction.nonce}')
    call_transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(call_transaction))
    response = network_provider.send_transaction(call_transaction)
    print(f"Transaction hash: {response}")

def sc_get_local_updates():
    builder = ContractQueryBuilder(
        contract=contract_address,
        function=SC_DOWNLOAD_LOCAL,
        call_arguments=[],
        caller=aggregator
    )
    query = builder.build()
    response = network_provider.query_contract(query)
    result = base64.b64decode(response.return_data[0]).decode('utf-8').rstrip('\x00')
    print(result)
    parsed = result.split('.')
    parsed = map(lambda x: x.rstrip('\x00'), parsed)
    parsed = list(parsed)
    return parsed[1:]

def sc_current_global_model():
    builder = ContractQueryBuilder(
        contract=contract_address,
        function=SC_CURRENT_GLOBAL,
        call_arguments=[],
        caller=aggregator
    )
    query = builder.build()
    response = network_provider.query_contract(query)
    return base64.b64decode(response.return_data[0]).decode('utf-8').rstrip('\x00')


def on_aggregating_round_started():
    print(f"\n*\n*\n*\n>>>[Aggregator] Aggregating round started!")
    curr_global_id = sc_current_global_model()
    print(f">>>[Aggregator] Current global model ID: {curr_global_id}")
    global_weights = download_weights_ipfs(curr_global_id, MODELS_DIR, "curr_global_model.pkl")
    avg_weights = [np.zeros_like(weight) for weight in global_weights]
    print(f">>>[Aggregator] Downloading local updates...")
    local_updates_ids = sc_get_local_updates()
    print(f">>>[Aggregator] Local updates IDs: {local_updates_ids}")
    for file_id in local_updates_ids:
        print("aa")
        client_weights = download_weights_ipfs(file_id, MODELS_DIR, f'download_result_client_weights.pkl')
        avg_weights = [avg + local for avg, local in zip(avg_weights, client_weights)]

    # Calculate the average of the weights
    avg_weights = [weight / len(local_updates_ids) for weight in avg_weights]
    new_global_id = upload_weights_ipfs(avg_weights, MODELS_DIR, f'new_global_weights.pkl')
    sc_set_global_model(new_global_id)
    print(f">>>[Aggregator] New global model ID: {new_global_id}")
    print(f">>>[Aggregator] Starting the next round, but sleep 5 seconds...")
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
            topic = base64.b64decode(event['topics'][0]).decode('utf-8')
            if (identifier == "set_active_round"):
                if (topic == "aggregation_started_event"):
                    on_aggregating_round_started()
            elif (identifier == "end_session"):
                print(f">>>[Aggregator] Session ended!")
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
        print(f">>>[Aggregator] Successfully connected to RabbitMQ and consuming messages from the queue.")
        channel.start_consuming()
    except Exception as e:
        print(f">>>[Aggregator] Failed to connect to RabbitMQ: {str(e)}")
    finally:
        connection.close()
        sys.exit()
    
print(f">>>[Aggregator] Setting up the events listener...")
setup_events_listener()