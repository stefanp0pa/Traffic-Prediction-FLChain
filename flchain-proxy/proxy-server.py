from flask import Flask

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

from abc import ABC, abstractmethod

import base64

SC_ADDR = "erd1qqqqqqqqqqqqqpgq3fx434vuswz3qsf54kg8w0uxqzqx5dvfch8qcf53r6"
WALLET_PATH = "/home/robert/Desktop/Facultate/Licenta//Traffic-Prediction-FLChain/wallets/master.pem" # replace with your own wallet
CHAIN_ID = "D" # D - devent, T - testnet
NETWORK_PROVIDER = "https://devnet-api.multiversx.com" if CHAIN_ID == "D" else "https://testnet-api.multiversx.com"
GAS_LIMIT = 60000000
PORT = 5678

app = Flask(__name__)

class BlockchainBaseApi(ABC):
    @abstractmethod
    def get_serialized_graph(self, graph_id: str) -> str:
        pass
    
    

class BlockchainApi(BlockchainBaseApi):
    def __init__(self, sc_addr: str, user_addr: str, wallet_path: str, chain_id: str, network_provider: str, gas_limit: int):
        self.sc_addr = sc_addr
        self.wallet_path = wallet_path
        self.chain_id = chain_id
        self.network_provider = network_provider
        self.gas_limit = gas_limit
        self.config = TransactionsFactoryConfig(chain_id)
        self.transaction_computer = TransactionComputer()
        self.sc_factory = SmartContractTransactionsFactory(self.config, TokenComputer())
        self.contract_address = Address.from_bech32(sc_addr)
        self.user_addr = Address.from_bech32(user_addr)
        self.signer = UserSigner.from_pem_file(Path(self.wallet_path))
        self.network_provider = ApiNetworkProvider(network_provider)
        self.nonce_holder = AccountNonceHolder(self.network_provider.get_account(self.user_addr).nonce)

    def get_serialized_graph(self, graph_id: int) -> str:
        builder = ContractQueryBuilder(
            contract = self.contract_address,
            function = "get_serialized_network_data",
            call_arguments = [graph_id],
            caller = self.user_addr
        )
        query = builder.build()
        response = self.network_provider.query_contract(query).to_dictionary()
        print(response)
        return "aaa" 

@app.route('/get-serialized-graph')
def get_serialized_graph():
    blApi = BlockchainApi(SC_ADDR, "erd1rxufcd8sn9t2k5cavngu60qeeytkuxymajdarnyq5f8enh850wpq8at8xu", WALLET_PATH, CHAIN_ID, NETWORK_PROVIDER, GAS_LIMIT)
    graph_id = 1
    serialized_graph = blApi.get_serialized_graph(graph_id)
    return serialized_graph

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True, port=PORT)