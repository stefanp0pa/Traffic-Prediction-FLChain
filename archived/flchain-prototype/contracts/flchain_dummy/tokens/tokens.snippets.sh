GAS_LIMIT=60000000
PROXY="https://devnet-gateway.multiversx.com"
TESTNET_PROXY="https://testnet-api.multiversx.com"
CHAIN_ID="D"
TESTNET_CHAIN_ID="T"
WALLET_PEM="/Users/stefan/ssi-proiect/contracts/wallets/wallet2.pem"

ISSUANCE_SC="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
ISSUANCE_FEE=50000000000000000 # 0.05 EGLD
ISSUANCE_FUNCTION="issueNonFungible"

SET_ROLE_FUNCTION="setSpecialRole"
ADDRESS_FOR_ROLES="erd1hgzhjjw47405npzjh8drx9hx4setln9phu798nhwvtgnz5lmdtts0pze2d"
HEX_ADDRESS_FOR_ROLES="0xba057949d5f55f498452b9da3316e6ac32bfcca1bf3c53ceee62d13153fb6ad7"
HEX_ESDTRoleNFTCreate="0x45534454526f6c654e4654437265617465" # ESDTRoleNFTCreate
HEX_ESDTRoleNFTBurn="0x45534454526f6c654e46544275726e" # ESDTRoleNFTBurn
HEX_ESDTRoleNFTUpdateAttributes="0x45534454526f6c654e465455706461746541747472696275746573" # ESDTRoleNFTUpdateAttributes
HEX_ESDTRoleNFTAddURI="0x45534454526f6c654e4654416464555249" # ESDTRoleNFTAddURI
HEX_ESDTTransferRole="0x455344545472616e73666572526f6c65" # ESDTTransferRole

CREATE_NFT_FUNCTION="ESDTNFTCreate"
CREATE_NFT_RECEIVER="erd1hgzhjjw47405npzjh8drx9hx4setln9phu798nhwvtgnz5lmdtts0pze2d"
HEX_CREATE_NFT_RECEIVER="0xba057949d5f55f498452b9da3316e6ac32bfcca1bf3c53ceee62d13153fb6ad7"

NFT_TRANSFER_FUNCTION="ESDTNFTTransfer"
NFT_TRANSFER_TARGET="erd1xvhadwera3dwy2z8j7qzdxkez9vmmzm9zprcq4c76a7svwwahkwqvp3j9k"
HEX_NFT_TRANSFER_TARGET="0x332fd6bb23ec5ae228479780269ad91159bd8b65104780571ed77d0639ddbd9c"

UPGRADE_NFT_FUNCTION="controlChanges"

# The receiver address erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u
# is a built-in system smart contract (not a VM-executable contract), which only handles
# token issuance and other token management operations, and does not handle any transfers.
# The contract will add a random string to the ticker thus creating the token identifier.
# The random string starts with “-” and has 6 more random characters.
# For example, a token identifier could look like ALC-6258d2.

# StefanPopaTokenBPDA = 0x53746566616e506f7061546f6b656e42504441
# SPTBPDA = 0x53505442504441
# SPTBPDA-0c96c4 = 0x535054425044412d306339366334
# IssuanceTx = https://devnet-explorer.multiversx.com/transactions/3e26ac425b57e8e6160a72763689d3f8f47a4b973db58a63fc03cdbef0e0623d
# Collection = https://devnet-explorer.multiversx.com/collections/SPTBPDA-0c96c4

# Roles can be seen from here: https://devnet-explorer.multiversx.com/collections/SPTBPDA-0c96c4/roles
# SettingRolesTx = https://devnet-explorer.multiversx.com/transactions/2dc484b0fda2d5b0c9b064885776685dbdfc85c3378d8fa381a3a0e2b114b6e6

# NFTCreationTx = https://devnet-explorer.multiversx.com/transactions/a750fde3e1e834a44f0030f10cb7718907a028780ded88d8d5aeddf6ec655e78


# Arguments
# "@" + <token name in hexadecimal encoding> +
# "@" + <token ticker in hexadecimal encoding>
issue_nft() {
    mxpy --verbose contract call ${ISSUANCE_SC} --recall-nonce \
        --pem=${WALLET_PEM} \
        --gas-limit=${GAS_LIMIT} \
        --proxy=${PROXY} --chain=${CHAIN_ID} \
        --value ${ISSUANCE_FEE} \
        --function ${ISSUANCE_FUNCTION} \
        --arguments $1 $2 \
        --send
}

HEX_COLLECTION_NAME="0x53746566616e506f7061546f6b656e42504441"
HEX_TOKEN_TICKER="0x53505442504441"
HEX_TOKEN_IDENTIFIER="0x535054425044412d306339366334"
HEX_INITIAL_NFT_QUANTITY="0x01"
NFT_NAME="Stefan Popa SSA2"
HEX_NFT_NAME="0x53746566616e20506f70612053534132"
ROYALTIES="7500" # 75%
HEX_ROYALTIES="0x1d4c"
NFT_ATTRIBUTES="metadata:QmRcP94kXr5zZjRGvi7mJ6un7LpxUhYVR4R4RpicxzgYkt;tags:curs_blockchain,laborator;"
HEX_NFT_ATTRIBUTES="0x6d657461646174613a516d52635039346b5872357a5a6a52477669376d4a36756e374c7078556859565234523452706963787a67596b743b746167733a637572735f626c6f636b636861696e2c6c61626f7261746f723b"
NFT_HASH="00"
HEX_NFT_HASH="0x00"
NFT_URI="https://ipfs.io/ipfs/QmSm1itcuANii3S7ENevbssv5eowLqju8b1Ve8C3Vt51F7"
HEX_NFT_URI="0x68747470733a2f2f697066732e696f2f697066732f516d536d3169746375414e6969335337454e65766273737635656f774c716a753862315665384333567435314637"

# Arguments
# "@" + <token identifier in hexadecimal encoding> +
# "@" + <address to assign the role(s) in a hexadecimal encoding> +
# "@" + <role in hexadecimal encoding> +
# "@" + <role in hexadecimal encoding> +
assign_create_nft_role() {
    mxpy --verbose contract call ${ISSUANCE_SC} --recall-nonce \
        --pem=${WALLET_PEM} \
        --gas-limit=${GAS_LIMIT} \
        --proxy=${PROXY} --chain=${CHAIN_ID} \
        --function=${SET_ROLE_FUNCTION} \
        --arguments ${HEX_TOKEN_IDENTIFIER} ${HEX_ADDRESS_FOR_ROLES} ${HEX_ESDTRoleNFTCreate} ${HEX_ESDTRoleNFTBurn} ${HEX_ESDTRoleNFTUpdateAttributes} ${HEX_ESDTRoleNFTAddURI} ${HEX_ESDTTransferRole} \
        --send
}

create_nft() {
    mxpy --verbose contract call ${CREATE_NFT_RECEIVER} --recall-nonce \
        --pem=${WALLET_PEM} \
        --gas-limit=${GAS_LIMIT} \
        --proxy=${PROXY} --chain=${CHAIN_ID} \
        --function ${CREATE_NFT_FUNCTION} \
        --arguments ${HEX_TOKEN_IDENTIFIER} ${HEX_INITIAL_NFT_QUANTITY} ${HEX_NFT_NAME} ${HEX_ROYALTIES} ${HEX_NFT_HASH} ${HEX_NFT_ATTRIBUTES} ${HEX_NFT_URI} \
        --send
}

upgrade_nft() {
    mxpy --verbose contract call ${ISSUANCE_SC} --recall-nonce \
        --pem=${WALLET_PEM} \
        --gas-limit=${GAS_LIMIT} \
        --proxy=${PROXY} --chain=${CHAIN_ID} \
        --function ${UPGRADE_NFT_FUNCTION}
        --arguments ${HEX_TOKEN_IDENTIFIER} 

}

# is this a transaction??
transfer_nft() {
    mxpy --verbose contract call ${CREATE_NFT_RECEIVER} --recall-nonce \
        --pem=${WALLET_PEM} \
        --gas-limit=${GAS_LIMIT} \
        --proxy=${PROXY} --chain=${CHAIN_ID} \
        --function ${NFT_TRANSFER_FUNCTION} \
        --arguments ${HEX_TOKEN_IDENTIFIER} 0x01 0x01 ${HEX_NFT_TRANSFER_TARGET} \
        --send
}

# ESDTNFTTransfer@535054425044412d306339366334@01@01@332fd6bb23ec5ae228479780269ad91159bd8b65104780571ed77d0639ddbd9c
# ESDTNFTTransfer@53505442504441@01@01@332FD6BB23EC5AE228479780269AD91159BD8B65104780571ED77D0639DDBD9C
