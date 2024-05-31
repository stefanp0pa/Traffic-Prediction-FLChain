#![no_std]

multiversx_sc::imports!();
multiversx_sc::derive_imports!();

mod role;
mod filetype;
mod evaluation_status;

use role::Role;
use filetype::FileType;
use evaluation_status::EvaluationStatus;

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi, Clone)]
pub struct GraphTopology<M: ManagedTypeApi> {
    pub vertices_count: u64,
    pub edges_count: u64,
    pub owner: ManagedAddress<M>,
    pub storage_addr: [u8; 46], // IPFS hash CDv1
    pub timestamp: u64,
    pub hash: [u8; 32],
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
    fn init(&self) {}

    #[upgrade]
    fn upgrade(&self) {}

    // Graph -----------------------------------------------------------------
    #[endpoint]
    fn setup_network(
        &self, city_id: u64, vertices_count: u64, edges_count: u64, storage_addr: [u8; 46], hash: [u8; 32]) {
        let owner = self.blockchain().get_caller();
        let timestamp = self.blockchain().get_block_timestamp();
        let graph = GraphTopology {
            vertices_count,
            edges_count,
            owner,
            storage_addr,
            timestamp,
            hash,
        };
        require!(
            self.graph_networks(city_id).is_empty(),
            "Network already exists, please clear it first."
        );
        self.graph_networks(city_id).set(graph);
        self.network_setup_event(city_id);
    }

    #[endpoint]
    fn clear_network(&self, city_id: u64) {
        require!(
            !self.graph_networks(city_id).is_empty(),
            "Network does not exist!"
        );
        require!(
            self.blockchain().get_caller() == self.graph_networks(city_id).get().owner,
            "Only the owner can clear the network!"
        );

        self.graph_networks(city_id).clear();
        self.network_cleared_event(city_id);
    }

    // Data ------------------------------------------------------------------
    #[endpoint]
    fn upload_file(
        &self, file_location: [u8; 46], file_type: FileType, round: usize) {
        let caller = self.blockchain().get_caller();
        let file = File { file_location, file_type, round };

        let round = self.round().get();
        self.files(file_location.clone()).set(file);
        self.file_locations().insert(file_location.clone());
        self.author_files(caller.clone()).insert(file_location.clone());
        self.file_authors(file_location.clone()).set(caller.clone());
        self.round_files(round).insert(file_location.clone());
        self.files_count().update(|count| { *count += 1 });

        self.upload_file_event(file_location, file_type, round, caller);
    }

    #[endpoint]
    fn clear_file(&self, file_location: [u8; 46]) {
        if self.files(file_location.clone()).is_empty() {
            sc_panic!("File does not exist!");
        }
        else {
            let file_author = self.file_authors(file_location.clone()).get();
            let caller = self.blockchain().get_caller();
            
            // require!(
            //     caller == author,
            //     "Only the author can clear the file!"
            // );

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

    #[endpoint]
    fn evaluate_file(&self, file_location: [u8; 46], status: EvaluationStatus) {
        let caller = self.blockchain().get_caller();
        if self.files(file_location.clone()).is_empty() {
            sc_panic!("File does not exist!");
        }
        else {
            self.file_evaluations(file_location.clone()).insert(Evaluation {
                evaluator: caller.clone(),
                status
            });
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

    #[view]
    fn get_all_round_files(&self, round: usize) -> ManagedVec<File> {
        let mut output: ManagedVec<File> = ManagedVec::new();
        for file in self.round_files(round).iter() {
            output.push(self.files(file.clone()).get());
        }
        output
    }

    // Trainers --------------------------------------------------------------

    // Global ----------------------------------------------------------------

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

    // Storage mappers -------------------------------------------------------
    #[view(get_graph_network)]
    #[storage_mapper("graph_networks")]
    fn graph_networks(&self, city_id: u64) -> SingleValueMapper<GraphTopology<Self::Api>>;

    #[view(get_user)]
    #[storage_mapper("users")]
    fn users(&self, user_addr: ManagedAddress) -> SingleValueMapper<User<Self::Api>>;

    #[view(get_user_addresses)]
    #[storage_mapper("user_addresses")]
    fn user_addresses(&self) -> UnorderedSetMapper<ManagedAddress>;

    #[view(get_file)]
    #[storage_mapper("files")]
    fn files(&self, file_location: [u8; 46]) -> SingleValueMapper<File>;

    #[view(get_file_locations)]
    #[storage_mapper("file_locations")]
    fn file_locations(&self) -> UnorderedSetMapper<[u8; 46]>;

    #[view(get_stake)]
    #[storage_mapper("stakes")]
    fn stakes(&self, user_addr: ManagedAddress) -> SingleValueMapper<BigUint>;

    #[view(get_reputation)]
    #[storage_mapper("reputations")]
    fn reputations(&self, user_addr: ManagedAddress) -> SingleValueMapper<usize>;

    #[view(file_evaluations)]
    #[storage_mapper("file_evaluations")]
    fn file_evaluations(&self, file_location: [u8; 46]) -> UnorderedSetMapper<Evaluation<Self::Api>>;

    #[view(get_author_files)]
    #[storage_mapper("author_files")]
    fn author_files(&self, author_addr: ManagedAddress) -> UnorderedSetMapper<[u8; 46]>;

    #[view(get_file_author)]
    #[storage_mapper("file_authors")]
    fn file_authors(&self, file_location: [u8; 46]) -> SingleValueMapper<ManagedAddress>;

    #[view(get_round_files)]
    #[storage_mapper("round_files")]
    fn round_files(&self, round: usize) -> UnorderedSetMapper<[u8; 46]>;

    #[view(get_files_count)]
    #[storage_mapper("files_count")]
    fn files_count(&self) -> SingleValueMapper<usize>;

    #[view(get_users_count)]
    #[storage_mapper("users_count")]
    fn users_count(&self) -> SingleValueMapper<usize>;

    #[view(get_round)]
    #[storage_mapper("round")]
    fn round(&self) -> SingleValueMapper<usize>;


    // Events ----------------------------------------------------------------
    #[event("network_setup_event")]
    fn network_setup_event(
        &self,
        #[indexed] city_id: u64);

    #[event("network_cleared_event")]
    fn network_cleared_event(
        &self,
        #[indexed] city_id: u64);
    
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
    
    #[event("reputation_updated_event")]
    fn reputation_updated_event(
        &self,
        #[indexed] user_addr: ManagedAddress,
        #[indexed] new_reputation: usize);

    #[event("set_round_event")]
    fn set_round_event(
        &self,
        #[indexed] round: usize);
    
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
}
