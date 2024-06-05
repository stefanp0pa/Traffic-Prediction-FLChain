ipfs_init() {
    ipfs init
    ipfs id
}

ipfs_id() {
    ipfs id
}

ipfs_upload() {
    IPFS_FILE_ID=$(ipfs add $1 | awk '{print $2}')
    echo "File ID is: ${IPFS_FILE_ID}"
}

ipfs_show_file() {
    ipfs cat $IPFS_FILE_ID
}

ipfs_upload_http() {
    IPFS_FILE_ID=$(curl -F file=@$1 http://127.0.0.1:5001/api/v0/add | awk -F'[:,}]' '{gsub(/"/, "", $2); print $2}')
    echo "File ID is: ${IPFS_FILE_ID}"
}

ipfs_download_http() {
    curl "http://127.0.0.1:8080/ipfs/${IPFS_FILE_ID}" -o output
}