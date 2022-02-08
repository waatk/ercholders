#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: waatk
"""

import numpy as np
import requests
import time

#############################################################################
### API KEYS AND CONTRACTS
#############################################################################

ETHERSCAN_API_KEY = 'apply_for_a_free_one'
ETHERSCAN_COOLDOWN = 1.0 # seconds, works well for no key, 0.2 with free key

NFT_CONTRACT_ADDRESS = '0x343f999eaacdfa1f201fb8e43ebb35c99d9ae0c1' # lasc baby
MINT_BLOCK = 12837477
COLLECTION_SIZE = 10001

#############################################################################
### ETHERSCAN API FUNCTIONS
#############################################################################

transfer_topic = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

def getCurrentBlock():
    print('Getting current block from etherscan ...')
    payload = {'module':'block',
               'action':'getblockcountdown',
               'blockno':'99999999',
               'apikey':ETHERSCAN_API_KEY}
    r = requests.get('https://api.etherscan.io/api', params=payload)
    current_block = r.json()['result']['CurrentBlock']
    print('\t{}'.format(current_block))
    time.sleep(ETHERSCAN_COOLDOWN)
    return current_block

def getTransfers(from_block, to_block='latest'):
    #print('Checking for token transfers ...')
    payload = {'module':'logs',
               'action':'getLogs',
               'fromBlock':str(int(from_block)),
               'toBlock':str(int(to_block)),
               'address':NFT_CONTRACT_ADDRESS,
               'topic0':transfer_topic,
               'apikey':ETHERSCAN_API_KEY}
    r = requests.get('https://api.etherscan.io/api', params=payload)
    time.sleep(ETHERSCAN_COOLDOWN)
    return r.json()['result']

def mapHolders(transfers_log, holders_map):
    """ Update token owners for every transfer. """
    for transfer in transfers_log:
        t = Transfer(transfer)
        holders_map[int(t.tokenId)-1] = t.taker_clean
    return holders_map

class Transfer:
    """ Object to handle etherscan log data for an individual transfer. """
    def __init__(self, transfer, print=False):
        self.maker = transfer['topics'][1]
        self.taker = transfer['topics'][2]
        self.maker_clean = '0x'+self.maker[26:]
        self.taker_clean = '0x'+self.taker[26:]
        self.tokenId = str(int(transfer['topics'][3],16))
        self.block = str(int(transfer['blockNumber'],16))
        self.tx_hash = transfer['transactionHash'] 
        
        if print:
            self.printOut()
        
    def printOut(self):
        print('\tToken #{} TRANSFER detected at block {}'.format(
            self.tokenId, self.block))
        print('\t\tFrom:\t{}'.format(self.maker))
        print('\t\t  To:\t{}'.format(self.taker))   

#############################################################################
### RUN PROGRAM
#############################################################################        
        
if __name__ == '__main__':
    
    current_block = int(getCurrentBlock())
    starting_block = MINT_BLOCK
    increment = 1000
    
    holders_map = np.empty(COLLECTION_SIZE, dtype='<U64')
    
    while starting_block < current_block:
        print('Scanning from {} to {}, increment={}'.format(
            starting_block, starting_block+increment, increment))
        transfers_log = getTransfers(starting_block, starting_block+increment)
        if len(transfers_log) < 1000:
            holders_map = mapHolders(transfers_log, holders_map)
            starting_block = starting_block + increment
            increment = int(1.1*increment)
        else:
            print('\tWARNING: MAX TRANSFER LOGS EXCEEDED')
            increment = int(0.5*increment)
    
    f = open('holders_map.txt', 'w')
    for number, address in enumerate(holders_map):
        f.write('{}, {}\n'.format(number+1,address))
    f.close()  
    
    unique_holders = []
    for address in holders_map:
        if address not in unique_holders:
            unique_holders.append(address)
            
    f = open('unique_holders.txt', 'w')
    for address in unique_holders:
        f.write(address+'\n')
    f.close()          
