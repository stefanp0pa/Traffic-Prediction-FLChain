multiversx_sc::derive_imports!();

#[derive(TopEncode, TopDecode, NestedDecode, NestedEncode, TypeAbi, Clone, Copy, PartialEq, Eq, Debug)]
pub enum Role {
    Initiator,
    Trainer,
    Aggregator
}

impl Role {
    pub fn can_initiate(&self) -> bool {
        matches!(*self, Role::Initiator)
    }
    
    pub fn can_train(&self) -> bool {
        matches!(*self, Role::Trainer)
    }

    pub fn can_upgate_global(&self) -> bool {
        matches!(*self, Role::Aggregator)
    }

    pub fn can_end_session(&self) -> bool {
        matches!(*self, Role::Initiator)
    }

    pub fn match_role(number: u8) -> Option<Role> {
        match number {
            0 => Some(Role::Initiator),
            1 => Some(Role::Trainer),
            2 => Some(Role::Aggregator),
            _ => None
        }
    }
}