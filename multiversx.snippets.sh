GAS_LIMIT=60000000
PROXY="https://devnet-gateway.multiversx.com" # "https://testnet-gateway.multiversx.com" for the testnet
CHAIN_ID="D" # T for testnet

PROJECT_PATH="/Users/stefan/Traffic-Prediction-FLChain" # replace with your project path
WALLETS_DIR="wallets"
MASTER_WALLET="$PROJECT_PATH/wallets/master.pem"
DWARF_WALLET="$PROJECT_PATH/wallets/dwarf.pem"

MASTER_ADDR="erd1dwlm0pazs43q0sad8h3r7ueehlzjmhyyq9spryaxruhvfgwych8qgydtwz"
DWARF_ADDR="erd12zjr9k2wae68are9rmz7z6hphyestwgf6m6utuqdndgchc3vyvvs0g3zlg"

create_wallet() {
    mxpy wallet new --format pem --outfile "${PROJECT_PATH}/${WALLETS_DIR}/${1}.pem"
}

parse_wallet_addr() {
    sed -n '1s/^.* \(erd[^-]*\).*$/\1/p' "${PROJECT_PATH}/${WALLETS_DIR}/${1}.pem"
}

# 0.1 EGLD = 100000000000000000
send_egld() {
    mxpy --verbose tx new --recall-nonce \
        --receiver=${1} \
        --pem=${MASTER_WALLET} \
        --gas-limit=${GAS_LIMIT} \
        --proxy=${PROXY} --chain=${CHAIN_ID} \
        --value 100000000000000000 \
        --send
}

seed_account() {
    create_wallet $1
    new_addr=$(parse_wallet_addr $1)
    echo $1=$new_addr >> "${PROJECT_PATH}/${WALLETS_DIR}/addresses.txt"
    send_egld $new_addr
}
