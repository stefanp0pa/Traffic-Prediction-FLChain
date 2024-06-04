multiversx_sc::derive_imports!();

#[derive(TopEncode, TopDecode, NestedDecode, NestedEncode, TypeAbi, Clone, Copy, PartialEq, Eq, Debug, ManagedVecItem)]
pub enum FileType {
    Undefined,
    Dataset,
    FootprintModel, // per (node, cluster) tuple each round
    ClusterStructure, // per cluster, adjacency matrix
    ClusterAggregationModel, // per cluster each round
    CandidateModel, // per (node, cluster) tuple each round
}