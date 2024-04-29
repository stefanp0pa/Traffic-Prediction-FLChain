#![no_std]

multiversx_sc::imports!();
multiversx_sc::derive_imports!();

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi)]
pub struct GraphTolopogy<M: ManagedTypeApi, N: ManagedTypeApi> {
    pub vertices_count: u64,
    pub edges_count: u64,
    pub owner: ManagedAddress<M>,
    pub storage_addr: ManagedBuffer<N>,
    pub timestamp: u64,
    pub hash: [u8; 32],
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
        self.graph_networks(city_id).insert(graph);
        self.network_setup_event(city_id);
    }

    #[view]
    fn get_network_storage_addr(&self, city_id: u64) -> ManagedBuffer<Self::Api> {
        self.graph_networks(city_id).get_by_index(1).storage_addr
    }

    // Data ------------------------------------------------------------------
    #[endpoint]
    fn publish_data_batch(&self) {
    }

    // Trainers --------------------------------------------------------------

    // Global ----------------------------------------------------------------

    // Storage mappers -------------------------------------------------------
    #[view(getGraphNetwork)]
    #[storage_mapper("graph_networks")]
    fn graph_networks(&self, city_id: u64) -> UnorderedSetMapper<GraphTolopogy<Self::Api, Self::Api>>;

    // #[view(getUserAddress)]
    // #[storage_get("user_address")]
    // fn get_user_address(&self, user_id: usize) -> ManagedAddress;

    // #[storage_set("user_address")]
    // fn set_user_address(&self, user_id: usize, address: &ManagedAddress);

    // Events ----------------------------------------------------------------
    #[event("network_setup_event")]
    fn network_setup_event(&self, city_id: u64);

    #[event("data_batch_published_event")]
    fn data_batch_published_event(&self);
}
