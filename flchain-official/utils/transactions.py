import requests
import constants

def get_latest_sc_transactions(scAddr, fromIndex, size):
    url = f'{constants.API_GATEWAY}/{constants.ACCOUNTS_PATH}/{scAddr}/{constants.TRANSFERS_PATH}?withUsername=true&from={fromIndex}&size={size}'
    response = requests.get(url)
    content = response.json()
    content = [item for item in content if 'nonce' in item]
    return sorted(content, key=lambda x: x['nonce'], reverse=True)


def get_transaction_events(txHash):
    url = f'{constants.API_GATEWAY}/{constants.TRANSACTIONS_PATH}/{txHash}'
    response = requests.get(url)
    response_json = response.json()
    events = response_json['logs']['events']
    return events