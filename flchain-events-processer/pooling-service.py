import base64
import requests
import json
import pika
import time

from events_reader_client import show_all_event_types
from events_reader_client import show_all_ignore_events
from events_reader_client import read_event_payload
from events_reader_client import base64_string_to_string

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

def decode_payload(event_name, payload):
    available_events = show_all_event_types()
    if event_name not in available_events:
        print(f"Event {event_name} not found in available events: {available_events}")
        return
    return read_event_payload(event_name, payload)
    
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
    print(f"[*] Sent event {event} with payload {payload} to RabbitMQ")

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
            print(f"New transactions found: {txHashes}\n\n")
            for tx in new_transactions:
                txHash = tx['txHash']
                print(f"Getting transaction events for {txHash}")
                transaction_events = get_transaction_events(txHash)
                print(f"Transaction events: {transaction_events}")
                for event in transaction_events:
                    try:
                        event_identifier = event['identifier']
                        if event_identifier in show_all_ignore_events():
                            print(f"Ignored event {event_identifier} for transaction {txHash}!")
                            continue
                        
                        event_name = base64_string_to_string(event['topics'][0].rstrip('\x00'))
                        event_payload = decode_payload(event_name, event['topics'])
                        
                        # print(f"Event name: {event_name}")
                        # print(f"Publishing event {event_name} with payload {event_payload}")
                        publish_event(event_name, event_payload)
                    except Exception as e:
                        print(f"Error processing event {event['identifier']} with exception: {e}")
                        continue
                print('\n\n')
        else:
            print("No new transactions found.")
            
        time.sleep(1)

infinite_pooling()