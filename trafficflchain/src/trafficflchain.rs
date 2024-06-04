#![no_std]

multiversx_sc::imports!();
multiversx_sc::derive_imports!();

mod role;
mod filetype;
mod evaluation_status;
mod stage;

use role::Role;
use filetype::FileType;
use evaluation_status::EvaluationStatus;
use stage::Stage;

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi, Clone)]
pub struct GraphTopology<M: ManagedTypeApi> {
    pub vertices_count: u64,
    pub edges_count: u64,
    pub owner: ManagedAddress<M>,
    pub storage_addr: [u8; 46], // IPFS hash CDv1
    pub timestamp: u64,
    pub hash: [u8; 32],
}

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi, Clone, ManagedVecItem)]
pub struct ClusterNode {
    global_node_index: u16,
    local_node_index: u16,
}

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi, Clone, ManagedVecItem)]
pub struct TrainingData {
    cluster_adj_matrix_addr: [u8; 46],
    dataset_addr: [u8; 46],
    aggr_cluster_model_addr : [u8; 46],
    footprind_model_addr: [u8; 46],
    local_node_index: u16
}

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi, Clone)]
pub struct User<M: ManagedTypeApi> {
    role: Role,
    addr: ManagedAddress<M>,
}

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi, Clone, ManagedVecItem)]
pub struct File {
    file_location: [u8; 46], // IPFS hash CDv1
    file_type: FileType,
    round: usize
}

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi, Clone, ManagedVecItem)]
pub struct Evaluation<M: ManagedTypeApi> {
    evaluator: ManagedAddress<M>,
    status: EvaluationStatus,
}

#[multiversx_sc::contract]
pub trait Trafficflchain {
    #[init]
    fn init(&self, nodes_count: u16, clusters_count: u16) {
        self.round().set(0);
        self.stage().set(Stage::Undefined);
        self.files_count().set(0);
        self.users_count().set(0);
        self.nodes_count().set(nodes_count);
        self.clusters_count().set(clusters_count);
    }

    #[upgrade]
    fn upgrade(&self) {}

    // Data ------------------------------------------------------------------
    fn upload_file(&self, file_location: [u8; 46], file_type: FileType, author_addr: ManagedAddress) {
        if self.file_locations().contains(&file_location) {
            sc_panic!("File already exists!");
        }
        else {
            let round = self.round().get();
            let file = File { file_location, file_type, round };
            self.files(file_location.clone()).set(file);
            self.file_locations().insert(file_location.clone());
            self.author_files(author_addr.clone()).insert(file_location.clone());
            self.file_authors(file_location.clone()).set(author_addr.clone());
            self.round_files(round).insert(file_location.clone());
            self.files_count().update(|count| { *count += 1 });
            self.upload_file_event(file_location, file_type, round, author_addr);
        }
    }

    fn clear_file(&self, file_location: [u8; 46]) {
        if !self.file_locations().contains(&file_location) {
            sc_panic!("File does not exist!");
        }
        else {
            let file_author = self.file_authors(file_location.clone()).get();
            let round = self.files(file_location.clone()).get().round;
            let file = self.files(file_location.clone()).get();
            self.files(file_location.clone()).clear();
            self.file_locations().swap_remove(&file_location.clone());
            self.author_files(file_author.clone()).swap_remove(&file_location.clone());
            self.file_authors(file_location.clone()).clear();
            self.round_files(round).swap_remove(&file_location.clone());
            self.file_evaluations(file_location.clone()).clear();
            self.files_count().update(|count| { *count -= 1 });
            self.clear_file_event(file_location, file.file_type, round, file_author);
        }
    }


    // The dataset file for each node, we only store the IPFS address and it is the consumer's responsibility to fetch it
    #[endpoint]
    fn upload_dataset_file(&self, file_location: [u8; 46], global_node_index: u16, cluster_index: u16) {
        let author_addr = self.blockchain().get_caller();
        self.upload_file(file_location, FileType::Dataset, author_addr);
        self.node_datasets(global_node_index, cluster_index).set(file_location.clone());
    }

    // This method should be used in-between the Training and Aggregation stages
    // The trainer uploads the model file for a specific cluster and awaits evaluation
    // Later, based on the evaluation score, the model may be considered in the Aggregation stage
    #[endpoint]
    fn upload_candidate_model_file(&self, file_location: [u8; 46], cluster_index: u16) {
        let author_addr = self.blockchain().get_caller();
        let round = self.round().get();
        self.upload_file(file_location, FileType::CandidateModel, author_addr);
        self.candidate_models(cluster_index, round).insert(file_location);
    }

    // This method should be used in the Seeding stage and at the end of each Training stage
    #[endpoint]
    fn upload_footprint_model_file(&self, file_location: [u8; 46], global_node_index: u16, cluster_index: u16) {
        let author_addr = self.blockchain().get_caller();
        let round = self.round().get();
        self.upload_file(file_location, FileType::FootprintModel, author_addr);
        self.footprint_models(global_node_index, cluster_index, round).set(file_location);
    }

    // This method should be used following the Aggregation stage or right at the Seeding stage
    // The aggregation file represents the new cluster model following a full training round
    #[endpoint]
    fn upload_cluster_aggregation_file(&self, file_location: [u8; 46], cluster_index: u16) {
        let author_addr = self.blockchain().get_caller();
        let round = self.round().get();
        self.upload_file(file_location, FileType::ClusterAggregationModel, author_addr);
        self.aggregation_models(cluster_index, round).set(file_location);
    }

    // This method should be used in the Seeding stage when seeding the cluster structure
    #[endpoint]
    fn upload_adj_matrix_file(&self, file_location: [u8; 46], cluster_index: u16) {
        let author_addr = self.blockchain().get_caller();
        self.upload_file(file_location, FileType::ClusterStructure, author_addr);
        self.cluster_adj_matrices(cluster_index).set(file_location);
    }

    #[endpoint]
    fn clear_dataset_file(&self, file_location: [u8; 46], global_node_index: u16, cluster_index: u16) {
        self.clear_file(file_location);
        self.node_datasets(global_node_index, cluster_index).clear();
    }

    #[endpoint]
    fn clear_cluster_aggregation_file(&self, file_location: [u8; 46], cluster_index: u16, round: usize) {
        self.clear_file(file_location);
        self.aggregation_models(cluster_index, round).clear();
    }

    #[endpoint]
    fn clear_footprint_model_file(&self, file_location: [u8; 46], global_node_index: u16, cluster_index: u16, round: usize) {
        self.clear_file(file_location);
        self.footprint_models(global_node_index, cluster_index, round).clear();
    }

    #[endpoint]
    fn clear_candidate_model_file(&self, file_location: [u8; 46], cluster_index: u16, round: usize) {
        self.clear_file(file_location);
        self.candidate_models(cluster_index, round).swap_remove(&file_location);
    }
    
    #[endpoint]
    fn clear_adj_matrix_file(&self, file_location: [u8; 46], cluster_index: u16) {
        self.clear_file(file_location);
        self.cluster_adj_matrices(cluster_index).clear();
    }



    // Cluster nodes description =============================================
    // There is a many-to-many relationship between clusters and nodes
    // A node can belong to multiple clusters
    // A cluster can encompass multiple nodes
    // We hold 2 storage mappers to encapsulate this relationship (cluster_nodes, node_clusters)
    #[endpoint]
    fn upload_cluster_description(&self, cluster_index: u16, global_node_index: u16, local_node_index: u16) {
        let cluster_node = ClusterNode {
            global_node_index: global_node_index,
            local_node_index: local_node_index
        };
        self.cluster_nodes(cluster_index).insert(cluster_node);
        self.node_clusters(global_node_index).insert(cluster_index);
    }

    #[endpoint]
    fn clear_cluster_description(&self, cluster_index: u16, global_node_index: u16) {
        let cluster_node = self.cluster_nodes(cluster_index)
            .iter().find(|cn| cn.global_node_index == global_node_index).unwrap();
        self.cluster_nodes(cluster_index).swap_remove(&cluster_node);
        
        let node_cluster = self.node_clusters(global_node_index)
            .iter().find(|cn| cn == &cluster_index).unwrap();
        self.node_clusters(global_node_index).swap_remove(&node_cluster);
    }

    // Given a node X, we want to know all the clusters it belongs to
    #[view]
    fn get_all_clusters_per_node(&self, node_global_index: u16) -> ManagedVec<u16> {
        let mut output: ManagedVec<u16> = ManagedVec::new();
        for cluster_index in self.node_clusters(node_global_index).iter() {
            output.push(cluster_index);
        }
        output
    }

    // Given a cluster Y, we want to know all the nodes it encompasses
    #[view]
    fn get_all_nodes_per_cluster(&self, cluster_index: u16) -> ManagedVec<ClusterNode> {
        let mut output: ManagedVec<ClusterNode> = ManagedVec::new();
        for cluster_node in self.cluster_nodes(cluster_index).iter() {
            output.push(cluster_node);
        }
        output
    }


    // Given a round, we want to know all the files that were uploaded in that round
    #[view]
    fn get_all_round_files(&self, round: usize) -> ManagedVec<File> {
        let mut output: ManagedVec<File> = ManagedVec::new();
        for file in self.round_files(round).iter() {
            output.push(self.files(file.clone()).get());
        }
        output
    }


    // Gets the necessary data that a trainer requires to train a model
    // Given a node X and a cluster Y as parameters, we want to know the following:
    // - The adjacency matrix of the cluster Y
    // - The dataset of the node X and cluster Y
    // - The aggregated model of the cluster Y from the previous round (this is the baseline model for the new round)
    // - The local index of the node X in the cluster Y
    #[view]
    fn get_training_data(&self, global_node_index: u16, cluster_index: u16) -> TrainingData {
        let adj_matrix = self.cluster_adj_matrices(cluster_index).get();
        if self.cluster_adj_matrices(cluster_index).is_empty() {
            sc_panic!("Cluster adjacency matrix does not exist!");
        }
        let data_addr = self.node_datasets(global_node_index, cluster_index).get();
        if self.node_datasets(global_node_index, cluster_index).is_empty() {
            sc_panic!("Dataset does not exist!");
        }
        let prev_round = self.round().get() - 1;
        let prev_aggr_model = self.aggregation_models(cluster_index, prev_round).get();
        if self.aggregation_models(cluster_index, prev_round).is_empty() {
            sc_panic!("No previous aggregated model to use!");
        }

        let footprint_model_addr = self.footprint_models(global_node_index, cluster_index, prev_round).get();

        let local_node_index = self.cluster_nodes(cluster_index)
            .iter().find(|cn| cn.global_node_index == global_node_index).unwrap().local_node_index;
        if self.cluster_nodes(cluster_index).is_empty() {
            sc_panic!("Node does not belong to any cluster!");
        }

        TrainingData {
            cluster_adj_matrix_addr: adj_matrix,
            dataset_addr: data_addr,
            aggr_cluster_model_addr: prev_aggr_model,
            footprind_model_addr: footprint_model_addr,
            local_node_index
        }
    }


    // Evaluation ------------------------------------------------------------
    #[endpoint]
    fn evaluate_file(&self, file_location: [u8; 46], status: EvaluationStatus) {
        let caller = self.blockchain().get_caller();
        if self.files(file_location.clone()).is_empty() {
            sc_panic!("File does not exist!");
        }
        else {
            self.file_evaluations(file_location.clone()).insert(Evaluation { evaluator: caller.clone(), status });
            self.evaluate_file_event(file_location, status, caller);
        }
    }

    #[view]
    fn get_file_evaluations(&self, file_location: [u8; 46]) -> ManagedVec<Evaluation<Self::Api>> {
        let mut output: ManagedVec<Evaluation<Self::Api>> = ManagedVec::new();
        for evaluation in self.file_evaluations(file_location.clone()).iter() {
            output.push(evaluation);
        }
        output
    }


    // Users -----------------------------------------------------------------
    #[endpoint]
    #[payable("*")]
    fn signup_user(&self) {
        let caller = self.blockchain().get_caller();
        let already_signed_up = self.users(caller.clone()).is_empty();
        if !already_signed_up {
            sc_panic!("Already signed up!");
        }
        else {
            let staked_amount = self.call_value().egld_value().clone_value();
            let user_role = Role::Undefined;
            let user = User {
                addr: caller.clone(),
                role: user_role
            };

            self.users(caller.clone()).set(user);
            self.user_addresses().insert(caller.clone());
            self.stakes(caller.clone()).set(staked_amount.clone());
            self.reputations(caller.clone()).set(0);
            self.users_count().update(|count| { *count += 1 });
            self.signup_user_event(caller, staked_amount.clone(), user_role);
        }
    }

    #[endpoint]
    fn clear_user(&self) {
        let caller: ManagedAddress = self.blockchain().get_caller();
        let invalid_user = self.users(caller.clone()).is_empty();
        if invalid_user {
            sc_panic!("User does not exist!");
        }
        else {
            self.send().direct_egld(&caller, &self.stakes(caller.clone()).get());
            self.stakes(caller.clone()).clear();
            self.users(caller.clone()).clear();
            self.user_addresses().swap_remove(&caller.clone());
            self.reputations(caller.clone()).clear();
            self.users_count().update(|count| { *count -= 1 });
            self.user_cleared_event(caller.clone());
        }
    }


 

    
    // This method should be used at the Aggregation stage, to get all the candidate models for the aggregation
    #[view]
    fn get_cluster_models_for_aggregation(&self, cluster_index: u16, round_index: usize) -> ManagedVec<[u8; 46]> {
        let mut output: ManagedVec<[u8; 46]> = ManagedVec::new();
        for model in self.candidate_models(cluster_index, round_index).iter() {
            output.push(model);
        }
        output
    }

    #[view]
    fn get_users_by_role(&self, role: Role) -> ManagedVec<ManagedAddress> {
        let mut output: ManagedVec<ManagedAddress> = ManagedVec::new();
        for user in self.user_addresses().iter() {
            if self.users(user.clone()).get().role == role {
                output.push(user);
            }
        }
        output
    }

    #[endpoint]
    fn update_reputation(&self, user_addr: ManagedAddress, reputation: usize) {
        require!(
            !self.users(user_addr.clone()).is_empty(),
            "User does not exist!"
        );

        self.reputations(user_addr.clone()).set(reputation);
        self.reputation_updated_event(user_addr, reputation);
    }

    // Rounds ----------------------------------------------------------------
    #[endpoint]
    fn next_round(&self) {
        self.round().update(|round| { *round += 1 });
        self.set_round_event(self.round().get());
    }

    #[endpoint]
    fn set_round(&self, round: usize) {
        self.round().set(round);
        self.set_round_event(round);
    }

    // Stages ----------------------------------------------------------------
    #[endpoint]
    fn set_stage(&self, stage: Stage) {
        self.stage().set(stage);
        self.set_stage_event(stage);
    }

    // Storage mappers -------------------------------------------------------

    // the IPFS address of the dataset for each node
    #[view(get_node_dataset)]
    #[storage_mapper("node_datasets")]
    fn node_datasets(&self, global_node_index: u16, cluster_index: u16) -> SingleValueMapper<[u8; 46]>;

    // The IPFS address of the cluster adjacency matrix
    #[view(get_cluster_adjacency_matrix)]
    #[storage_mapper("cluster_adjacency_matrices")]
    fn cluster_adj_matrices(&self, cluster_index: u16) -> SingleValueMapper<[u8; 46]>;

    #[storage_mapper("cluster_nodes")]
    fn cluster_nodes(&self, cluster_index: u16) -> UnorderedSetMapper<ClusterNode>;

    #[storage_mapper("node_clusters")]
    fn node_clusters(&self, global_node_index: u16) -> UnorderedSetMapper<u16>;

    // The IPFS address of the cluster aggregation model at each round
    #[view(get_cluster_aggregation_model)]
    #[storage_mapper("aggregation_models")]
    fn aggregation_models(&self, cluster_index: u16, round: usize) -> SingleValueMapper<[u8; 46]>;

    // The IPFS address of the candidate model for each (node, cluster, round) tuple
    #[view(get_candidate_model)]
    #[storage_mapper("candidate_models")]
    fn candidate_models(&self, cluster_index: u16, round: usize) -> UnorderedSetMapper<[u8; 46]>;

    // The IPFS address of the footprint model for each (node, round) tuple
    #[view(get_footprint_model)]
    #[storage_mapper("footprint_models")]
    fn footprint_models(&self, global_node_index: u16, cluster_index: u16, round: usize) -> SingleValueMapper<[u8; 46]>;

    #[view(get_user)]
    #[storage_mapper("users")]
    fn users(&self, user_addr: ManagedAddress) -> SingleValueMapper<User<Self::Api>>;

    #[storage_mapper("user_addresses")]
    fn user_addresses(&self) -> UnorderedSetMapper<ManagedAddress>;

    #[view(get_file)]
    #[storage_mapper("files")]
    fn files(&self, file_location: [u8; 46]) -> SingleValueMapper<File>;

    #[storage_mapper("file_locations")]
    fn file_locations(&self) -> UnorderedSetMapper<[u8; 46]>; //  Trainer X <- Qmdddd, Qmmaa

    #[view(get_stake)]
    #[storage_mapper("stakes")]
    fn stakes(&self, user_addr: ManagedAddress) -> SingleValueMapper<BigUint>;

    #[view(get_reputation)]
    #[storage_mapper("reputations")]
    fn reputations(&self, user_addr: ManagedAddress) -> SingleValueMapper<usize>;

    #[storage_mapper("file_evaluations")]
    fn file_evaluations(&self, file_location: [u8; 46]) -> UnorderedSetMapper<Evaluation<Self::Api>>;

    #[storage_mapper("author_files")]
    fn author_files(&self, author_addr: ManagedAddress) -> UnorderedSetMapper<[u8; 46]>;

    #[view(get_file_author)]
    #[storage_mapper("file_authors")]
    fn file_authors(&self, file_location: [u8; 46]) -> SingleValueMapper<ManagedAddress>;

    #[storage_mapper("round_files")]
    fn round_files(&self, round: usize) -> UnorderedSetMapper<[u8; 46]>;

    #[view(get_files_count)]
    #[storage_mapper("files_count")]
    fn files_count(&self) -> SingleValueMapper<usize>;

    #[view(get_users_count)]
    #[storage_mapper("users_count")]
    fn users_count(&self) -> SingleValueMapper<usize>;

    #[view(get_nodes_count)]
    #[storage_mapper("nodes_count")]
    fn nodes_count(&self) -> SingleValueMapper<u16>;

    #[view(get_clusters_count)]
    #[storage_mapper("clusters_count")]
    fn clusters_count(&self) -> SingleValueMapper<u16>;

    #[view(get_round)]
    #[storage_mapper("round")]
    fn round(&self) -> SingleValueMapper<usize>;

    #[view(get_stage)]
    #[storage_mapper("stage")]
    fn stage(&self) -> SingleValueMapper<Stage>;

    // Events ----------------------------------------------------------------

    // This method is used for testing purposes only, to simulate the occurrence of an event
    #[endpoint]
    fn test_event(&self, event_type: u8) {
        let test_user_addr = self.blockchain().get_caller().clone();
        let test_stake= BigUint::from(567u32);
        let test_role = Role::Trainer;
        let test_stage = Stage::ModelTraining;
        let test_file_type = FileType::ClusterAggregationModel;
        let test_round = 89;
        let test_reputation = 656;
        let test_evaluation_status = EvaluationStatus::Positive;
        let test_file_location: [u8; 46] = "QmUPW6vbfbTW7LGDMy6QrzxLRHMkUBAdVAfTCQKUuQj999".as_bytes().try_into().unwrap();

        if event_type == 1 {
            self.signup_user_event(test_user_addr, test_stake, test_role);
        }
        else if event_type == 2 {
            self.user_cleared_event(test_user_addr);
        }
        else if event_type == 3 {
            self.reputation_updated_event(test_user_addr, test_reputation);
        }
        else if event_type == 4 {
            self.set_round_event(test_round);
        }
        else if event_type == 5 {
            self.set_stage_event(test_stage);
        }
        else if event_type == 6 {
            self.upload_file_event(test_file_location, test_file_type, test_round, test_user_addr);
        }
        else if event_type == 7 {
            self.clear_file_event(test_file_location, test_file_type, test_round, test_user_addr);
        }
        else if event_type == 8 {
            self.evaluate_file_event(test_file_location, test_evaluation_status, test_user_addr);
        }
        else {
            sc_panic!("Do not know what event to publish!");
        }
    }
    
    #[event("signup_user_event")]
    fn signup_user_event(
        &self,
        #[indexed] user_addr: ManagedAddress,
        #[indexed] stake: BigUint,
        #[indexed] role: Role);

    #[event("user_cleared_event")]
    fn user_cleared_event(
        &self,
        #[indexed] user_addr: ManagedAddress);


    #[event("set_round_event")]
    fn set_round_event(
        &self,
        #[indexed] round: usize);
    
    #[event("set_stage_event")]
    fn set_stage_event(
        &self,
        #[indexed] stage: Stage);
    
    #[event("upload_file_event")]
    fn upload_file_event(
        &self,
        #[indexed] file_location: [u8; 46],
        #[indexed] file_type: FileType,
        #[indexed] round: usize,
        #[indexed] author_addr: ManagedAddress);

    #[event("clear_file_event")]
    fn clear_file_event(
        &self,
        #[indexed] file_location: [u8; 46],
        #[indexed] file_type: FileType,
        #[indexed] round: usize,
        #[indexed] author_addr: ManagedAddress);

    #[event("evaluate_file_event")]
    fn evaluate_file_event(
        &self,
        #[indexed] file_location: [u8; 46],
        #[indexed] status: EvaluationStatus,
        #[indexed] evaluator: ManagedAddress);
    
    #[event("reputation_updated_event")]
    fn reputation_updated_event(
        &self,
        #[indexed] user_addr: ManagedAddress,
        #[indexed] new_reputation: usize);
}
