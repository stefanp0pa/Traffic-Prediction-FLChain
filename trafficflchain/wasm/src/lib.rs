// Code generated by the multiversx-sc build system. DO NOT EDIT.

////////////////////////////////////////////////////
////////////////// AUTO-GENERATED //////////////////
////////////////////////////////////////////////////

// Init:                                 1
// Endpoints:                            5
// Async Callback (empty):               1
// Total number of exported functions:   7

#![no_std]
#![allow(internal_features)]
#![feature(lang_items)]

multiversx_sc_wasm_adapter::allocator!();
multiversx_sc_wasm_adapter::panic_handler!();

multiversx_sc_wasm_adapter::endpoints! {
    trafficflchain
    (
        init => init
        upgrade => upgrade
        setup_network => setup_network
        get_network_storage_addr => get_network_storage_addr
        publish_data_batch => publish_data_batch
        getGraphNetwork => graph_networks
    )
}

multiversx_sc_wasm_adapter::async_callback_empty! {}
