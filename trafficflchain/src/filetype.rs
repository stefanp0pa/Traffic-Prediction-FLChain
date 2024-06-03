multiversx_sc::derive_imports!();

#[derive(TopEncode, TopDecode, NestedDecode, NestedEncode, TypeAbi, Clone, Copy, PartialEq, Eq, Debug, ManagedVecItem)]
pub enum FileType {
    Undefined,
    Dataset,
    ClusterModel,
    ClusterStructure, // adjacency matrix
    // ClusterDescription, // cluster encompassing nodes
    ClusterAggregationModel,
    // SensitiveDataBatch,
    // PublicDataBatch,
    // Model,
    // AggregationResult,
}