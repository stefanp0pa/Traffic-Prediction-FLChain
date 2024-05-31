multiversx_sc::derive_imports!();

#[derive(TopEncode, TopDecode, NestedDecode, NestedEncode, TypeAbi, Clone, Copy, PartialEq, Eq, Debug, ManagedVecItem)]
pub enum FileType {
    Undefined,
    SensitiveDataBatch,
    PublicDataBatch,
    Model,
    AggregationResult,
}

impl FileType {
    pub fn match_file_type(number: u8) -> Option<FileType> {
        match number {
            1 => Some(FileType::SensitiveDataBatch),
            2 => Some(FileType::PublicDataBatch),
            3 => Some(FileType::Model),
            4 => Some(FileType::AggregationResult),
            _ => Some(FileType::Undefined),
        }
    }
}