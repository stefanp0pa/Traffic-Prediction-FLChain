#!/bin/bash

# Constants
NO_NODES=170
NO_CLUSTERS=22
PROJECT_PATH="/Users/stefan/Traffic-Prediction-FLChain/flchain-official/wallets"
WALLET_DIR_ADDRESS_FILE="wallets_addr"

GAS_LIMIT=100000000
PROXY="https://devnet-gateway.multiversx.com" # "https://testnet-gateway.multiversx.com" for the testnet
CHAIN_ID="D" # T for testnet

PATRON_ADDR="erd1dwlm0pazs43q0sad8h3r7ueehlzjmhyyq9spryaxruhvfgwych8qgydtwz"
PATRONAGE_SUM=500000000000000000 # 0.5 xEGLD
PATRON_WALLET="/Users/stefan/Traffic-Prediction-FLChain/wallets/master.pem" #

WALLETS_DIR_TRAINERS="trainers"
WALLETS_DIR_EVALUATORS="evaluators"
WALLETS_DIR_CLUSTERS_AGGREGATOR="aggregators"

WALLETS_COUNT_TRAINERS=$NO_NODES
WALLETS_COUNT_EVALUATORS=$NO_CLUSTERS
WALLETS_COUNT_CLUSTERS_AGGREGATOR=$NO_CLUSTERS

# Function to generate wallets
generate_wallets() {
    local wallets_dir="$1"
    local count=$2

    WALLETS_CATEGORY_DIR="${PROJECT_PATH}/${wallets_dir}"
    WALLETS_CATEGORY_ADDR_FILE="${PROJECT_PATH}/${wallets_dir}_addresses.txt"

    echo "Generating ${count} wallets in '${wallets_dir}' directory..."
    mkdir "${WALLETS_CATEGORY_DIR}"
    touch "${WALLETS_CATEGORY_ADDR_FILE}"

    for ((i = 1; i <= count; i++)); do
        WALLET_PATH="${WALLETS_CATEGORY_DIR}/${i}.pem"
        mxpy wallet new --format pem --outfile "${WALLET_PATH}"
        WALLET_ADDR=$(sed -n '1s/^.* \(erd[^-]*\).*$/\1/p' "${WALLET_PATH}")
        echo ${WALLET_ADDR} >> "${WALLETS_CATEGORY_ADDR_FILE}"
    done
}

# Generate wallets

mkdir "${PROJECT_PATH}"
# mkdir "${PROJECT_PATH}/${WALLET_DIR_ADDRESS_FILE}"

generate_wallets "$WALLETS_DIR_TRAINERS" $WALLETS_COUNT_TRAINERS
generate_wallets "$WALLETS_DIR_EVALUATORS" $WALLETS_COUNT_EVALUATORS
generate_wallets "$WALLETS_DIR_CLUSTERS_AGGREGATOR" $WALLETS_COUNT_CLUSTERS_AGGREGATOR

echo "All wallets generated successfully."
