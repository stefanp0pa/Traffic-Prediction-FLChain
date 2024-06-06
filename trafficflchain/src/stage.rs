multiversx_sc::derive_imports!();

#[derive(TopEncode, TopDecode, NestedDecode, NestedEncode, TypeAbi, Clone, Copy, PartialEq, Eq, Debug, ManagedVecItem)]
pub enum Stage {
    Undefined,
    Initialization,
    DataCollection,
    ModelTraining,
    EvaluationCandidates,
    ModelAggregation,
    EvaluationAggregation,
    RewardsDistribution,
    Finalization,
}
