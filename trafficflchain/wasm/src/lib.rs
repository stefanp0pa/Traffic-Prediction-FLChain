// Code generated by the multiversx-sc build system. DO NOT EDIT.

////////////////////////////////////////////////////
////////////////// AUTO-GENERATED //////////////////
////////////////////////////////////////////////////

// Init:                                 1
// Endpoints:                           39
// Async Callback (empty):               1
// Total number of exported functions:  41

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
        upload_dataset_file => upload_dataset_file
        upload_cluster_model_file => upload_cluster_model_file
        upload_cluster_aggregation => upload_cluster_aggregation
        upload_adj_matrix_file => upload_adj_matrix_file
        clear_dataset_file => clear_dataset_file
        clear_cluster_aggregation => clear_cluster_aggregation
        clear_cluster_model_file => clear_cluster_model_file
        clear_adj_matrix_file => clear_adj_matrix_file
        upload_cluster_description => upload_cluster_description
        clear_cluster_description => clear_cluster_description
        get_all_round_files => get_all_round_files
        get_all_clusters_per_node => get_all_clusters_per_node
        get_training_data => get_training_data
        evaluate_file => evaluate_file
        get_file_evaluations => get_file_evaluations
        signup_user => signup_user
        clear_user => clear_user
        get_aggregated_models => get_aggregated_models
        get_users_by_role => get_users_by_role
        update_reputation => update_reputation
        next_round => next_round
        set_round => set_round
        set_stage => set_stage
        get_node_dataset => node_datasets
        get_cluster_adjacency_matrix => cluster_adj_matrices
        get_cluster_aggregation => cluster_aggregation
        get_user => users
        get_file => files
        get_stake => stakes
        get_reputation => reputations
        get_file_author => file_authors
        get_files_count => files_count
        get_users_count => users_count
        get_nodes_count => nodes_count
        get_clusters_count => clusters_count
        get_round => round
        get_stage => stage
        test_event => test_event
    )
}

multiversx_sc_wasm_adapter::async_callback_empty! {}
