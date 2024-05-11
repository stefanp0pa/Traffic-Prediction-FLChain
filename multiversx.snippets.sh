GAS_LIMIT=60000000
PROXY="https://devnet-gateway.multiversx.com" # "https://testnet-gateway.multiversx.com" for the testnet
CHAIN_ID="D" # T for testnet

PROJECT_PATH="/Users/stefan/Traffic-Prediction-FLChain" # replace with your project path
WALLETS_DIR="wallets"
MASTER_WALLET="$PROJECT_PATH/wallets/master.pem"
DWARF_WALLET="$PROJECT_PATH/wallets/dwarf.pem"

SC_ADDR="erd1qqqqqqqqqqqqqpgqz82nup6jgsxhf0xzx6yyg4xm2tcqsd27ch8quuq97s"

BYTECODE="$PROJECT_PATH/trafficflchain/output/trafficflchain.wasm"

MASTER_ADDR="erd1dwlm0pazs43q0sad8h3r7ueehlzjmhyyq9spryaxruhvfgwych8qgydtwz"
DWARF_ADDR="erd12zjr9k2wae68are9rmz7z6hphyestwgf6m6utuqdndgchc3vyvvs0g3zlg"

build_contract() {
    mxpy contract build
}

deploy_contract() {
    mxpy --verbose contract deploy --recall-nonce \
        --bytecode=${BYTECODE} \
        --pem=${MASTER_WALLET} \
        --gas-limit=${GAS_LIMIT} \
        --proxy=${PROXY} --chain=${CHAIN_ID} \
        --outfile="deploy-devnet.interaction.json" --send || return

    TRANSACTION=$(mxpy data parse --file="deploy-devnet.interaction.json" --expression="data['emittedTransactionHash']")
    SC_ADDR=$(mxpy data parse --file="deploy-devnet.interaction.json" --expression="data['contractAddress']")

    mxpy data store --key=address-devnet --value=${SC_ADDR}
    mxpy data store --key=deployTransaction-devnet --value=${TRANSACTION}

    echo ""
    echo "Smart contract address: ${SC_ADDR}"
}

upgrade_contract() {
    mxpy --verbose contract upgrade ${SC_ADDR} --recall-nonce \
        --bytecode=${BYTECODE} \
        --pem=${MASTER_WALLET} \
        --gas-limit=${GAS_LIMIT} \
        --proxy=${PROXY} --chain=${CHAIN_ID} \
        --send || return
}

# storage_addr = yzfres09zw
# hash = 6beflgj9go2g5xhak2c1h6b22bbcgd7k
# setup_network "0x01" "0x06" "0x08" "0x797a6672657330397a77" "0x366265666c676a39676f3267357868616b32633168366232326262636764376b"

setup_network() {
    mxpy contract call ${SC_ADDR} --recall-nonce \
        --pem=${MASTER_WALLET} \
        --gas-limit=${GAS_LIMIT} \
        --proxy=${PROXY} --chain=${CHAIN_ID} \
        --function="setup_network" \
        --arguments $1 $2 $3 $4 $5 \
        --send
}

clear_network() {
    mxpy contract call ${SC_ADDR} --recall-nonce \
        --pem=${MASTER_WALLET} \
        --gas-limit=${GAS_LIMIT} \
        --proxy=${PROXY} --chain=${CHAIN_ID} \
        --function="clear_network" \
        --arguments $1 \
        --send
}

view_graph_network() {
    mxpy contract query ${SC_ADDR} \
        --proxy=${PROXY}\
        --function getGraphNetwork \
        --arguments $1
}

view_local_updates() {
    mxpy contract query ${SC_ADDR} \
        --proxy=${PROXY}\
        --function get_local_updates
}

get_serialized_network_data() {
    mxpy contract query ${SC_ADDR} \
        --proxy=${PROXY}\
        --function "get_serialized_network_data" \
        --arguments $1

}


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
