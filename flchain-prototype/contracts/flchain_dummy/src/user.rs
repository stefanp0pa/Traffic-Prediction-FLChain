multiversx_sc::derive_imports!();

pub const BAN_REPUTATION: (u32, u32) = (0, 50);
pub const LOW_REPUTATION: (u32, u32) = (50, 100);
pub const MED_REPUTATION: (u32, u32) = (100, 200);
pub const HIGH_REPUTATION: (u32, u32) = (200, 1000);

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi)]
pub struct User {
  reputation: u32,
}

impl User {
    pub fn can_propose(&self) -> bool {
        self.reputation > LOW_REPUTATION.0
    }
    pub fn can_train(&self) -> bool {
        self.reputation > MED_REPUTATION.0
    }
    pub fn can_update_global(&self) -> bool {
        self.reputation > HIGH_REPUTATION.0
    }
    pub fn can_do_nothing(&self) -> bool {
        self.reputation < BAN_REPUTATION.1
    }
}