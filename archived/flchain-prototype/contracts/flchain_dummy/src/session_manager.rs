multiversx_sc::imports!();
multiversx_sc::derive_imports!();

#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, TypeAbi)]
pub struct SessionManager {
    pub session_id: u64,
    pub start_time: u64,
    pub rounds_signup: u64,
    pub rounds_training: u64,
    pub rounds_aggregation: u64,
    pub round_seconds: u64,
}

impl SessionManager {
    pub fn rounds_per_learning_epoch(&self) -> u64 {
        self.rounds_training + self.rounds_aggregation
    }

    pub fn seconds_per_learning_epoch(&self) -> u64 {
        self.round_seconds * self.rounds_per_learning_epoch()
    }

    pub fn is_signup_open(&self, curr_time: u64) -> bool {
        let signup_max_time = self.start_time + self.rounds_signup * self.round_seconds;
        curr_time <= signup_max_time
    }

    pub fn is_training_open(&self, curr_time: u64) -> bool {
        if self.is_signup_open(curr_time) {
            return false;
        }

        let signup_max_time = self.start_time + self.rounds_signup * self.round_seconds;
        let diff_timestamp = curr_time - signup_max_time;
        let diff_rounds = diff_timestamp / self.round_seconds;
        let curr_epoch_round = diff_rounds % self.rounds_per_learning_epoch();
        return curr_epoch_round < self.rounds_training;
    }

    pub fn is_aggregation_open(&self, curr_time: u64) -> bool {

        if self.is_signup_open(curr_time) {
            return false;
        }

        let signup_max_time = self.start_time + self.rounds_signup * self.round_seconds;
        let diff_timestamp = curr_time - signup_max_time;
        let diff_rounds = diff_timestamp / self.round_seconds;
        let curr_epoch_round = diff_rounds % self.rounds_per_learning_epoch();
        return curr_epoch_round >= self.rounds_training;
    }
}