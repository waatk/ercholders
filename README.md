# ercholders
Python script to take a snapshot of unique erc721 holders, and map all tokens to current owners, powered by etherscan.

The program will pull all transfer logs from etherscan, dynamically changing the number of blocks polled to stay within the 1000 logs per call limit, but go as fast as possible.  The owner of each token is updated with each transfer.

To use, add an etherscan api key (used to work with no key, but doesn't seem to anymore ... at least they're free), and change the NFT_CONTRACT_ADDRESS, MINT_BLOCK, and COLLECTION_SIZE parameters to match your desired collection.

Two .txt files are output, unique_holders.txt is a list of the unique holders adresses, and holders_map.txt is a csv file where each row contains the token number, and owner address.
