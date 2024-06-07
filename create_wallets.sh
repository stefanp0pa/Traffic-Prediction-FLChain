#!/bin/bash

# Constants
NO_NODES=170
NO_CLUSTERS=25
PROJECT_PATH="/home/robert/Desktop/Facultate/Licenta/Traffic-Prediction-FLChain/flchain-official/wallets"

WALLET_DIR_ADDRESS_FILE="wallets_addr"

WALLETS_DIR_TRAINERS="trainers"
WALLETS_DIR_EVALUATOR_TRAINERS="evaluator_trainers"
WALLETS_DIR_CLUSTERS_AGGREGATOR="aggregator"
WALLETS_DIR_EVALUATOR_CLUSTERS="evaluator_clusters"

WALLETS_COUNT_TRAINERS=$NO_NODES
WALLETS_COUNT_EVALUATOR_TRAINERS=$NO_NODES
WALLETS_COUNT_CLUSTERS_AGGREGATOR=$NO_CLUSTERS
WALLETS_COUNT_EVALUATOR_CLUSTERS=$NO_CLUSTERS

# Function to generate wallets
generate_wallets() {
    local wallets_dir="$1"
    local count=$2

    echo "Generating ${count} wallets in '${wallets_dir}' directory..."
    mkdir "${PROJECT_PATH}/${wallets_dir}"

    for ((i = 1; i <= count; i++)); do
        mxpy wallet new --format pem --outfile "${PROJECT_PATH}/${wallets_dir}/${i}.pem"
        sed -n '1s/^.* \(erd[^-]*\).*$/\1/p' "${PROJECT_PATH}/${wallets_dir}/${i}.pem" >> "${PROJECT_PATH}/${WALLET_DIR_ADDRESS_FILE}/${wallets_dir}"
    done
}

# Generate wallets

mkdir "${PROJECT_PATH}"
mkdir "${PROJECT_PATH}/${WALLET_DIR_ADDRESS_FILE}"

generate_wallets "$WALLETS_DIR_TRAINERS" $WALLETS_COUNT_TRAINERS
generate_wallets "$WALLETS_DIR_EVALUATOR_TRAINERS" $WALLETS_COUNT_EVALUATOR_TRAINERS
generate_wallets "$WALLETS_DIR_CLUSTERS_AGGREGATOR" $WALLETS_COUNT_CLUSTERS_AGGREGATOR
generate_wallets "$WALLETS_DIR_EVALUATOR_CLUSTERS" $WALLETS_COUNT_EVALUATOR_CLUSTERS

echo "All wallets generated successfully."
