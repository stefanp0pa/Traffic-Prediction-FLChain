import base64
import requests
import json
import pika
import time
import logging

from events_reader_client import show_all_event_types
from events_reader_client import show_all_ignore_events
from events_reader_client import read_event_payload
from events_reader_client import base64_string_to_string

API_GATEWAY = 'https://devnet-api.multiversx.com'
LOGGER_OUTPUT = 'pooling-service.log'

ACCOUNTS_PATH = 'accounts'
TRANSACTIONS_PATH = 'transactions'

BLOCK_COMMIT_DELAY = 6
LATEST_TX_COUNT = 50
TX_PAGE_SIZE = 50

SC_ADDR = 'erd1qqqqqqqqqqqqqpgq3fx434vuswz3qsf54kg8w0uxqzqx5dvfch8qcf53r6'
SC_ABI_ADDR = '/home/robert/Desktop/Facultate/Licenta//Traffic-Prediction-FLChain/trafficflchain/output/trafficflchain.abi.json'

TRANSFERS_PATH = 'transfers'
TRANSFERS_COUNT_PATH = 'transfers/c'
LOGS_PATH = 'logs'

TRANSACTION_STATUS = {
    'success': 'success',
    'fail': 'fail',
    'pending': 'pending'
}

RABBITMQ_HOST = 'localhost'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGGER_OUTPUT),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

ingested_transactions = []

def decode_payload(event_name, payload):
    available_events = show_all_event_types()
    if event_name not in available_events:
        logger.warning(f"Event {event_name} not found in available events: {available_events}")
        return
    return read_event_payload(event_name, payload)

def get_transaction_events(txHash, retries_count = 3):
    url = f'{API_GATEWAY}/{TRANSACTIONS_PATH}/{txHash}'
    for attempt in range(retries_count):
        try:
            response = requests.get(url)
            response_json = response.json()
            # print(response_json) # enable if show full transaction details
            logs = response_json.get('logs', {})
            if 'logs' not in response_json:
                raise KeyError("Missing 'logs' key or 'logs' is not a dictionary")
            if 'events' not in response_json['logs']:
                raise KeyError("Missing 'events' key or 'events' is not a dictionary")
            return response_json['logs']['events']
        except Exception as e:
            logger.debug(f"Attempt {attempt + 1} failed for url {url}: {e}")
            if attempt < retries_count - 1:
                time.sleep(retries_count)  # optional: add delay between retries
            else:
                logger.error("❌ Failed to retrieve transaction events for url: {url}!")
                return []

def get_latest_sc_transactions(scAddr, fromIndex, size, retries_count = 3):
    url = f'{API_GATEWAY}/{ACCOUNTS_PATH}/{scAddr}/{TRANSFERS_PATH}?withUsername=true&from={fromIndex}&size={size}'
    for attempt in range(retries_count):
        try:    
            response = requests.get(url)
            content = response.json()
            content = [item for item in content if 'nonce' in item]
            return sorted(content, key=lambda x: x['nonce'], reverse=True)
        except (requests.RequestException, ValueError, KeyError) as e:
            logger.debug(f"Attempt {attempt + 1} failed for url {url}: {e}")
            if attempt < retries_count - 1:
                time.sleep(retries_count)  # optional: add delay between retries
            else:
                logger.error(f"❌ Failed to retrieve transaction events for url: {url}!")
                return []

def get_sc_transactions_page(scAddr, fromIndex, size, retries_count = 3):
    url = f'{API_GATEWAY}/{ACCOUNTS_PATH}/{scAddr}/{TRANSFERS_PATH}?withUsername=true&from={fromIndex}&size={size}'
    for attempt in range(retries_count):
        try:
            response = requests.get(url)
            return response.json()
        except (requests.RequestException, ValueError, KeyError) as e:
            logger.debug(f"Attempt {attempt + 1} failed for url {url}: {e}")
            if attempt < retries_count - 1:
                time.sleep(retries_count)
            else:
                logger.error(f"❌ Failed to retrieve transaction events for url: {url}!")
                return []

def get_transactions_count(scAddr, retries_count = 3):
    url = f'{API_GATEWAY}/{ACCOUNTS_PATH}/{scAddr}/{TRANSFERS_COUNT_PATH}'
    for attempt in range(retries_count):
        try:
            response = requests.get(url)
            return response.json()
        except (requests.RequestException, ValueError, KeyError) as e:
            logger.debug(f"Attempt {attempt + 1} failed for url {url}: {e}")
            if attempt < retries_count - 1:
                time.sleep(retries_count)
            else:
                logger.error(f"Failed to retrieve transaction count for SC {SC_ADDR}!")
                return 0

def publish_event(event, payload):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange='flchain-events-exchange', exchange_type='direct')
    channel.basic_publish(
        exchange='flchain-events-exchange',
        routing_key=event,
        body=json.dumps(payload)),
    connection.close()
    logger.info(f"✅ Sent event {event} with payload {payload} to RabbitMQ")

def cross_filter_latest_transactions(received_transactions, sc_transactions):
    received_tx_hashes = [tx['txHash'] for tx in received_transactions]
    sc_tx_hashes = [tx['txHash'] for tx in sc_transactions]
    not_processed_txs = [tx for tx in received_transactions if tx['txHash'] not in sc_tx_hashes]
    return not_processed_txs

def infinite_pooling():
    latest_nonce = 0
    while True:
        logger.info("Pooling latest SC transactions...")
        received_transactions = get_latest_sc_transactions(SC_ADDR, 0, LATEST_TX_COUNT)
        if len(received_transactions) == 0:
            logger.info("No new transactions found!")
            time.sleep(BLOCK_COMMIT_DELAY)
            continue
        
        received_transactions.reverse()
        new_transactions = cross_filter_latest_transactions(received_transactions, ingested_transactions)
        if (len(new_transactions) > 0):
            txHashes = [tx['txHash'] for tx in new_transactions]
            logger.info(f"\nNew transactions found: {txHashes}\n")
            for tx in new_transactions:
                ingested_transactions.append(tx)
                txHash = tx['txHash']
                logger.info(f"Getting transaction events for {txHash}")
                transaction_events = get_transaction_events(txHash)
                # print(f"Transaction events: {transaction_events}") # enable if show full transaction events
                for event in transaction_events:
                    try:
                        event_identifier = event['identifier']
                        if event_identifier in show_all_ignore_events():
                            # print(f"Ignored event {event_identifier} for transaction {txHash}!")
                            continue
                        
                        event_name = base64_string_to_string(event['topics'][0].rstrip('\x00'))
                        event_payload = decode_payload(event_name, event['topics'])
                        
                        # print(f"Event name: {event_name}")
                        # print(f"Publishing event {event_name} with payload {event_payload}")
                        publish_event(event_name, event_payload)
                    except Exception as e:
                        logger.error(f"Error processing event {event['identifier']} with exception: {e}")
                        continue
        else:
            logger.info("No new transactions found!")
            
        time.sleep(BLOCK_COMMIT_DELAY)

def ingest_existing_txs(tx_count):
    ingested_transactions = []
    for i in range(0, tx_count, TX_PAGE_SIZE):
        logger.info(f"Getting transactions page {i}...")
        fields_to_extract = ['txHash', 'gasLimit', 'gasPrice', 'gasUsed', 'nonce', 'timestamp', 'function', 'sender', 'receiver']
        transactions = get_sc_transactions_page(SC_ADDR, i, TX_PAGE_SIZE)
        filtered_transactions = [
            {key: element[key] for key in fields_to_extract}
            for element in transactions
        ]
        ingested_transactions += filtered_transactions
    ingested_transactions.reverse()
    return ingested_transactions

tx_count = get_transactions_count(SC_ADDR)   
logger.info(f"There are {tx_count} transactions in SC {SC_ADDR} to be ingested before proceeding to pooling...!")

ingested_transactions = ingest_existing_txs(tx_count)
infinite_pooling()