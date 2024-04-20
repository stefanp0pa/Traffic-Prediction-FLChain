#![no_std]

multiversx_sc::imports!();
multiversx_sc::derive_imports!();

mod user;
mod participant_role;
mod session_manager;
use user::User;
use participant_role::Role;
use session_manager::SessionManager;

const ROUND_SECONDS: u64 = 6;
// const ROUNDS_FOR_SIGNUP: u64 = 6;
// const ROUNDS_FOR_TRAINING: u64 = 5;
// const ROUNDS_FOR_AGGREGATION: u64 = 2;

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi)]
pub struct Participant<M: ManagedTypeApi> {
    user_addr: ManagedAddress<M>,
    role: Role
}

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi)]
pub struct ModelUpdate<M: ManagedTypeApi, N: ManagedTypeApi> {
    user_addr: ManagedAddress<M>,
    file_location: ManagedBuffer<N>
}


#[multiversx_sc::contract]
pub trait FlchainDummy {

    #[init]
    fn init(&self) {
    }

    #[upgrade]
    fn upgrade(&self) {
    }

    #[endpoint]
    fn start_session(
        &self,
        global_model_addr: ManagedBuffer,
        rounds_signup: u64,
        rounds_training: u64,
        rounds_aggregation: u64
    ) {
        require!(
            self.active_session_manager().is_empty(),
            "Training session already started!"
        );

        let now = self.blockchain().get_block_timestamp();
        let caller: ManagedAddress = self.blockchain().get_caller();

        let mut rand_source = RandomnessSource::new();
        let session_id = rand_source.next_u64_in_range(0u64, 1000u64);
        self.active_session_manager().set(SessionManager {
            session_id,
            start_time: now,
            rounds_signup,
            rounds_training,
            rounds_aggregation,
            round_seconds: ROUND_SECONDS,
        });

        self.active_session_initiator().set(caller);
        self.version(session_id).set(0u32);
        self.global_updates(session_id, 0u32).insert(ModelUpdate {
            user_addr: self.blockchain().get_caller(),
            file_location: global_model_addr,
        });
        self.participants(session_id).insert(Participant {
            user_addr: self.blockchain().get_caller(),
            role: Role::Initiator,
        });

        self.active_round(session_id).set(1u8);

        self.session_started_event(session_id, now, rounds_signup, rounds_training, rounds_aggregation);
        self.new_signup_event(session_id, self.blockchain().get_caller(), Role::Initiator);
    }

    #[endpoint]
    fn end_session(&self) {
        require!(
            !self.active_session_manager().is_empty(),
            "Training session empty or already ended!"
        );
        
        let curr_time = self.blockchain().get_block_timestamp();
        let session_id = self.active_session_manager().get().session_id;

        self.clear_round_entities(session_id);
        self.session_ended_event(session_id, curr_time);
    }

    #[endpoint]
    fn signup(&self, role: u8) {
        require!(
            !self.active_session_manager().is_empty(),
            "Cannot signup! No training session ongoing!"
        );
        let session_manager = self.active_session_manager().get();
        let caller_addr = self.blockchain().get_caller();
        let session_id = session_manager.session_id;
        require!(
            !self.has_signed_up(caller_addr, session_id),
            "Cannot signup! Already signed up!"
        );
        
        self.participants(session_id).insert(Participant {
            user_addr: self.blockchain().get_caller(),
            role: Role::match_role(role).unwrap(),
        });

        self.new_signup_event(
            session_id,
            self.blockchain().get_caller(),
            Role::match_role(role).unwrap());
    }

    fn has_signed_up(&self, caller_addr: ManagedAddress, session_id: u64) -> bool {
        let session_participants = self.participants(session_id);
        let count = session_participants
                        .iter()
                        .filter(|participant| {
                            (*participant).user_addr == caller_addr
                        })
                        .count();
        return count > 0;
    }


    fn clear_round_entities(&self, session_id: u64) {
        let max_version = self.version(session_id).get();
        for i in 0u32..max_version {
            self.global_updates(session_id, i).clear();
            self.local_updates(session_id, i).clear();
        }

        self.active_round(session_id).clear();
        self.version(session_id).clear();
        self.participants(session_id).clear();
        self.active_session_initiator().clear();
        self.active_session_manager().clear();
    }

    #[view]
    fn trainers_count(&self, session_id: u64) -> usize {
        require!(
            !self.participants(session_id).is_empty(),
            "No participants in this session!"
        );
        
        let session_participants = self.participants(session_id);
        session_participants
                        .iter()
                        .filter(|participant| {
                            (*participant).role.can_train()
                        })
                        .count()
    }

    #[view]
    fn aggregators_count(&self, session_id: u64) -> usize {
        require!(
            !self.participants(session_id).is_empty(),
            "No participants in this session!"
        );
        
        let session_participants = self.participants(session_id);
        session_participants
                        .iter()
                        .filter(|participant| {
                            (*participant).role.can_upgate_global()
                        })
                        .count()
    }

    #[view]
    fn is_session_active(&self) -> bool {
        !self.active_session_manager().is_empty()
    }

    #[view]
    fn get_active_session(&self) -> u64 {
        require!(
            !self.active_session_manager().is_empty(),
            "No training session available!"
        );
        self.active_session_manager().get().session_id
        // let mut encoded = ManagedBuffer::new();
        // let _ = self.active_session_manager().get().top_encode(&mut encoded);
        // encoded
    }

    #[view]
    fn is_signup_open(&self) -> bool {
        require!(
            !self.active_session_manager().is_empty(),
            "No training session available!"
        );

        let curr_time = self.blockchain().get_block_timestamp();
        self.active_session_manager().get().is_signup_open(curr_time)
    }

    #[view]
    fn is_training_open(&self) -> bool {
        require!(
            !self.active_session_manager().is_empty(),
            "No training session available!"
        );

        let curr_time = self.blockchain().get_block_timestamp();
        self.active_session_manager().get().is_training_open(curr_time)
    }

    #[view]
    fn is_aggregation_open(&self) -> bool {
        require!(
            !self.active_session_manager().is_empty(),
            "No training session available!"
        );

        let curr_time = self.blockchain().get_block_timestamp();
        self.active_session_manager().get().is_aggregation_open(curr_time)
    }

    #[view]
    fn get_session_initiator(&self) -> ManagedAddress {
        require!(
            !self.active_session_initiator().is_empty(),
            "No training session available!"
        );

        self.active_session_initiator().get()
    }

    #[view]
    fn get_active_round(&self, session_id: u64) -> u8 {
        self.active_round(session_id).get()
    }

    #[endpoint]
    fn set_active_round(&self, round: u8) {
        require!(
            !self.active_session_manager().is_empty(),
            "No training session available!"
        );

        let session_id = self.active_session_manager().get().session_id;
        self.active_round(session_id).set(round);
        if round == 1u8 {
            self.signup_started_event(session_id);
        } else if round == 2u8 {
            self.training_started_event(session_id);
        } else if round == 3u8 {
            self.aggregation_started_event(session_id);
        } else if round == 4u8 {
            self.evaluation_started_event(session_id);
        }
    }

    #[endpoint]
    fn set_global_version(&self, file_location: ManagedBuffer) {
        require!(
            !self.active_session_initiator().is_empty(),
            "No training session available!"
        );
        let caller = self.blockchain().get_caller();
        let session_id = self.active_session_manager().get().session_id;
        let mut version = self.version(session_id).get();
        version = version + 1;
        self.global_updates(session_id, version).insert(ModelUpdate {
            user_addr: caller,
            file_location,
        });
        self.version(session_id).set(version);
    }

    #[view]
    fn get_current_global_version(&self) -> ManagedBuffer {
        require!(
            !self.active_session_initiator().is_empty(),
            "No training session available!"
        );

        let session_id = self.active_session_manager().get().session_id;
        let version = self.version(session_id).get();
        self.global_updates(session_id, version)
            .iter().next().unwrap().file_location
    }

    #[endpoint]
    fn set_local_update(&self, file_location: ManagedBuffer) {
        require!(
            !self.active_session_initiator().is_empty(),
            "No training session available!"
        );
        let caller = self.blockchain().get_caller();
        let session_id = self.active_session_manager().get().session_id;
        let version = self.version(session_id).get();
        self.local_updates(session_id, version).insert(ModelUpdate {
            user_addr: caller,
            file_location,
        });
    }

    #[view]
    fn get_local_updates(&self) -> ManagedVec<ManagedBuffer> {
        require!(
            !self.active_session_initiator().is_empty(),
            "No training session available!"
        );
        let session_id = self.active_session_manager().get().session_id;
        let version = self.version(session_id).get();
        let mut result: ManagedVec<ManagedBuffer> = ManagedVec::new();
        for update in self.local_updates(session_id, version).iter() {
            result.push(update.file_location);
        }
        result
    }

    #[view]
    fn get_timestamp(&self) -> u64 {
        self.blockchain().get_block_timestamp()
    }

    // Events.............................................

    #[event("session_started_event")]
    fn session_started_event(
        &self,
        #[indexed] session_id: u64,
        #[indexed] start_time: u64,
        #[indexed] rounds_signup: u64,
        #[indexed] rounds_training: u64,
        #[indexed] rounds_aggregation: u64,
    );

    #[event("session_ended_event")]
    fn session_ended_event(
        &self,
        #[indexed] session_id: u64,
        #[indexed] end_time: u64,
    );

    #[event("new_signup_event")]
    fn new_signup_event(
        &self,
        #[indexed] session_id: u64,
        #[indexed] user: ManagedAddress,
        #[indexed] role: Role,
    );

    #[event("signup_started_event")]
    fn signup_started_event(
        &self,
        #[indexed] session_id: u64
    );

    #[event("training_started_event")]
    fn training_started_event(
        &self,
        #[indexed] session_id: u64
    );

    #[event("aggregation_started_event")]
    fn aggregation_started_event(
        &self,
        #[indexed] session_id: u64
    );

    #[event("evaluation_started_event")]
    fn evaluation_started_event(
        &self,
        #[indexed] session_id: u64
    );

    // ----------------------------------------------------

    #[storage_mapper("active_session_manager")]
    fn active_session_manager(&self) -> SingleValueMapper<SessionManager>;

    #[storage_mapper("active_session_initiator")]
    fn active_session_initiator(&self) -> SingleValueMapper<ManagedAddress>;

    #[storage_mapper("active_round")]
    fn active_round(&self, sessiond_id: u64) -> SingleValueMapper<u8>;

    // -----------------------------------------------

    // stores all the users that have signeup up so far in a round
    #[storage_mapper("users")]
    fn users(&self, address: ManagedAddress) -> UnorderedSetMapper<User>;

    #[storage_mapper("participants")]
    fn participants(&self, session_id: u64) -> UnorderedSetMapper<Participant<Self::Api>>;

    // -----------------------------------------------

    #[storage_mapper("local_updates")]
    fn local_updates(&self, session_id: u64, version: u32) -> UnorderedSetMapper<ModelUpdate<Self::Api, Self::Api>>;

    #[storage_mapper("global_updates")]
    fn global_updates(&self, session_id: u64, version: u32) -> UnorderedSetMapper<ModelUpdate<Self::Api, Self::Api>>;

    #[storage_mapper("version")]
    fn version(&self, session_id: u64) -> SingleValueMapper<u32>;
}   
