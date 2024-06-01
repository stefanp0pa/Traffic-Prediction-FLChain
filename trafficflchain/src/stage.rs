multiversx_sc::derive_imports!();

#[derive(TopEncode, TopDecode, NestedDecode, NestedEncode, TypeAbi, Clone, Copy, PartialEq, Eq, Debug, ManagedVecItem)]
pub enum Stage {
    Undefined,
    Initialization,
    DataCollection,
    ModelTraining,
    ModelAggregation,
    Evaluation,
    RewardsDistribution,
    Finalization,
}

impl Stage {
    pub fn match_stage(number: u8) -> Option<Stage> {
        match number {
            1 => Some(Stage::Initialization),
            2 => Some(Stage::DataCollection),
            3 => Some(Stage::ModelTraining),
            4 => Some(Stage::ModelAggregation),
            5 => Some(Stage::Evaluation),
            6 => Some(Stage::RewardsDistribution),
            7 => Some(Stage::Finalization),
            _ => Some(Stage::Undefined),
        }
    }
}
