from enum import Enum

API_GATEWAY = 'https://devnet-api.multiversx.com'

ACCOUNTS_PATH = 'accounts'
TRANSACTIONS_PATH = 'transactions'

SC_ADDR = 'erd1qqqqqqqqqqqqqpgq3vwx0z53r8km2re2xzqljzgwuffr83kkch8qpg4u8m'
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


AGGREGATOR_DIR = 'aggregator'
NO_ROUNDS = 10

class Verdict(Enum):
    POSITIVE = 1
    NEGATIVE = 2
    def __init__(self, code):
        self.code = code


class File_Type(Enum):
    Dataset = (1, 'Dataset')
    FootprintModel = (2, 'Footprint') 
    ClusterStructure = (3, 'Cluster Structure')
    ClusterAggregationModel = (4, 'Aggregated Model')
    CandidateModel = (5, 'Candidate')

    def __init__(self, code, file_name):
        self.code = code
        self.file_name = file_name