multiversx_sc::derive_imports!();

#[derive(TopEncode, TopDecode, NestedDecode, NestedEncode, TypeAbi, Clone, Copy, PartialEq, Eq, Debug)]
pub enum Role {
    Undefined,
    Initiator,
    Sampler,
    Trainer,
    Evaluator,
    Aggregator,
    EventsProcessor,
}

impl Role {
    pub fn match_role(number: u8) -> Option<Role> {
        match number {
            1 => Some(Role::Initiator),
            2 => Some(Role::Sampler),
            3 => Some(Role::Trainer),
            4 => Some(Role::Evaluator),
            5 => Some(Role::Aggregator),
            6 => Some(Role::EventsProcessor),
            _ => Some(Role::Undefined),
        }
    }
}