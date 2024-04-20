#!/bin/bash

echo "Checking dependencies..."
command -v jq || { echo "jq not found. Installing jq using Homebrew..."; brew install jq; }

CONTRACT_ADDR="erd1qqqqqqqqqqqqqpgq5fqj294099nurngdz9rzgv7du0n6h4vedttshsdl08"

source "/Users/stefan/ssi-proiect/contracts/flchain_dummy/commands/devnet.snippets.sh"

set_contract ${CONTRACT_ADDR}

assess_condition() {
    [ "$1" == true ]
}

should_block_timestamp_increment() {
    first_timestamp=$(query_contract_block_timestamp | jq -r '.[0].number')
    sleep 6
    second_timestamp=$(query_contract_block_timestamp | jq -r '.[0].number')

    if [ "$second_timestamp" -gt "$first_timestamp" ]; then
        return 0
    else
        return 1
    fi
}

should_be_active_session_1() {
    error_message=$(query_get_active_session 2>&1 | tail -n 1)
    query_failed_part=$(echo "$error_message" | grep -o "Query failed:.*$")
    [ "$query_failed_part" == "Query failed: No training session available!" ]
}

should_be_signup_open_1() {
    error_message=$(query_is_signup_open 2>&1 | tail -n 1)
    query_failed_part=$(echo "$error_message" | grep -o "Query failed:.*$")
    [ "$query_failed_part" == "Query failed: No training session available!" ]
}

should_be_signup_open_2() {
    ipfs_addr=0x516d536d3169746375414e6969335337454e65766273737635656f774c716a753862315665384333567435314637
    call_start_session $ipfs_addr 0x06 0x05 0x02 > /dev/null 2>&1
    sleep 6
    is_signup_open=$(query_is_signup_open | jq -r '.[0].number')
    call_end_session > /dev/null 2>&1
    [ "$is_signup_open" == "1" ]
}

should_not_be_training_open_1() {
    error_message=$(query_is_training_open 2>&1 | tail -n 1)
    query_failed_part=$(echo "$error_message" | grep -o "Query failed:.*$")
    [ "$query_failed_part" == "Query failed: No training session available!" ]
}

should_be_training_open() {
    ipfs_addr=0x516d536d3169746375414e6969335337454e4e65766273737635656f774c716a753862315665384333567435314637
    call_start_session $ipfs_addr 0x01 0x08 0x01 > /dev/null 2>&1
    sleep 18
    is_training_open=$(query_is_training_open | jq -r '.[0].number')
    call_end_session > /dev/null 2>&1
    [ "$is_training_open" == "1" ]
}

should_be_aggregation_open_1() {
    error_message=$(query_is_aggregation_open 2>&1 | tail -n 1)
    query_failed_part=$(echo "$error_message" | grep -o "Query failed:.*$")
    [ "$query_failed_part" == "Query failed: No training session available!" ]
}

should_initiator_exist_1() {
    error_message=$(query_get_initiator 2>&1 | tail -n 1)
    query_failed_part=$(echo "$error_message" | grep -o "Query failed:.*$")
    [ "$query_failed_part" == "Query failed: No training session available!" ]
}

should_initiator_exist_2() {
    ipfs_addr=0x516d536d3169746375414e6969335337454e65766273737635656f774c716a753862315665384333567435314637
    call_start_session $ipfs_addr 0x06 0x05 0x02 > /dev/null 2>&1
    sleep 6
    hexed_addr=$(query_get_initiator | jq -r '.[0].hex')
    call_end_session > /dev/null 2>&1
    [ "$hexed_addr" == "ba057949d5f55f498452b9da3316e6ac32bfcca1bf3c53ceee62d13153fb6ad7" ]
}

should_block_timestamp_increment && echo "[✅] Test: should_block_timestamp_increment" || echo "[❌] Test: should_block_timestamp_increment"
sleep 6
should_be_active_session_1 && echo "[✅] Test: should_be_active_session_1" || echo "[❌] Test: should_be_active_session_1"
sleep 6
should_be_signup_open_1 && echo "[✅] Test: should_be_signup_open_1" || echo "[❌] Test: should_be_signup_open_1"
sleep 6
# should_be_signup_open_2 && echo "[✅] Test: should_be_signup_open_2" || echo "[❌] Test: should_be_signup_open_2"
# sleep 6
# should_not_be_training_open_1 && echo "[✅] Test: should_not_be_training_open_1" || echo "[❌] Test: should_not_be_training_open_1"
# sleep 6
# should_be_training_open && echo "[✅] Test: should_be_training_open" || echo "[❌] Test: should_be_training_open"
# sleep 6
# should_be_aggregation_open_1 && echo "[✅] Test: should_be_aggregation_open_1" || echo "[❌] Test: should_be_aggregation_open_1"
# sleep 6
# should_initiator_exist_1 && echo "[✅] Test: should_initiator_exist_1" || echo "[❌] Test: should_initiator_exist_1"
# sleep 6
# should_initiator_exist_2 && echo "[✅] Test: should_initiator_exist_2" || echo "[❌] Test: should_initiator_exist_2"
