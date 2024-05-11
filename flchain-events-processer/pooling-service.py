import base64
import requests
import json
import pika
import time

import sys
sys.path.append('../')

from utils.converts import base64_string_to_hex_string, base64_string_to_string, hex_string_to_numeric

API_GATEWAY = 'https://devnet-api.multiversx.com'

ACCOUNTS_PATH = 'accounts'
TRANSACTIONS_PATH = 'transactions'

SC_ADDR = 'erd1qqqqqqqqqqqqqpgqz82nup6jgsxhf0xzx6yyg4xm2tcqsd27ch8quuq97s'
SC_ABI_ADDR = '/Users/stefan/Traffic-Prediction-FLChain/trafficflchain/output/trafficflchain.abi.json'

TRANSFERS_PATH = 'transfers'
TRANSFERS_COUNT_PATH = 'transfers/c'
LOGS_PATH = 'logs'

TRANSACTION_STATUS = {
    'success': 'success',
    'fail': 'fail',
    'pending': 'pending'
}

RABBITMQ_HOST = 'localhost'

def decode_base64(encoded_string):
    try:
        decoded_bytes = base64.b64decode(encoded_string)
        decoded_string = decoded_bytes.decode('utf-8')
        return decoded_string
    except Exception as e:
        return f"Error decoding base64: {str(e)}"

def read_sc_abi(location):
    try:
        with open(location, 'r') as file:
            json_data = json.load(file)
            return json_data
    except FileNotFoundError:
        print(f"File '{location}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file '{location}': {e}")
    except Exception as e:
        print(f"An error occurred while reading or parsing file '{location}': {e}")
    
def get_transaction_details(txHash):
    url = f'{API_GATEWAY}/{TRANSACTIONS_PATH}/{txHash}'
    response = requests.get(url)
    return response.json()

def get_transaction_events(txHash):
    url = f'{API_GATEWAY}/{TRANSACTIONS_PATH}/{txHash}'
    response = requests.get(url)
    response_json = response.json()
    events = response_json['logs']['events']
    return events

def get_latest_sc_transactions(scAddr, fromIndex, size):
    url = f'{API_GATEWAY}/{ACCOUNTS_PATH}/{scAddr}/{TRANSFERS_PATH}?withUsername=true&from={fromIndex}&size={size}'
    response = requests.get(url)
    return sorted(response.json(), key=lambda x: x['nonce'], reverse=True)

def publish_event(event, payload):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange='flchain-events-exchange', exchange_type='direct')
    channel.basic_publish(
        exchange='flchain-events-exchange',
        routing_key=event,
        body=json.dumps(payload)),
    connection.close()
    print(f" [*] Sent event {event} with payload {payload} to RabbitMQ")

def infinite_pooling():
    latest_nonce = 0
    while True:
        print("Pooling latest SC transactions...")
        transactions = get_latest_sc_transactions(SC_ADDR, 0, 5)
        new_latest_nonce = transactions[0]['nonce']
        new_transactions = sorted([tx for tx in transactions if tx['nonce'] > latest_nonce], key=lambda x: x['nonce'], reverse=False)
        txHashes = [tx['txHash'] for tx in new_transactions]
        latest_nonce = new_latest_nonce
        if (len(new_transactions) > 0):
            print(f"New transactions found: {txHashes}")
            for tx in new_transactions:
                txHash = tx['txHash']
                print(f"Getting transaction events for {txHash}")
                transaction_events = get_transaction_events(txHash)
                print(f"Transaction events: {transaction_events}")
                for event in transaction_events:
                    try:
                        event_name = base64_string_to_string(event['topics'][0].rstrip('\x00'))
                        event_payload = base64_string_to_string(event['topics'][1].rstrip('\x00'))
                        print(f"Event name: {event_name}")
                        print(f"Publishing event {event_name} with payload {event_payload}")
                        publish_event(event_name, event_payload)
                    except Exception as e:
                        print(f"Error processing event: {e}")
                        break
        else:
            print("No new transactions found.")
            
        time.sleep(1)

# print(get_transaction_events('56877580598cdc357ee95004b0d71ed1fd4b92eefe9842f8510fdd643f3ac6f7'))
# print(get_latest_sc_transactions(SC_ADDR, 0, 50))
# abi_file = read_sc_abi(SC_ABI_ADDR)
# sc_events = abi_file['events']
# sc_event_identifiers = [event['identifier'] for event in sc_events]
# publish_event("network_setup_event", "caca")
base64_string_to_hex_string("AQ==")
infinite_pooling()