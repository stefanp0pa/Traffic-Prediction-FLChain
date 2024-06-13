import base64
import requests
import json
import pika
import time
import logging

API_GATEWAY = 'https://devnet-api.multiversx.com'
LOGGER_OUTPUT = 'pooling-service.log'

ACCOUNTS_PATH = 'accounts'
TRANSACTIONS_PATH = 'transactions'

BLOCK_COMMIT_DELAY = 6
LATEST_TX_COUNT = 50
TX_PAGE_SIZE = 50

SC_ADDRS = ['erd1qqqqqqqqqqqqqpgq3fx434vuswz3qsf54kg8w0uxqzqx5dvfch8qcf53r6',
            'erd1qqqqqqqqqqqqqpgq79af8p2pk7ha2p4tkccznut78gdh4ezgch8qpczmcf',
            'erd1qqqqqqqqqqqqqpgq9ekh642qhpp3y3t2q226afjdm64d72awch8qlzfeda',
            'erd1qqqqqqqqqqqqqpgqqwptcz58e2dd5np9gg7ak6lakhnjzv3zch8q3nduxs']
SC_INDEX = [3, 4, 5, 6]
index = 3

TRANSFERS_PATH = 'transfers'
TRANSFERS_COUNT_PATH = 'transfers/c'

SC_ADDR = SC_ADDRS[index]

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler(f"{SC_INDEX[index]}_{SC_ADDR}-transactions.json"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

ingested_transactions = []

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

def ingest_existing_txs(tx_count):
    ingested_transactions = []
    for i in range(0, tx_count, TX_PAGE_SIZE):
        # logger.info(f"Getting transactions page {i}...")
        fields_to_extract = ['txHash', 'function', 'fee', 'gasUsed', 'gasLimit', 'gasPrice', 'nonce', 'timestamp', 'sender', 'receiver']
        transactions = get_sc_transactions_page(SC_ADDR, i, TX_PAGE_SIZE)
        filtered_transactions = [
            {key: element[key] for key in fields_to_extract}
            for element in transactions
        ]
        ingested_transactions += filtered_transactions
    ingested_transactions.reverse()
    return ingested_transactions

tx_count = get_transactions_count(SC_ADDR)   
# logger.info(f"There are {tx_count} transactions in SC {SC_ADDR} to be ingested before proceeding to pooling...!")

ingested_transactions = ingest_existing_txs(tx_count)
logger.info(json.dumps(ingested_transactions, indent=2))
# for tx in ingested_transactions:
#     logger.info(tx)