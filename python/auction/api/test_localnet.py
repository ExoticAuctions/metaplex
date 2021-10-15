from solana.account import Account
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.transaction import Transaction,TransactionInstruction,AccountMeta
from base58 import b58decode
import solana.system_program as sp
import json
import base64
import time
from spl.token.client import Token
import spl.token.instructions as spl_token
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID

import auction_api
import instruction

program_id=PublicKey("2rq6o4nzR8khsU6DLfXPix99JE9uMzGj8L1u9RgECzbS")
endpoint="http://localhost:8899"
client=Client(endpoint)
# secret_key=b58decode("2pUVo4mVSnebLyLmMTHgPRNbk7rgZki77bsYgbsuuQX9585N4aKNXWJRpyc98qnpgRKRH2hzB8VVnqeffurW39F4")
# payer=Keypair.from_secret_key(secret_key)

payer=Keypair()
client.request_airdrop(payer.public_key,int(3e9))
time.sleep(20)
client.request_airdrop(payer.public_key,int(3e9))
time.sleep(20)
client.request_airdrop(payer.public_key,int(3e9))
time.sleep(20)
print(client.get_balance(payer.public_key))

def setup_auction(
	max_winners : int,
	price_floor : int,
	gap_tick_size_percentage : int,
	tick_size : int,
	reward_size : int,
	):
	auction_creator = payer #Keypair()
	token_mint = Token.create_mint(
		client,
		payer, 
		payer.public_key,
		2,
		TOKEN_PROGRAM_ID,
		payer.public_key,
		)
	mint=token_mint.pubkey
	resource = Keypair().public_key
	auction_pubkey=PublicKey.find_program_address([b'auction',bytes(program_id),bytes(resource)],program_id)[0]
	auction_api.create_auction_v2(
		conn=client,
		program_id=program_id,
		payer=auction_creator,
		resource=resource,
		mint=mint,
		max_winners=max_winners,
		price_floor=price_floor,
		gap_tick_size_percentage=gap_tick_size_percentage,
		tick_size=tick_size,
		reward_size=reward_size
		)
	bidders=[]
	for i in range(5):
		bidder=Keypair()
		tx=Transaction().add(
			sp.transfer(sp.TransferParams(
				from_pubkey = payer.public_key,
				to_pubkey = bidder.public_key,
				lamports = int(5e8)
				)))
		client.send_transaction(tx,payer)
		bidder_token=token_mint.create_account(bidder.public_key)
		bid_pot_pubkey=PublicKey.find_program_address([b'auction',bytes(program_id),bytes(auction_pubkey),bytes(bidder.public_key)],program_id)[0]
		auction_spl_pot=token_mint.create_account(auction_pubkey)
		token_mint.mint_to(
			dest=bidder_token,
			mint_authority=payer,
			amount=1000,
			opts=TxOpts(skip_confirmation=False),
			)
		bidders.append((bidder,bidder_token,auction_spl_pot,bid_pot_pubkey))
	auction_api.start_auction(
		conn=client,
		program_id=program_id,
		authority=auction_creator,
		resource=resource
		)
	return bidders,resource,auction_creator,auction_pubkey,token_mint;

def show_bidders(bidders,token_mint):
	index=0
	for bidder in bidders:
		print("bidder ",index,"  :  ",token_mint.get_account_info(bidder[1]).amount," --- ",token_mint.get_account_info(bidder[2]).amount)
		index+=1

def get_winner(bidders,res_bidders):
	last_bidder=res_bidders[len(res_bidders)-1]
	for bidder in bidders:
		if bidder[0].public_key==PublicKey(last_bidder.bidder):
			return bidder

strategies = [
	{
		"actions":[
			(0,0,100),
			(0,1,110),
			(0,2,130),
			(0,3,180),
			(0,2,190),
			(0,1,220),
			(2,)
		],
		"max_winners" : 1,
		"price_floor" : 100,
		"tick_size" : 10,
		"gap_tick_size_percentage" : 0,
		"reward_size" : 4
	},
	{
		"actions":[
			(0,0,200),
			(0,1,250),
			(0,0,350),
			(0,3,400),
			(0,2,500),
			(2,)
		],
		"max_winners" : 1,
		"price_floor" : 200,
		"tick_size" : 50,
		"gap_tick_size_percentage" : 0,
		"reward_size" : 10
	},
]
index=0
for strategy in strategies:	
	index+=1
	print("Strategy ",index,": ")
	bidders,resource,auction_creator,auction_pubkey,token_mint=setup_auction(
		strategy["max_winners"],
		strategy["price_floor"],
		strategy["gap_tick_size_percentage"],
		strategy["tick_size"],
		strategy["reward_size"],
		)
	for action in strategy["actions"]:
		auction_extended=instruction.get_auction_v2_extended_data(
			conn=client,
			program_id=program_id,
			resource=resource
			)
		print(auction_extended)
		
		auction=instruction.get_auction_data(
			conn=client,
			program_id=program_id,
			resource=resource
			)
		print(auction.bid_state.bidders)


		if action[0]==0:
			print("PLACE BID : bidder",action[1],"  --  ",action[2])
			cur_bidder=bidders[action[1]]
			transfer_authority=Keypair()
			token_mint.approve(
				source=cur_bidder[1],
				delegate=transfer_authority.public_key,
				owner=cur_bidder[0].public_key,
				amount=action[2],
				multi_signers=[cur_bidder[0]],
				opts=TxOpts(skip_confirmation=False)
				)
			if len(auction.bid_state.bidders)==0:
				auction_api.place_bid(
					conn=client,
					program_id=program_id,
					payer=payer,
					bidder=cur_bidder[0],
					bidder_token=cur_bidder[1],
					bidder_pot_token=cur_bidder[2],
					transfer_authority=transfer_authority,
					resource=resource,
					mint=token_mint.pubkey,
					amount=action[2]
					)
			else:
				prev_bidder=auction.bid_state.bidders[0]
				auction_api.place_bid_v2(
					conn=client,
					program_id=program_id,
					payer=payer,
					bidder=cur_bidder[0],
					bidder_token=cur_bidder[1],
					bidder_pot_token=cur_bidder[2],
					transfer_authority=transfer_authority,
					resource=resource,
					mint=token_mint.pubkey,
					amount=action[2],
					prev_bidder=PublicKey(prev_bidder.bidder),
					prev_bidder_token=PublicKey(prev_bidder.bidder_token),
					prev_bidder_pot_token=PublicKey(prev_bidder.bidder_pot_token),
					)

		# elif action[0]==1:
		# 	cur_bidder=bidders[action[1]]
		# 	auction_api.cancel_bid(
		# 		conn=client,
		# 		program_id=program_id,
		# 		payer=payer,
		# 		bidder=cur_bidder[0],
		# 		bidder_token=cur_bidder[1],
		# 		bidder_pot_token=cur_bidder[2],
		# 		resource=resource,
		# 		mint=token_mint.pubkey
		# 		)
		else:
			auction_api.end_auction(
				conn=client,
				program_id=program_id,
				authority=auction_creator,
				resource=resource
				)
		show_bidders(bidders,token_mint)
		
	auction=instruction.get_auction_data(
			conn=client,
			program_id=program_id,
			resource=resource
			)
	destination=token_mint.create_account(auction_creator.public_key)
	winner=get_winner(bidders=bidders,res_bidders=auction.bid_state.bidders)
	print(winner)

	auction_api.claim_bid(
		conn=client,
		program_id=program_id,
		payer=payer,
		authority=auction_creator,
		bidder=winner[0].public_key,
		bidder_pot_token=winner[2],
		seller=destination,
		resource=resource,
		mint=token_mint.pubkey,
		)
	print(token_mint.get_balance(destination))
