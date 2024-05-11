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
    fn get_local_updates(&self) -> ManagedVec<u16> {

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

    #[view]
    fn get_serialized_network_data(&self, city_id: u64) -> ManagedBuffer<Self::Api> {
        require!(
            !self.graph_networks(city_id).is_empty(),
            "Network does not exist!"
        );

        let graph = self.graph_networks(city_id).get();

        let mut vertices_buff = ManagedBuffer::new();
        let _ = graph.vertices_count.top_encode(&mut vertices_buff);
        let mut edges_buff = ManagedBuffer::new();
        let _ = graph.edges_count.top_encode(&mut edges_buff);
        let mut storage_addr_buff = ManagedBuffer::new();
        let _ = graph.storage_addr.top_encode(&mut storage_addr_buff);
        let mut timestamp_buff = ManagedBuffer::new();
        let _ = graph.timestamp.top_encode(&mut timestamp_buff);
        let mut hash_buff = ManagedBuffer::new();
        let _ = graph.hash.top_encode(&mut hash_buff);
        let delimiter = ManagedBuffer::from(b"\0\0\0\0");
        let mut serialized_attributes = ManagedBuffer::new();

        let _ = serialized_attributes.append(&vertices_buff);
        let _ = serialized_attributes.append(&delimiter);
        let _ = serialized_attributes.append(&edges_buff);
        let _ = serialized_attributes.append(&delimiter);
        let _ = serialized_attributes.append(&delimiter);
        let _ = serialized_attributes.append(&storage_addr_buff);
        let _ = serialized_attributes.append(&delimiter);
        let _ = serialized_attributes.append(&timestamp_buff);
        let _ = serialized_attributes.append(&delimiter);
        let _ = serialized_attributes.append(&hash_buff);

        serialized_attributes
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
    fn graph_networks(&self, city_id: u64) -> SingleValueMapper<GraphTolopogy<Self::Api, Self::Api>>;

    // #[view(getUserAddress)]
    // #[storage_get("user_address")]
    // fn get_user_address(&self, user_id: usize) -> ManagedAddress;

    // #[storage_set("user_address")]
    // fn set_user_address(&self, user_id: usize, address: &ManagedAddress);

    // Events ----------------------------------------------------------------
    #[event("network_setup_event")]
    fn network_setup_event(&self, city_id: u64);

    #[event("network_cleared_event")]
    fn network_cleared_event(&self, city_id: u64);

    #[event("data_batch_published_event")]
    fn data_batch_published_event(&self);
}
