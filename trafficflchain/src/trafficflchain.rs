#![no_std]

multiversx_sc::imports!();
multiversx_sc::derive_imports!();
use multiversx_sc::codec::TopEncodeMulti;

mod role;
mod filetype;

use role::Role;
use filetype::FileType;

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi)]
pub struct GraphTolopogy<M: ManagedTypeApi, N: ManagedTypeApi> {
    pub vertices_count: u64,
    pub edges_count: u64,
    pub owner: ManagedAddress<M>,
    pub storage_addr: ManagedBuffer<N>,
    pub timestamp: u64,
    pub hash: [u8; 32],
}

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi)]
pub struct User {
    role: Role,
    reputation: u32,
    stake: u32,
}

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi)]
pub struct File<M: ManagedTypeApi> {
    file_location: ManagedBuffer<M>,
    file_hash: [u8; 32],
    approval_evaluators: ManagedVec<M, ManagedAddress<M>>,
    disapproval_evaluators: ManagedVec<M, ManagedAddress<M>>,
    file_type: FileType,
    epoch: u64
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
        &self,
        city_id: u64,
        vertices_count: u64,
        edges_count: u64,
        storage_addr: ManagedBuffer<Self::Api>,
        hash: [u8; 32]) {
        let owner = self.blockchain().get_caller();
        let timestamp = self.blockchain().get_block_timestamp();
        let graph = GraphTolopogy {
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

    #[view]
    fn get_local_updates(&self) -> ManagedVec<u32> {

        // let session_id = self.active_session_manager().get().session_id;
        // let version = self.version(session_id).get();
        // let mut result: ManagedVec<ManagedBuffer> = ManagedVec::new();
        // for update in self.local_updates(session_id, version).iter() {
        //     result.push(update.file_location);
        // }
        let mut a = ManagedVec::new();
        a.push(1);
        a.push(2);
        a.push(3);
        a
    }

    // Data ------------------------------------------------------------------
    #[endpoint]
    fn publish_data_batch(&self) {
    }

    // Trainers --------------------------------------------------------------

    // Global ----------------------------------------------------------------

    // Users -----------------------------------------------------------------
    #[endpoint]
    fn sign_up(&self) {
        let caller: ManagedAddress = self.blockchain().get_caller();
        let already_signed_up = self.users(caller.clone()).is_empty();
        if !already_signed_up {
            sc_panic!("Already signed up!");
        }
        else {
            self.users(caller.clone()).insert(User {
                role: Role::Sampler,
                reputation: 123u32,
                stake: 99u32,
            });
            self.signup_user_event(caller, Role::Undefined);
            self.users_count().set(self.users_count().get() + 1);
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
            self.users(caller.clone()).clear();
            self.user_cleared_event(caller.clone());
            self.users_count().set(self.users_count().get() - 1);
        }
    }

    // #[view]
    // fn get_users_by_role(&self, role: Role) -> ManagedVec<ManagedAddress> {
    //     let mut output: ManagedVec<ManagedAddress> = ManagedVec::new();
    //     for user in self.users()
    //         .iter().filter {
    //         if user.role == role {
    //             output.push(user);
    //         }
    //     }
    //     output
    // }

    #[view]
    fn get_serialized_user_data(&self, user_addr: ManagedAddress) -> ManagedVec<ManagedBuffer<Self::Api>> {
        require!(
            !self.users(user_addr.clone()).is_empty(),
            "User does not exist!"
        );

        let mut output: ManagedVec<ManagedBuffer<Self::Api>> = ManagedVec::new();
        let _ = self.users(user_addr.clone()).multi_encode(&mut output);
        output
    }

    #[view]
    fn get_serialized_network_data(&self, city_id: u64) -> ManagedBuffer<Self::Api> {
        require!(
            !self.graph_networks(city_id).is_empty(),
            "Network does not exist!"
        );

        let mut output: ManagedBuffer<Self::Api> = ManagedBuffer::new();
        let _ = self.graph_networks(city_id).get().top_encode(&mut output);
        output
    }

    // Storage mappers -------------------------------------------------------
    #[view(get_graph_networks)]
    #[storage_mapper("graph_networks")]
    fn graph_networks(&self, city_id: u64) -> SingleValueMapper<GraphTolopogy<Self::Api, Self::Api>>;

    #[view(get_users)]
    #[storage_mapper("users")]
    fn users(&self, user_addr: ManagedAddress) -> UnorderedSetMapper<User>;

    #[view(get_files)]
    #[storage_mapper("files")]
    fn files(&self, author_addr: ManagedAddress) -> UnorderedSetMapper<File<Self::Api>>;

    #[view(get_users_count)]
    #[storage_mapper("users_count")]
    fn users_count(&self) -> SingleValueMapper<u64>;

    #[view(get_files_count)]
    #[storage_mapper("files_count")]
    fn files_count(&self) -> SingleValueMapper<u64>;

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
        #[indexed] user_addr: ManagedAddress<Self::Api>,
        #[indexed] role: Role);

    #[event("user_cleared_event")]
    fn user_cleared_event(
        &self,
        #[indexed] user_addr: ManagedAddress<Self::Api>);

    #[event("data_batch_published_event")]
    fn data_batch_published_event(&self);
}
