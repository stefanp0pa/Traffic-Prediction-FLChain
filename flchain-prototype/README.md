## Description

Simple FLChain project using MultiversX and IPFS. The project is inspired by the following paper: https://arxiv.org/abs/2306.10841.

The code for the smart contract is in the `contracts` folder, and an already available smart contract is deployed [here](https://devnet-explorer.multiversx.com/accounts/erd1qqqqqqqqqqqqqpgq5fqj294099nurngdz9rzgv7du0n6h4vedttshsdl08). For interacting with the smart contract, please navigate to `contracts/flchain_dummy/commands` and run `source devnet.snippets.sh`. Make sure to have [mxpy](https://docs.multiversx.com/sdk-and-tools/sdk-py/mxpy-cli/) installed. This project uses IPFS, so make sure to have a local node running following the [install docs](https://docs.ipfs.tech/install/).

## How to run
* You will need to set up 3 RabbitMQ instances at [https://beaconx.app/](https://beaconx.app/) and get the credentials for each of them. For each of the participant folder, you will need to set up an `.env` file with the given credentials.
* Navigate to `participants/` folder and set up a virtual environment with `python3 -m venv venv`. After that, activate it with `source venv/bin/activate`. There are some MultiversX packages that need to be installed, so run `pip install -r requirements.txt`.
* In a terminal, run:
  - `pip install -r requirements.txt` to install the MultiversX packages
  - `pip install tensorflow` to install the TensorFlow package
* Open 4 terminals for each of the participants:
  - Run `python3 evaluator/evaluator.py` 
  - Run `python3 aggregator/aggregator.py`
  - Run `python3 trainer/trainer.py 1`
  - Make sure that each of these processes is connected to RabbitMQ. If not, please restart
  - Run `python3 initiator/initiator.py`
* Navigate to the smart contract address from above and watch the interactions
  