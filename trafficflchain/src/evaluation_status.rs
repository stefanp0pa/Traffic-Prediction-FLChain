multiversx_sc::derive_imports!();

#[derive(TopEncode, TopDecode, NestedDecode, NestedEncode, TypeAbi, Clone, Copy, PartialEq, Eq, Debug, ManagedVecItem)]
pub enum EvaluationStatus {
    Undefined,
    Positive,
    Negative,
}

impl EvaluationStatus {
    pub fn match_evaluation(number: u8) -> Option<EvaluationStatus> {
        match number {
            1 => Some(EvaluationStatus::Positive),
            2 => Some(EvaluationStatus::Negative),
            _ => Some(EvaluationStatus::Undefined),
        }
    }
}